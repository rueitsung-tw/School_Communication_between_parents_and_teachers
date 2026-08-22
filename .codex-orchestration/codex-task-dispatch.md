---
task_id: 0013
title: 00 通用主題安全 fallback
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0013.md
current_report: .codex-orchestration/reports/report-agy-0013.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序

1. `.codex-orchestration/codex-task-dispatch.md`
2. `.codex-orchestration/plans/plan-0013.md`
3. `.codex-orchestration/reports/report-agy-0009.md`
4. `.codex-orchestration/reports/report-agy-0012.md`
5. `app.py`
6. `test_app_ui_wording.py`
7. `test_safety_contract.py`

## 規則

1. 只執行 0013；0014 尚未獲執行授權。
2. 先 RED、後 GREEN。
3. 只可修改 `app.py`、`test_app_ui_wording.py`、`.codex-orchestration/reports/report-agy-0013.md`。
4. 禁止修改其他檔案，禁止模型、網路、ChromaDB 與 Streamlit。
5. 完成後必須如實寫入自己的 `report-agy-0013.md`：必讀清單、RED/GREEN、每項實際測試／git 輸出、修改與未修改範圍；不得使用「略」省略輸出。停止等待 Codex 審查。
