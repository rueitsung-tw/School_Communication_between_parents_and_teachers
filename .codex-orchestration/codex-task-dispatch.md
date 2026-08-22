---
task_id: 0010
title: RAG 來源信任核心：manifest 與 Chroma metadata
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0010.md
current_report: .codex-orchestration/reports/report-agy-0010.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單：`.codex-orchestration/codex-task-dispatch.md`
2. 實作計畫：`.codex-orchestration/plans/plan-0010.md`
3. 設計依據：`.codex-orchestration/reports/report-agy-0009.md`
4. 實作檔：`rag_engine.py`
5. 既有測試：`test_rag_engine.py`、`test_safety_contract.py`
6. 忽略規則：`.gitignore`
7. 完整讀畢後，才可撰寫 RED 測試。

## 執行規則

1. 僅執行 `plan-0010.md` 的 Task 1；不得自行開啟 UI、提示詞或 fallback 的下一階段。
2. 必須先 RED、後 GREEN；不得在看到失敗測試前修改 production code。
3. 允許新增／修改：`rag_engine.py`、`test_rag_engine.py`、`.gitignore`、`.codex-orchestration/reports/report-agy-0010.md`。
4. 禁止修改：`app.py`、`utils.py`、`ingest_pipeline.py`、README、提示詞、設定、`docs/`、`.chromadb/`、其他測試及任何其他檔案；不得呼叫模型、網路或建立平行任務。
5. 不得建立或提交實際 `docs/manifest.json`；測試只能在暫存目錄建立 manifest。
6. 寫完 `report-agy-0010.md` 後停止，等待 Codex 審查。

## 完成條件

- `RAGEngine.register_source_metadata()` 驗證並原子寫入以正規化絕對路徑為 key 的 manifest。
- `_index_file()` 與 `retrieve()` 均傳遞四個來源信任欄位；未登記與舊 metadata 都安全降級。
- `docs/manifest.json` 已列入 `.gitignore`。
- 專屬與全套 pytest 均通過，`git diff --check` 離退碼為 0。
