---
task_id: 0011
title: 管理端新增來源分級登記
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0011.md
current_report: .codex-orchestration/reports/report-agy-0011.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單：`.codex-orchestration/codex-task-dispatch.md`
2. 實作計畫：`.codex-orchestration/plans/plan-0011.md`
3. 設計依據：`.codex-orchestration/reports/report-agy-0009.md`
4. 前階段報告：`.codex-orchestration/reports/report-agy-0010.md`
5. UI 實作：`app.py`
6. RAG 核心：`rag_engine.py`
7. 上傳工具：`utils.py`
8. 既有測試：`test_app_ui_wording.py`、`test_rag_engine.py`、`test_safety_contract.py`
9. 完整讀畢後，才可撰寫 RED 測試。

## 執行規則

1. 僅執行 `plan-0011.md` 的 Task 1；不可實作 Trust Badges、RAG prompt 邊界、`00_通用` fallback、UI 主題分類或資料庫遷移。
2. 必須先 RED、後 GREEN；不得在看到失敗測試前修改 production code。
3. 只允許修改：`app.py`、`rag_engine.py`、`test_app_ui_wording.py`、`test_rag_engine.py`、`.codex-orchestration/reports/report-agy-0011.md`。
4. 禁止修改：`utils.py`、`ingest_pipeline.py`、README、提示詞、設定、`.gitignore`、`docs/`、`.chromadb/`、其他測試及任何其他檔案；不得呼叫模型、網路或啟動 Streamlit。
5. 不得建立或提交實際 `docs/manifest.json`；測試只能在暫存目錄建立 manifest。
6. 完成報告後停止，等待 Codex 審查；不得自行啟動 0012。

## 完成條件

- 管理員的「上傳檔案」分頁可明確選擇 `official`、`teacher_case` 或 `external_unverified`；網址匯入固定登記為 `external_unverified` / `web_crawl` / `unverified`。
- 兩個成功寫檔路徑都必須在同步索引前成功呼叫 `rag.register_source_metadata()`；登記失敗則顯示錯誤且不得手動呼叫 `rag._sync_index()`。
- 成功登記會使該檔案的既有索引指紋失效，讓隨後同步能以最新 manifest metadata 重建 chunk；不可重新摘要或呼叫模型。
- 專屬與全套 pytest 均通過，`git diff --check` 離退碼為 0。
