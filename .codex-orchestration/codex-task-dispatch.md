---
task_id: 0007
title: 建立 Type B 草稿格式品質關卡
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0007.md
current_report: .codex-orchestration/reports/report-agy-0007.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單 `.codex-orchestration/codex-task-dispatch.md`。
2. 計畫 `.codex-orchestration/plans/plan-0007.md`。
3. 計畫「必讀檔案與順序」列出的 `utils.py`、`app.py`、兩份測試及任務 0004 至 0006 報告。
4. 確認全部讀畢後，才可開始 TDD RED 階段。

## 執行規則

1. 僅執行計畫中的唯一工作。
2. 僅在 `status: approved` 時執行；本任務已獲准執行。
3. 將結果寫入 `current_report` 指向的報告檔。
4. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許新增／修改：僅 `utils.py`、`app.py`、`test_response_contract.py`、`.codex-orchestration/reports/report-agy-0007.md`。
- 禁止修改：README、`prompts/`、現有測試、RAG、模型呼叫流程、法律／安全核心內容、taxonomy、research、docs、依賴與設定；不得呼叫模型、網路或建立平行任務。

## 完成條件

- `utils.validate_parent_reply` 以純函式檢查：空白、段落數、可見 NVC 標題與條列／編號。
- Type B 草稿未通過時不會顯示原草稿或成功訊息，只提示重新生成；通過時保留現有顯示行為。
- 新測試先 RED 後 GREEN，`pytest -q` 與 `git diff --check` 均通過。
