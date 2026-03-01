import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import json, os


def generate_report_html(title, factors, pro_total, con_total, net, verdict_text):
    today = date.today().strftime("%Y 年 %m 月 %d 日")
    df = pd.DataFrame(factors)

    # ── charts ──────────────────────────────────────────────────
    pie_df = df.groupby('side')['score'].sum().reset_index()
    fig_pie = px.pie(pie_df, values='score', names='side',
                     color='side', hole=0.4,
                     color_discrete_map={'Pro': '#27ae60', 'Con': '#e74c3c'},
                     title="Pro vs Con 分數比例")
    fig_pie.update_traces(textinfo='percent+value', textfont_size=15,
                          textposition='inside')
    fig_pie.update_layout(font=dict(size=14), height=380,
                          margin=dict(t=60, b=20, l=20, r=20))

    net_df = df.copy()
    net_df['signed'] = net_df.apply(lambda r: r['score'] if r['side'] == 'Pro' else -r['score'], axis=1)
    net_totals = net_df.groupby('category')['signed'].sum().reset_index().sort_values('signed')
    net_totals['label'] = net_totals['signed'].apply(lambda v: f"+{v}" if v > 0 else str(v))
    bar_colors = net_totals['signed'].apply(
        lambda v: '#27ae60' if v > 0 else ('#e74c3c' if v < 0 else '#888888')).tolist()
    fig_net = go.Figure(go.Bar(
        x=net_totals['signed'], y=net_totals['category'],
        orientation='h', text=net_totals['label'],
        textposition='outside', textfont=dict(size=14),
        marker_color=bar_colors))
    fig_net.add_vline(x=0, line_dash="dash", line_color="#888")
    fig_net.update_layout(
        title="各分類淨分（Pro − Con）", font=dict(size=14), showlegend=False,
        xaxis_title='淨分數', yaxis_title='分類',
        height=max(320, len(net_totals) * 55 + 100),
        margin=dict(t=60, b=20, r=100))

    pie_html = fig_pie.to_html(full_html=False, include_plotlyjs=False)
    net_html = fig_net.to_html(full_html=False, include_plotlyjs=False)

    # ── factor table rows ────────────────────────────────────────
    rows_html = ""
    for _, r in df.iterrows():
        color = "#27ae60" if r['side'] == "Pro" else "#e74c3c"
        desc = r['description'] if r['description'] else "—"
        rows_html += f"""
        <tr>
          <td>{r['category']}</td>
          <td>{desc}</td>
          <td style="color:{color};font-weight:600">{r['side']}</td>
          <td style="text-align:center">{r['score']}</td>
        </tr>"""

    verdict_color = "#27ae60" if net > 0 else ("#e74c3c" if net < 0 else "#888")

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>{title} — 決策報告</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body {{ font-family: "Helvetica Neue", Arial, sans-serif; color: #222;
          max-width: 960px; margin: 40px auto; padding: 0 24px; line-height: 1.7; }}
  h1   {{ color: #1f4e79; border-bottom: 3px solid #1f4e79; padding-bottom: 10px; }}
  h2   {{ color: #2c3e50; margin-top: 2rem; }}
  .meta {{ color: #888; font-size: 0.95rem; margin-bottom: 2rem; }}
  .metrics {{ display: flex; gap: 16px; margin: 1.5rem 0; }}
  .card {{ flex: 1; background: #f4f7fb; border-radius: 12px; padding: 18px 20px; text-align: center; }}
  .card .val {{ font-size: 2rem; font-weight: 700; margin: 4px 0; }}
  .card .lbl {{ font-size: 0.9rem; color: #666; }}
  .verdict {{ font-size: 1.5rem; font-weight: 700; color: {verdict_color};
               background: #f9f9f9; border-left: 5px solid {verdict_color};
               padding: 14px 20px; border-radius: 8px; margin: 1rem 0 2rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.97rem; }}
  th    {{ background: #1f4e79; color: white; padding: 10px 14px; text-align: left; }}
  td    {{ padding: 9px 14px; border-bottom: 1px solid #eee; }}
  tr:hover td {{ background: #f7faff; }}
  .charts {{ display: block; margin-top: 1rem; }}
  .chart-box {{ width: 100%; margin-bottom: 1.5rem; }}
  footer {{ margin-top: 3rem; color: #aaa; font-size: 0.85rem; border-top: 1px solid #eee; padding-top: 1rem; }}
</style>
</head>
<body>
<h1>⚖️ {title}</h1>
<p class="meta">產生日期：{today} &nbsp;｜&nbsp; 因子總數：{len(df)} 筆</p>

<h2>摘要指標</h2>
<div class="metrics">
  <div class="card"><div class="lbl">因子總數</div><div class="val">{len(df)}</div></div>
  <div class="card"><div class="lbl">✅ Pro 總分</div><div class="val" style="color:#27ae60">{pro_total}</div></div>
  <div class="card"><div class="lbl">❌ Con 總分</div><div class="val" style="color:#e74c3c">{con_total}</div></div>
  <div class="card"><div class="lbl">⚖️ 淨分數</div><div class="val" style="color:{verdict_color}">{net:+d}</div></div>
</div>

<div class="verdict">綜合結論：{verdict_text}</div>

<h2>因子清單</h2>
<table>
  <tr><th>分類</th><th>描述</th><th>方向</th><th>分數</th></tr>
  {rows_html}
</table>

<h2>視覺化圖表</h2>
<div class="charts">
  <div class="chart-box">{pie_html}</div>
  <div class="chart-box">{net_html}</div>
</div>

<footer>由 Decision Factor Analyzer 自動產生</footer>
</body>
</html>"""
    return html


st.set_page_config(page_title="人生重要決定天秤", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 18px; }
    [data-testid="collapsedControl"] { display: none; }
    header[data-testid="stHeader"]   { display: none; }

    /* ── 大標題 ── */
    .big-title { font-size: 10rem; font-weight: 400; color: #e8f0fe;
                 line-height: 1.05; margin-bottom: 0.1rem;
                 text-shadow: 0 2px 12px rgba(0,0,0,0.35); }
    .sub-header { color: #b0bec5; font-size: 1.1rem; margin-bottom: 0.8rem; }

    /* ── 內文 ── */
    p, li, [data-testid="stText"] { font-size: 1.1rem !important; }
    h2, h3 { font-size: 1.45rem !important; font-weight: 700; }
    .col-head { font-weight: 700; color: #444; font-size: 1rem;
                text-transform: uppercase; letter-spacing: 0.05em; }
    label { font-size: 1rem !important; }

    /* ── Metric ── */
    [data-testid="metric-container"] { background:#f4f7fb; border-radius:14px; padding:1rem 1.2rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:2.4rem !important; font-weight:800; }
    [data-testid="metric-container"] [data-testid="stMetricLabel"] { font-size:1.05rem !important; color:#555; }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size:1rem !important; }

    /* ── Expander ── */
    details summary p { font-size: 1.1rem !important; font-weight: 600; }
    [data-testid="stAlert"] p { font-size: 1.05rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Persistence (JSON auto-save) ───────────────────────────────
_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decision_data.json")

def _load():
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save():
    with open(_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'title': st.session_state.title,
                   'factors': st.session_state.factors}, f,
                  ensure_ascii=False, indent=2)

# ── Session state ──────────────────────────────────────────────
if 'loaded' not in st.session_state:
    _d = _load()
    st.session_state.factors    = _d.get('factors', [])
    st.session_state.title      = _d.get('title', '人生重要決定')
    st.session_state.editing_idx = None
    st.session_state.sort_by    = "輸入順序"
    st.session_state.loaded     = True

# ── Header ─────────────────────────────────────────────────────
st.markdown(f'<p class="big-title">⚖️ {st.session_state.title}</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">系統化評估你的決策，量化每個影響因子</p>', unsafe_allow_html=True)

# 標題修改輸入框
new_title = st.text_input("修改標題", value=st.session_state.title,
                           label_visibility="collapsed")
st.caption("✏️ 修改後按 Enter 即套用")
if new_title.strip() and new_title.strip() != st.session_state.title:
    st.session_state.title = new_title.strip()
    _save()
    st.rerun()

with st.expander("❕ 使用說明"):
    st.markdown("""
**1. 修改標題**　在上方輸入框修改決策名稱，按 Enter 即套用。

**2. 新增因子**　在「➕ 新增因子」表單中：
- 選擇分類（或選「＋ 自行輸入」填入自訂分類）
- 描述為選填，可簡短說明此因子
- 選擇方向：**Pro**（支持）或 **Con**（反對）
- 拖曳滑桿設定重要程度（1–10）
- 按「➕ 新增」完成

**3. 編輯 / 刪除**　在因子清單每一列點擊 ✏️ 進入編輯模式，或 🗑️ 直接刪除。

**4. 排序**　清單右上角的下拉選單可依「輸入順序」、「依分類」、「依分數↓↑」排列。

**5. 圓餅圖**　即時顯示 Pro vs Con 分數比例，拖曳或縮放可互動檢視。

**6. 匯出**
- ⬇️ **匯出 CSV**：下載因子資料，可用 Excel 開啟
- 📄 **產生彙整報告**：下載獨立 HTML 報告，含圖表與摘要

**7. 匯入 CSV**　展開底部「📥 匯入 CSV」區塊，上傳含 `category`、`side`、`score` 欄位的 CSV 檔；可選擇「覆蓋載入」或「附加載入」。

**8. 重置**　按「🗑️ 清除所有因子」將刪除目前所有因子，操作前請確認或先匯出備份。

**9. 自動儲存**　所有變更即時寫入 `decision_data.json`，重新整理頁面資料不會遺失。
""")

st.markdown("---")

# ── Preset categories ──────────────────────────────────────────
PRESET_CATS = ["家庭", "經濟", "未來發展性", "研究興趣", "職涯發展", "地點", "時間成本", "＋ 自行輸入"]

# ── Add / Edit form ────────────────────────────────────────────
is_editing = st.session_state.editing_idx is not None
if is_editing:
    f = st.session_state.factors[st.session_state.editing_idx]
    default_cat, default_desc = f['category'], f['description']
    default_side, default_score = f['side'], f['score']
    form_label = f"✏️ 編輯因子（第 {st.session_state.editing_idx + 1} 筆）"
else:
    default_cat, default_desc, default_side, default_score = "", "", "Pro", 5
    form_label = "➕ 新增因子"

_preset_names = [c for c in PRESET_CATS if c != "＋ 自行輸入"]
if default_cat in _preset_names:    _cat_sel = default_cat
elif default_cat == "":             _cat_sel = PRESET_CATS[0]
else:                               _cat_sel = "＋ 自行輸入"

with st.expander(form_label, expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        cat_choice = st.selectbox("分類", PRESET_CATS,
                                  index=PRESET_CATS.index(_cat_sel),
                                  help="選預設分類，或選「＋ 自行輸入」")
        if cat_choice == "＋ 自行輸入":
            inp_cat = st.text_input("自訂分類",
                                    value=default_cat if default_cat not in _preset_names else "",
                                    placeholder="例如：心理健康")
        else:
            inp_cat = cat_choice
        inp_desc = st.text_input("描述（選填）", value=default_desc,
                                 placeholder="簡短說明此因子（可留空）")
    with col_b:
        inp_side  = st.radio("方向", ["Pro", "Con"],
                             index=0 if default_side == "Pro" else 1, horizontal=True)
        inp_score = st.slider("重要程度 (1–10)", 1, 10, default_score)

    b1, b2, _ = st.columns([1.2, 1.2, 5])
    with b1:
        if st.button("💾 儲存修改" if is_editing else "➕ 新增",
                     type="primary", use_container_width=True):
            if inp_cat:
                entry = {'category': inp_cat, 'description': inp_desc,
                         'side': inp_side, 'score': inp_score}
                if is_editing:
                    st.session_state.factors[st.session_state.editing_idx] = entry
                    st.session_state.editing_idx = None
                else:
                    st.session_state.factors.append(entry)
                _save()
                st.rerun()
            else:
                st.warning("請選擇或輸入分類")
    with b2:
        if is_editing and st.button("❌ 取消", use_container_width=True):
            st.session_state.editing_idx = None
            st.rerun()

st.markdown("---")

# ── Main content ───────────────────────────────────────────────
if not st.session_state.factors:
    st.info("👆 使用上方表單新增因子，即可開始分析。")
    with st.expander("📖 載入範例資料"):
        if st.button("載入範例"):
            st.session_state.factors = [
                {"category": "研究興趣", "description": "對研究主題充滿熱情",     "side": "Pro", "score": 9},
                {"category": "職涯發展", "description": "契合學術職涯規劃",       "side": "Pro", "score": 7},
                {"category": "經濟",     "description": "獎學金足以支付生活",     "side": "Pro", "score": 6},
                {"category": "經濟",     "description": "與業界薪資的機會成本差距","side": "Con", "score": 8},
                {"category": "家庭",     "description": "長期與家人分隔",         "side": "Con", "score": 7},
                {"category": "研究興趣", "description": "良好的師生關係",         "side": "Pro", "score": 8},
                {"category": "時間成本", "description": "需要 4–5 年完成",        "side": "Con", "score": 6},
            ]
            _save()
            st.rerun()

else:
    df_all = pd.DataFrame(st.session_state.factors)

    # ── Metrics ────────────────────────────────────────────────
    pro_total = int(df_all[df_all.side == "Pro"]["score"].sum())
    con_total = int(df_all[df_all.side == "Con"]["score"].sum())
    net = pro_total - con_total
    verdict = "✅ 偏向 Pro" if net > 0 else ("❌ 偏向 Con" if net < 0 else "⚖️ 中立")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📋 因子總數", len(df_all))
    m2.metric("✅ Pro 總分", pro_total)
    m3.metric("❌ Con 總分", con_total)
    m4.metric("⚖️ 淨分數", f"{net:+d}", delta=verdict, delta_color="off")

    st.markdown("---")

    # ── Factor table ───────────────────────────────────────────
    tbl_hd, tbl_sort = st.columns([3, 1])
    tbl_hd.subheader("📋 因子清單")
    sort_by = tbl_sort.selectbox("排序", ["輸入順序", "依分類", "依分數↓", "依分數↑"],
                                  label_visibility="collapsed")

    factors_view = list(st.session_state.factors)
    if sort_by == "依分類":
        factors_view = sorted(factors_view, key=lambda r: r['category'])
    elif sort_by == "依分數↓":
        factors_view = sorted(factors_view, key=lambda r: r['score'], reverse=True)
    elif sort_by == "依分數↑":
        factors_view = sorted(factors_view, key=lambda r: r['score'])

    hcols = st.columns([2.2, 4, 1.5, 1.2, 0.9, 0.9])
    for hc, lb in zip(hcols, ["分類", "描述", "方向", "分數", "編輯", "刪除"]):
        hc.markdown(f'<span class="col-head">{lb}</span>', unsafe_allow_html=True)

    to_delete = None
    for view_i, row in enumerate(factors_view):
        real_i = st.session_state.factors.index(row)
        rc = st.columns([2.2, 4, 1.5, 1.2, 0.9, 0.9])
        rc[0].write(row['category'])
        rc[1].write(row['description'] or "—")
        rc[2].write("🟢 Pro" if row['side'] == "Pro" else "🔴 Con")
        rc[3].write(str(row['score']))
        if rc[4].button("✏️", key=f"edit_{view_i}", help="編輯"):
            st.session_state.editing_idx = real_i
            st.rerun()
        if rc[5].button("🗑️", key=f"del_{view_i}", help="刪除"):
            to_delete = real_i

    if to_delete is not None:
        st.session_state.factors.pop(to_delete)
        if st.session_state.editing_idx == to_delete:
            st.session_state.editing_idx = None
        _save()
        st.rerun()

    st.markdown("---")

    # ── Pie chart ──────────────────────────────────────────────
    st.subheader("📊 視覺化分析")
    _font = dict(family="Arial, sans-serif", size=17, color="#222")
    _tfont = dict(size=22, color="#1f4e79", family="Arial, sans-serif")

    pie_df = df_all.groupby('side')['score'].sum().reset_index()
    fig_pie = px.pie(pie_df, values='score', names='side', hole=0.45,
                     color='side',
                     color_discrete_map={'Pro': '#27ae60', 'Con': '#e74c3c'},
                     title="Pro vs Con 分數比例")
    fig_pie.update_traces(textinfo='label+percent+value',
                          textfont=dict(size=18, family="Arial"),
                          pull=[0.05, 0.05])
    fig_pie.update_layout(font=_font, title_font=_tfont, title_x=0.5,
                          legend=dict(font=dict(size=16)),
                          margin=dict(t=80, b=30, l=40, r=40), height=420)
    _, pie_col, _ = st.columns([1, 2, 1])
    with pie_col:
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # ── Export & Report ────────────────────────────────────────
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        st.download_button("⬇️ 匯出 CSV",
                           df_all.to_csv(index=False, encoding='utf-8-sig'),
                           "decision_factors.csv", "text/csv",
                           use_container_width=True)
    with exp_col2:
        report_html = generate_report_html(st.session_state.title,
                                           st.session_state.factors,
                                           pro_total, con_total, net, verdict)
        st.download_button("📄 產生彙整報告",
                           report_html.encode("utf-8"),
                           "decision_report.html", "text/html",
                           use_container_width=True)
    with exp_col3:
        if st.button("🗑️ 清除所有因子", use_container_width=True):
            st.session_state.factors = []
            st.session_state.editing_idx = None
            _save()
            st.rerun()

    # ── CSV Import ─────────────────────────────────────────────
    with st.expander("📥 匯入 CSV"):
        st.caption("需包含欄位：category、side、score（description 選填）")
        uploaded = st.file_uploader("CSV", type="csv", label_visibility="collapsed")
        if uploaded:
            try:
                imp_df = pd.read_csv(uploaded)
                if {'category','side','score'}.issubset(imp_df.columns):
                    if 'description' not in imp_df.columns:
                        imp_df['description'] = ""
                    imp_df['score'] = imp_df['score'].clip(1, 10).astype(int)
                    imp_df['side'] = imp_df['side'].where(imp_df['side'].isin(['Pro','Con']), 'Pro')
                    imp_df['description'] = imp_df['description'].fillna("")
                    records = imp_df[['category','description','side','score']].to_dict('records')
                    ic1, ic2 = st.columns(2)
                    with ic1:
                        if st.button("覆蓋載入", use_container_width=True):
                            st.session_state.factors = records
                            st.session_state.editing_idx = None
                            _save(); st.rerun()
                    with ic2:
                        if st.button("附加載入", use_container_width=True):
                            st.session_state.factors.extend(records)
                            _save(); st.rerun()
                    st.caption(f"偵測到 {len(records)} 筆因子")
                else:
                    st.error("CSV 需包含欄位：category、side、score")
            except Exception as e:
                st.error(f"讀取失敗：{e}")
