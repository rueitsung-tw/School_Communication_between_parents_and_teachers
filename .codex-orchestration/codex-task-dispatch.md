---
task_id: 0003
title: 同步高風險主題的法令知識卡
status: approved
executor: agy
current_plan: .codex-orchestration/plans/plan-0003.md
current_report: .codex-orchestration/reports/report-agy-0003.md
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

- 允許讀取：`research_D_legal.md`、`theme_taxonomy.md`、任務 0001／0002 報告、相關官方法規頁。
- 允許新增／修改：僅 `theme_taxonomy.md` 與 `.codex-orchestration/reports/report-agy-0003.md`。
- 禁止：修改 Python、提示詞、README、docs、RAG 索引與設定；下載或匯入外部文件；呼叫模型；建立平行任務。

## 前置條件

任務 0002 已完成並核准。`research_D_legal.md` 是本任務唯一的法令研究依據；若與外部頁面衝突，停止並在報告標記 `待 Codex 確認`。

## 完成條件

- 僅三個高風險主題（3、4、10）的法令欄與必要溝通策略文字被更新。
- 不作個案法律定性，不作責任保證，不把調和程序寫成強制或可私下和解。
- 報告列出每項更新、對應法源及 `git diff --check` 結果。
