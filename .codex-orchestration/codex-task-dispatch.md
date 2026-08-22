---
task_id: 0014
title: 最終整合驗收
status: completed
executor: agy
current_plan: .codex-orchestration/plans/plan-0014.md
current_report: .codex-orchestration/reports/report-agy-0014.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序

1. `.codex-orchestration/codex-task-dispatch.md`
2. `.codex-orchestration/plans/plan-0014.md`
3. `.codex-orchestration/reports/report-agy-0009.md`
4. `.codex-orchestration/reports/report-agy-0010.md`
5. `.codex-orchestration/reports/report-agy-0011.md`
6. `.codex-orchestration/reports/report-agy-0012.md`
7. `.codex-orchestration/reports/report-agy-0013.md`
8. `app.py`、`utils.py`、`rag_engine.py`
9. 所有 `test_*.py`

## 規則

1. 此為不改碼最終驗收；只允許建立／更新 `.codex-orchestration/reports/report-agy-0014.md`。
2. 禁止修改任何 production code、測試、設定、提示詞、`docs/` 或資料庫；不得啟動 Streamlit、模型、網路或 ChromaDB。
3. 依序執行 `python -m py_compile app.py utils.py rag_engine.py`、`pytest -q`、`git diff --check`、`git status --short`。
4. 必須在自己的 `report-agy-0014.md` 如實逐字記錄必讀清單、所有命令輸出與離退碼、未改動範圍，以及計畫檔中的人工 Windows UI 驗收清單；不得使用「略」或省略號代替輸出。
5. 完成後停止，等待 Codex 最終結案。

## Codex 最終結案結果

- 0010～0013 的來源信任、RAG 邊界與通用 fallback 已完成並驗收。
- 0014 驗證通過：`python -m py_compile app.py utils.py rag_engine.py` 離退碼 0；`pytest -q` 為 **34 passed**；`git diff --check` 離退碼 0。
- 人工 Windows UI 驗收清單已交付於 `.codex-orchestration/reports/report-agy-0014.md`。
- 本工作流結案。
