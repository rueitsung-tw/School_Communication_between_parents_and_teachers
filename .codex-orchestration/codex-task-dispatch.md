---
task_id: 0008
title: 修正 Type B 範例中的未確認事實與處置敘述
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0008.md
current_report: .codex-orchestration/reports/report-agy-0008.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單：`.codex-orchestration/codex-task-dispatch.md`
2. 計畫檔：`.codex-orchestration/plans/plan-0008.md`
3. 計畫檔「必讀檔案與順序」列出的 `utils.py`、`README.md`、11 份 `prompts/*.md` 與任務 0004、0007 報告。
4. 完整讀畢並完成報告中的勾列後，才可修改檔案。

## 執行規則

1. 僅執行計畫中的唯一工作。
2. 僅在 `status: approved` 時執行；本任務已獲准執行。
3. 完成後將結果寫入：`.codex-orchestration/reports/report-agy-0008.md`。
4. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許新增／修改：僅 `prompts/00_通用_TypeB_回覆草稿生成器.md`、`prompts/01_座位安排與班級經營.md` 至 `prompts/10_LINE群組溝通禮儀與界線.md` 的 Type B 使用範例，以及 `.codex-orchestration/reports/report-agy-0008.md`。
- 禁止修改：Type A、Type B 規範、README、Python、測試、RAG、法律／安全核心、taxonomy、research、docs、依賴與設定；不得呼叫模型、網路或建立平行任務。

## 完成條件

- 全部 11 份 Type B 範例只陳述範例輸入或教師補充背景支持的事實。
- 未確認資訊一律改為條件式查證／後續說明，不杜撰行動、他人說法、責任、處分或保證。
- 每份範例仍保留本主題理論與地雷句，並維持 2 至 3 段自然段落。
- `pytest -q` 與 `git diff --check` 均通過。
