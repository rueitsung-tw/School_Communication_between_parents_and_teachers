---
task_id: 0009
title: RAG 來源信任模型設計與影響盤點
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0009.md
current_report: .codex-orchestration/reports/report-agy-0009.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單：`.codex-orchestration/codex-task-dispatch.md`
2. 計畫檔：`.codex-orchestration/plans/plan-0009.md`
3. 計畫檔「必讀檔案與順序」列出的 README、RAG 實作、上傳工具、設定、測試與任務 0004、0007、0008 報告。
4. 完整讀畢並在報告勾列後，才可進行設計盤點。

## 執行規則

1. 僅執行計畫中的唯一工作。
2. 僅在 `status: approved` 時執行；本任務已獲准執行。
3. 僅能新增／修改：`.codex-orchestration/reports/report-agy-0009.md`。
4. 禁止修改：`app.py`、`rag_engine.py`、`utils.py`、`ingest_pipeline.py`、README、測試、設定、`docs/`、`.chromadb/`、提示詞與任何其他檔案；不得呼叫模型、網路或建立平行任務。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 完成條件

- 報告完整勾列 16 份必讀檔案。
- 提出三類來源的最小 metadata、資料流、LLM 使用邊界、向後相容與分階段實作方案。
- 說明教師內容不屬 11 個主題時的通用提示詞 fallback、教師告知與安全失敗規則。
- 精確列出日後實作會觸及的檔名與函式，不憑空宣稱現有 metadata。
- `git diff --check` 通過，且工作樹除報告外無本任務新增修改。
