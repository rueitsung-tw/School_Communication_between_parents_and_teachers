---
task_id: 0005
title: 將 NVC 四步驟落實至所有 Type B 回覆模組
status: rework_required
executor: agy
current_plan: .codex-orchestration/plans/plan-0005.md
current_report: .codex-orchestration/reports/report-agy-0005.md
execution_allowed: true
---

# 單線任務派工單

1. 先讀本派工單。
2. 再讀 `current_plan` 指向的計畫檔。
3. 僅執行計畫中的唯一工作。
4. 將結果寫入 `current_report` 指向的報告檔。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許讀取：README.md、`prompts/`、`utils.py`、任務 0004 報告。
- 允許新增／修改：僅 README.md、`prompts/*.md` 與 `.codex-orchestration/reports/report-agy-0005.md`。
- 禁止：修改 Python、測試、taxonomy、research、docs、RAG 索引與設定；下載或匯入外部文件；呼叫模型；建立平行任務。

## 完成條件

- README 與全部 11 個 Type B 模組一致地採 NVC 四步驟。
- 對家長的成稿仍是自然段落，沒有強制輸出「觀察／感受／需要／請求」標題或條列。
- 不得以未確認資訊、教師未提供的事實、過度承諾或責任承認填補任一步驟。
- `pytest -q`、`git diff --check` 均通過。

## Codex 複審：小範圍補正後再驗收

本次不開啟新任務，僅允許在原任務範圍內補正下列三點：

1. `prompts/00_通用_TypeB_回覆草稿生成器.md` 的用途摘要仍寫「符合三段式結構」；改為與 NVC 四步驟內化、自然段落呈現一致的表述。
2. `prompts/07_校園安全與意外事故.md` 的 Type B「感受」步驟將家長的「自責」當作既定情緒；改為僅同理訊息可合理辨識的擔心／心疼，或明示不得推定家長心理狀態。
3. `report-agy-0005.md` 的標題「回覆模组」改為繁體「回覆模組」，並補記以上兩項修正與重新驗證結果。

不得修改其他檔案。完成後執行 `pytest -q` 與 `git diff --check`，更新報告後停止，等待 Codex 再審。
