---
task_id: 0002
title: 更新法令研究基礎與可追溯法源
status: rework_required
executor: agy
current_plan: .codex-orchestration/plans/plan-0002.md
current_report: .codex-orchestration/reports/report-agy-0002.md
execution_allowed: true
---

# 單線任務派工單

## 執行順序（不可變更）

1. 先讀本派工單。
2. 再讀 `current_plan` 指向的計畫檔。
3. 僅執行計畫中的唯一工作，不得修改提示詞、Python 程式、RAG 索引或計畫未列出的既有知識文件。
4. 將結果寫入 `current_report` 指向的報告檔。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 範圍與權限

- 允許讀取：`research_D_legal.md`、README.md、theme_taxonomy.md、docs/、任務 0001 報告與相關官方法規頁。
- 允許新增／修改：僅 `research_D_legal.md` 與 `.codex-orchestration/reports/report-agy-0002.md`。
- 禁止：修改 Python、提示詞、README、taxonomy、docs、RAG 索引與設定；下載或匯入外部文件；呼叫模型；建立平行任務。

## 完成條件

報告需列出修改段落、每一項法源的官方直連、未處理項目及 `git diff --check` 結果；若沒有足夠的權威來源，必須明確標記為「待人工確認」。


## 前置條件

任務 0001 已完成；權威法源與需修正的主張已記錄於 `.codex-orchestration/reports/report-agy-0001.md`。本任務只處理 `research_D_legal.md`，不可將法令文字改寫進提示詞、taxonomy 或 RAG 文件。

## Codex 審查決定（2026-08-22）

結論：**退回補正；僅可改寫 `research_D_legal.md` 與 `report-agy-0002.md`。**

1. 個資法段落必須區分：公立學校通常屬公務機關，應依第 15、16 條評估；私立學校或其他非公務機關才依第 19、20 條評估。不可將第 19 條當作所有學校 LINE 群組情境的唯一條件。
2. 「關鍵實務判例與案例分析」不可使用沒有案號、裁判書連結或官方裁判摘要支持的「法院多認定／可能判決」結論。請二擇一：補上可核對的司法院裁判來源；或改名為「情境風險分析」，且明確表明不是判例整理。
3. 將「霸凌或性別事件均於 24 小時內完成法定通報」改成依各該法規與校內權責程序的條件式提醒，並於文內附正確一手法源；避免將不同事件類型與時點義務合併成單一絕對規則。

補正後覆寫 `current_report`，並執行 `git diff --check`；完成後停止等待 Codex 複審。
