---
task_id: 0009
title: RAG 來源信任與未涵蓋主題安全降級設計
status: rework_required
executor: agy
current_plan: .codex-orchestration/plans/plan-0009.md
current_report: .codex-orchestration/reports/report-agy-0009.md
execution_allowed: true
---

# 單線任務派工單

## 必讀順序（不得省略）

1. 本派工單：`.codex-orchestration/codex-task-dispatch.md`
2. 計畫檔：`.codex-orchestration/plans/plan-0009.md`
3. 計畫檔「必讀檔案與順序」列出的 README、RAG 實作、上傳工具、設定、測試與任務 0004、0007、0008 報告。
4. 完整讀畢並在報告勾列後，才可進行設計盤點。

## 執行規則

1. 僅執行計畫中的唯一工作。
2. 僅在 `status: approved` 時執行；本任務已獲准執行。
3. 僅能新增／修改：`.codex-orchestration/reports/report-agy-0009.md`。
4. 禁止修改：`app.py`、`rag_engine.py`、`utils.py`、`ingest_pipeline.py`、README、測試、設定、`docs/`、`.chromadb/`、提示詞與任何其他檔案；不得呼叫模型、網路或建立平行任務。
5. 寫完報告後停止，等待 Codex 審查；不可自行開啟下一個任務。

## 完成條件

- 報告完整勾列 16 份必讀檔案。
- 提出三類來源的最小 metadata、資料流、LLM 使用邊界、向後相容與分階段實作方案。
- 說明教師內容不屬 11 個主題時的通用提示詞 fallback、教師告知與安全失敗規則。
- 精確列出日後實作會觸及的檔名與函式，不憑空宣稱現有 metadata。
- `git diff --check` 通過，且工作樹除報告外無本任務新增修改。

## Codex 複審：僅修正設計報告

僅允許修改 `.codex-orchestration/reports/report-agy-0009.md`，不得修改任何程式、設定、測試、提示詞、文件或索引。補正下列四點：

1. **現況盤點須精確**：`rag_engine.py::_index_file()` 目前實際寫入 `source`、`indexed_from`、`filename`、`is_summary`、`chunk_index`；報告不得說存在 `indexed_at`，也不得將函式寫成不存在的 `index_file()`。
2. **摘要來源傳遞須可實作**：僅在 `ingest_pipeline.py` 的 YAML frontmatter 寫入 `trust_level`，不會自動成為 Chroma metadata；設計必須明定 `rag_engine.py::_index_file()` 如何從原始文件的來源紀錄／manifest 取得分類，再將其寫入每個 chunk，並說明摘要索引時仍以原始來源為準。
3. **來源分類建立方式須完整**：明確定義官方／校務、教師個案／參考、網址／未分類資料各自如何在新增時取得分類。應以管理者明確選擇為主要機制；網址預設未核定、歷史與未標記資料保守降級為未核定。不得把所有教師上傳一律歸為網址類型，也不得只靠檔名推斷可信度。
4. **未涵蓋主題 fallback 須符合現況**：目前僅有教師手動 `selected_theme_key` 下拉選擇，沒有自動主題分類。設計應採明確的「00 通用親師溝通情境」手動 fallback（可另提未來自動分類為後續選項），並定義 Type A／B 通用提示詞任一載入失敗時不得呼叫 LLM 的安全失敗分支。

更新報告後再執行 `git diff --check`；如實記錄離退碼與任何行尾提示後停止等待複審。

## Codex 複審：設計完整性補正（僅報告）

只允許修改 `.codex-orchestration/reports/report-agy-0009.md`。請補齊以下兩項，程式一律不得修改：

1. **最小 metadata 契約表**：列出 `trust_level`、`author_type`、`verified_status`、`source_url` 的型別、允許值與預設值；明定只有管理者明確標為 `official` 的來源可為 `verified`，`teacher_case` 與 `external_unverified` 預設／維持 `unverified`。並說明 manifest 的鍵必須使用與現有 `source_fpath` 相同的正規化絕對路徑，否則 `_index_file()` 無法穩定查回來源紀錄。
2. **manifest 寫入責任與精確改動點**：選定一個最小介面（例如 `RAGEngine.register_source_metadata()`），說明由 `app.py` 的檔案上傳與網址抓取兩條成功路徑在寫入／索引前呼叫它；定義 URL 的 `source_url` 使用教師輸入的 URL，檔案上傳為空字串。將這個介面與相關 `app.py` 區塊納入「精確改動檔名與函式對照表」，並說明直接放入 `docs/`、無 manifest 的檔案為何仍安全降級。

重跑 `git diff --check`，如實記錄結果後停止等待複審。

## Codex 複審：最小範圍與實際路徑補正（僅報告）

只允許修改 `.codex-orchestration/reports/report-agy-0009.md`：

1. **網址抓取路徑**：目前 `app.py` 將 `utils.fetch_url_content()` 回傳的 `filename` 組為 `target_path = os.path.join(DOCS_DIR, filename)`，寫入的是抓取器產生的 `web_<title>_<timestamp>.md` 類型檔案；報告不得寫成不存在的 `docs/web_crawl_<hash>.txt`。設計中 `register_source_metadata()` 必須以該實際 `target_path` 為 `source_fpath`，並以 `input_url` 為 `source_url`。
2. **單一來源真相**：既然設計已指定 `docs/manifest.json` 為信任 metadata 的來源真相，請移除 `ingest_pipeline.py`／摘要 YAML frontmatter 的 `trust_level` 傳遞需求、改動表項目與對應風險緩解。說明摘要索引始終以 `_index_file(source_fpath, material_path)` 的原始 `source_fpath` 查 manifest，故不需要修改摘要流程。

重跑 `git diff --check`，如實記錄後停止等待最終複審。
