---
task_id: 0008
title: 修正 Type B 範例中的未確認事實與處置敘述
status: rework_required
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

## Codex 複審：小範圍補正後再驗收

僅允許修改下列六份檔案，其他一律不得修改：

1. `prompts/01_座位安排與班級經營.md`：範例「這次座位安排主要參考全班定期輪換與課堂分組」不是範例輸入可確認事實；改為先釐清本次安排考量後再說明。
2. `prompts/02_成績評量與學習表現.md`：範例「這次國語測驗題型確實比較靈活」不是範例輸入可確認事實；改為先核對考卷、評量標準與作答情況的條件式表述。
3. `prompts/04_管教方式與獎懲制度.md`：範例「當下主要考量」與「我的初衷始終」仍將實際管教動機當作既定事實；改為先了解當時經過與聽取孩子想法，再向家長說明。
4. `prompts/08_生活照顧與責任邊界.md`：範例「我會時常在全班面前統一提醒」是未提供的既定班級做法；改為可邀請、可執行的後續作法，勿假定已在實施。
5. `prompts/09_班費使用與行政事務.md`：範例仍把園區材料費成因、班費原訂用途、既有記錄／報核等資訊當成已確認；改為僅承接家長詢問，承諾彙整、核對並提供明細，不預設費用來源或行政事實。
6. `.codex-orchestration/reports/report-agy-0008.md`：清除第 3 至 6 行尾端空白，修正前後對照表並如實記錄重跑的驗證輸出。

完成後重跑 `pytest -q` 與 `git diff --check`；後者必須實際離退碼 0、無任何錯誤輸出。更新報告後停止等待複審。
