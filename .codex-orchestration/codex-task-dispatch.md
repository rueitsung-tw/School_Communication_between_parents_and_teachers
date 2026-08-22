---
task_id: 0001
title: 知識圖譜網路查核與更新建議
status: rework_required
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

## Codex 審查決定（2026-08-22）

結論：**退回補正；僅可改寫同一份報告，不得進入下一步。**

補正項目：

1. 每一個法令條目都必須提供可直接開啟的官方一手 URL；僅寫「全國法規資料庫」或「教育部系統」不符合完成條件。
2. 修正《校園霸凌防制準則》令號：應以教育部官方頁所載的 **臺教學（五）字第 1132801790A 號**為準，不得使用報告中的 `1132801799A`；並以官方頁面確認施行日期與程序描述。
3. 將「師對生已移出霸凌準則」與個資／誹謗等絕對化表述，改成附明確法源、適用條件與限制的中性說法；無法證實即標記 `待人工確認`。
4. 對照並列出已讀的 `docs/` 內現有法令文件；不要只比較研究報告與 taxonomy。
5. 將心理學的「完全正確／精確」改為證據範圍內的描述，並為原始研究或正式出版品補 DOI、出版社頁面或穩定書目連結。

完成補正後覆寫 `current_report`，然後停止等待下一次 Codex 審查。
