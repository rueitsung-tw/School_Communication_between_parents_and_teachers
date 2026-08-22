---
task_id: 0001
title: 知識圖譜網路查核與更新建議
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0001.md
current_report: .codex-orchestration/reports/report-agy-0001.md
execution_allowed: true
---

# 單線任務派工單

## 執行順序（不可變更）

1. 先讀本派工單。
2. 再讀 `current_plan` 指向的計畫檔。
3. 僅執行計畫中的第 0 步，不得修改提示詞、Python 程式、RAG 索引或既有知識文件。
4. 將結果寫入 `current_report` 指向的報告檔。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許讀取：README.md、theme_taxonomy.md、research_*.md、docs/、prompts/、.codex-orchestration/。
- 允許新增／修改：僅 `.codex-orchestration/reports/report-agy-0001.md`。
- 禁止：修改任何現有專案檔案、下載或匯入外部文件、執行重建索引、呼叫模型、建立平行任務。

## 完成條件

報告需列出每一項建議知識的「保留／新增／更新」判定、理由、官方或一手來源連結、查核日期、受影響的本地檔案，以及信心等級。若沒有足夠的權威來源，必須明確標記為「待人工確認」。
