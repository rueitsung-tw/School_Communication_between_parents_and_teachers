---
task_id: 0012
title: RAG 信任標示與提示詞邊界
status: rework_required
executor: agy
current_plan: .codex-orchestration/plans/plan-0012.md
current_report: .codex-orchestration/reports/report-agy-0012.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單：`.codex-orchestration/codex-task-dispatch.md`
2. 實作計畫：`.codex-orchestration/plans/plan-0012.md`
3. 設計依據：`.codex-orchestration/reports/report-agy-0009.md`
4. 前階段報告：`.codex-orchestration/reports/report-agy-0011.md`
5. 共用工具與安全核心：`utils.py`
6. RAG context UI：`app.py`
7. 既有安全測試：`test_safety_contract.py`
8. 既有 UI 測試：`test_app_ui_wording.py`
9. 完整讀畢後，才可撰寫 RED 測試。

## 執行規則

1. 僅執行 `plan-0012.md` 的 Task 1；不得修改來源登記、manifest、RAG 索引、上傳 UI、提示詞檔、主題 fallback 或設定。
2. 必須先 RED、後 GREEN；不得在看到失敗測試前修改 production code。
3. 只允許修改：`utils.py`、`app.py`、`test_safety_contract.py`、`test_app_ui_wording.py`、`.codex-orchestration/reports/report-agy-0012.md`。
4. 禁止修改：`rag_engine.py`、`ingest_pipeline.py`、README、提示詞、設定、`.gitignore`、`docs/`、`.chromadb/`、其他測試及任何其他檔案；不得呼叫模型、網路、ChromaDB 或啟動 Streamlit。
5. 完成報告後停止，等待 Codex 審查；不得自行啟動 0013。

## 完成條件

- `official`、`teacher_case`、`external_unverified` 與未知／舊 metadata 都有固定、可讀、不可誤解的信任標示；驗證狀態由 `verified_status` 決定。
- RAG context 的每一段包含信任摘要與 Trust Badge；兩處教師檢視清單也顯示信任摘要。
- `SAFETY_CORE` 明確禁止把教師經驗當成本案已知事實，或把外部未核定資料直接引用為法令／校規，且仍優先於 RAG context。
- 專屬與全套 pytest 均通過，`git diff --check` 離退碼為 0。

## Codex 報告補正（不得改程式）

1. 只讀取本派工單與 `.codex-orchestration/reports/report-agy-0012.md`。
2. 不得修改 `utils.py`、`app.py`、測試或任何其他檔案；只可修改 `report-agy-0012.md`。
3. 重新執行 `pytest -q`、`git diff --check`、`git status --short`；將全套測試結果由錯誤的 `32 passed` 更正為當前實際輸出，並如實記錄當前 status。
4. 完成後停止，等待 Codex 最終驗收。
