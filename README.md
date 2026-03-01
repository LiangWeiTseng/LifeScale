# LifeScale — 人生重要決定天秤

![version](https://img.shields.io/badge/version-1.0.0-blue)
![python](https://img.shields.io/badge/python-3.8%2B-green)
![streamlit](https://img.shields.io/badge/streamlit-1.x-red)

> A Streamlit app for weighing life's important decisions through structured pros & cons analysis.
> 用結構化的方式量化人生重要決策，透過 Pro/Con 因子評分找出最佳選擇。

---

## Features 功能特色

| English | 中文 |
|---------|------|
| Customizable decision title | 可自訂決策標題 |
| Add / edit / delete factors | 新增、編輯、刪除因子 |
| Preset & custom categories | 預設分類 + 自行輸入 |
| Sort by category or score | 依分類或分數排序 |
| Interactive pie chart | 互動式圓餅圖 |
| Summary metrics (Pro / Con / Net) | 摘要指標卡片 |
| Auto-save to local JSON | 自動儲存至本地 JSON |
| Export CSV & HTML report | 匯出 CSV 及 HTML 彙整報告 |
| Import CSV (overwrite or append) | 匯入 CSV（覆蓋或附加） |
| Reset / clear all factors | 一鍵清除所有因子 |
| Built-in help instructions | 內建使用說明（❕ 展開） |

---

## Setup 環境安裝

```bash
pip install streamlit pandas plotly
```

---

## Run 啟動

```bash
streamlit run decision_app.py
```

瀏覽器會自動開啟，資料自動儲存於 `decision_data.json`（同目錄）。
The browser will open automatically. Data is auto-saved to `decision_data.json` in the same folder.

---

## Usage 使用方式

1. **Set title** — Edit the decision name at the top; press Enter to apply.
   **設定標題** — 在頁面頂端修改決策名稱，按 Enter 套用。

2. **Add factors** — Choose a category, write a description (optional), select Pro or Con, and rate importance 1–10.
   **新增因子** — 選擇分類、填入描述（選填）、選擇 Pro/Con、設定重要程度 1–10。

3. **Edit / Delete** — Click ✏️ or 🗑️ on any row in the factor table.
   **編輯 / 刪除** — 在因子清單中點擊 ✏️ 或 🗑️。

4. **Sort** — Use the dropdown above the table to sort by category or score.
   **排序** — 使用清單右上角的下拉選單依分類或分數排列。

5. **Review** — Check the summary metrics and pie chart to see the overall balance.
   **查看結果** — 透過摘要指標與圓餅圖掌握整體傾向。

6. **Export** — Download a CSV or a full HTML report with embedded charts.
   **匯出** — 下載 CSV 資料或含圖表的完整 HTML 報告。

7. **Import CSV** — Expand the "📥 匯入 CSV" section and upload a file with columns `category`, `side`, `score`.
   **匯入 CSV** — 展開「📥 匯入 CSV」，上傳含必要欄位的 CSV 檔。

8. **Reset** — "🗑️ 清除所有因子" removes all factors. Export a backup first if needed.
   **重置** — 「🗑️ 清除所有因子」清空所有因子，操作前可先匯出備份。

9. **Help** — Click the ❕ expander below the title input for in-app instructions.
   **使用說明** — 點擊標題輸入框下方的 ❕ 展開內建說明。

---

## File Structure 檔案結構

```
phd決定/
├── decision_app.py      # Main Streamlit app 主程式
├── decision_data.json   # Auto-saved data 自動儲存資料（執行後產生）
└── README.md
```

---

*LifeScale — measure what matters.*
