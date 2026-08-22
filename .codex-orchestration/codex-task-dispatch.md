---
task_id: 0006
title: 同步介面中的 NVC 四步驟說明
status: completed
executor: agy
current_plan: .codex-orchestration/plans/plan-0006.md
current_report: .codex-orchestration/reports/report-agy-0006.md
execution_allowed: true
---

# 單線任務派工單

1. 先讀本派工單。
2. 再讀 `current_plan` 指向的計畫檔。
3. 僅執行計畫中的唯一工作。
4. 將結果寫入 `current_report` 指向的報告檔。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許讀取：`app.py`、README.md、`prompts/`、既有測試及任務 0005 報告。
- 允許新增／修改：僅 `app.py`、一份針對 NVC 介面文案的測試檔，以及 `.codex-orchestration/reports/report-agy-0006.md`。
- 禁止：修改 `utils.py`、RAG、模型呼叫／prompt 組裝邏輯、README、`prompts/`、taxonomy、research、docs、依賴與設定；呼叫模型；建立平行任務。

## 完成條件

- `app.py` 不再含「三段式」或「同理 -> 事實 -> 解方」這類舊 NVC 架構說明。
- 相關 UI 文案明確說明「觀察、感受、需要、請求」僅為內部思維，對家長呈現為自然段落。
- 新測試先 RED 後 GREEN，且 `pytest -q`、`git diff --check` 均通過。

## Codex 驗收

任務 0006 已通過驗收：四處介面文案已與 NVC 四步驟內化、自然段落規範一致；回歸測試與全套 14 項測試均通過，`git diff --check` 離退碼為 0。
