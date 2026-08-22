---
task_id: 0004
title: 所有主題共用的事實與高風險安全核心
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0004.md
current_report: .codex-orchestration/reports/report-agy-0004.md
execution_allowed: true
---

# 單線任務派工單

## 執行順序（不可變更）

1. 先讀本派工單。
2. 再讀 `current_plan` 指向的計畫檔。
3. 僅執行計畫中定義的唯一工作。
4. 將結果寫入 `current_report` 指向的報告檔。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許讀取：`app.py`、`utils.py`、`test_prompts_loader.py`、`research_D_legal.md`、`theme_taxonomy.md`、`prompts/`、任務 0001 至 0003 報告。
- 允許新增／修改：僅 `utils.py`、`app.py`、`test_safety_contract.py` 與 `.codex-orchestration/reports/report-agy-0004.md`。
- 禁止：修改提示詞 Markdown、README、taxonomy、docs、RAG 索引、設定檔、既有測試檔；下載或匯入外部文件；呼叫模型；建立平行任務。

## 完成條件

- 每個 Type A／Type B 呼叫都經由同一個可測試的 prompt 組裝函式。
- 安全核心在主題提示詞與 RAG 內容之前，且任何主題均不可略過。
- 新測試先失敗後通過；全套 `pytest -q` 與 `git diff --check` 均通過。
