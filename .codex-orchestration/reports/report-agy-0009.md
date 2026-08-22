# 報告 agy-0009：RAG 來源信任與未涵蓋主題安全降級設計（退回補正最終版）

**執行任務 ID**：0009
**執行步驟**：唯一步驟 — 完成 RAG 來源信任模型、Metadata 資料架構、LLM 邊界、分階段實作規劃與未涵蓋主題安全降級架構設計報告（補正版）
**執行者**：agy
**執行日期**：2026-08-22

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0009.md` 要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0009.md`
- [x] 3. `README.md`
- [x] 4. `app.py`
- [x] 5. `rag_engine.py`
- [x] 6. `utils.py`
- [x] 7. `ingest_pipeline.py`
- [x] 8. `config.json`
- [x] 9. `requirements.txt`
- [x] 10. `test_rag_engine.py`
- [x] 11. `test_ingest_pipeline.py`
- [x] 12. `test_safety_contract.py`
- [x] 13. `test_response_contract.py`
- [x] 14. `.codex-orchestration/reports/report-agy-0004.md`
- [x] 15. `.codex-orchestration/reports/report-agy-0007.md`
- [x] 16. `.codex-orchestration/reports/report-agy-0008.md`

---

## 二、 現有 RAG 資料流程與 Metadata 實體盤點

經程式碼精確追溯（`ingest_pipeline.py` → `rag_engine.py` 私有函式 `_index_file` → `app.py`），現有 RAG 檢索流程與 metadata 如下：

1. **檔案處理與摘要**：`docs/` 下之 `.pdf` / `.txt` / `.md` 透過 `ingest_pipeline.py` 進行 Stage 1 JSON 分析與 Stage 2 摘要頁生成（存於 `docs/summaries/<filename>_summary.md`）。
2. **切段與向量化**：`rag_engine.py::_index_file(source_fpath, material_path)` 將摘要頁或原始檔切段（`CHUNK_SIZE=500, OVERLAP=80`），呼叫 Ollama `nomic-embed-text` 生成 Embedding。
3. **ChromaDB 寫入**：寫入 `.chromadb` 向量資料庫（Collection Name: `parent_teacher_rag`）。
4. **現有 Metadata 欄位精確盤點**：
   - 於 `rag_engine.py` 第 533~539 行 `_index_file()` 中，實際寫入 ChromaDB 之 `metas` 欄位恰為以下 5 項：
     - `source`：原始檔案之絕對路徑（字串）
     - `indexed_from`：實際被向量化材料之路徑（摘要或原始檔路徑）
     - `filename`：檔案名稱基底（字串）
     - `is_summary`：是否為摘要頁（字串 `"True"` / `"False"`）
     - `chunk_index`：段落序號（整數）
   - **精確判定**：現有程式碼中**並無 `indexed_at` 欄位**，且寫入私有函式名稱為 `_index_file(source_fpath, material_path)`（非 `index_file()`）。現有 ChromaDB metadata **未包含任何來源信任分級（`trust_level`）、作者類別、驗證狀態或網址欄位**。

---

## 三、 RAG 三類來源信任模型、最小 Metadata 契約與寫入機制

### 1. 三類來源分類與權威性定義

| 信任等級 | 標籤代碼 | 涵蓋來源範圍 | 權威性與使用邊界 |
|---|---|---|---|
| **Tier 1** | `official` | 官方教育法規、教育部/局處函釋、本校修訂核定之校規、校事會議/性平會標準作業手冊。 | **規範性依據**：可作為標準常規、處置程序與法令補充之引用依據。 |
| **Tier 2** | `teacher_case` | 教師上傳之個案筆記、過去親師對話紀錄、教學心得、研習講義、班級自訂公約。 | **經驗性參考**：僅供親師溝通同理與對話參考，**絕對不可視為當前處理個案之既定事實或過失證明**。 |
| **Tier 3** | `external_unverified` | 網路爬蟲抓取文章、網址匯入、部落格、媒體報導、未經核定之外部資料。 | **待確認參考**：必須提示「待人工確認」，Prompt 內禁止 LLM 將其作為法規或校規依據。 |

### 2. 最小 Metadata 欄位契約表（Schema Contract）

| 欄位名稱 | 資料型態 | 允許值範圍（Enum / Format） | 預設值 | 規則說明與限制 |
|---|---|---|---|---|
| `trust_level` | `str` | `"official"` \| `"teacher_case"` \| `"external_unverified"` | `"external_unverified"` | 表示來源信任等級。 |
| `author_type` | `str` | `"moe_official"` \| `"school_admin"` \| `"teacher"` \| `"web_crawl"` | `"web_crawl"` | 表示作者身份屬性。 |
| `verified_status` | `str` | `"verified"` \| `"unverified"` | `"unverified"` | **約束規則**：僅管理者明確標為 `official` 的來源可設為 `"verified"`；`teacher_case` 與 `external_unverified` 必須維持 `"unverified"`。 |
| `source_url` | `str` | 原始 HTTP/HTTPS 網址 或 空字串 `""` | `""` | 檔案上傳預設為 `""`；網址抓取帶入教師輸入之 URL。 |

### 3. Manifest 鍵（Key）正規化要求

- 於 `docs/manifest.json` 檔案清單中，字典的鍵（Key）**必須使用與 `rag_engine.py` 相同的 `normalize_path(source_fpath)` 正規化絕對路徑**（統一 Windows 磁碟機大寫與斜線格式）。
- **理由**：若路徑大小寫或斜線不一致（例如 `c:\docs\file.pdf` 與 `C:/docs/file.pdf`），`_index_file()` 在進行字典比對時將無法穩定查回原始來源紀錄。

### 4. 來源分類建立機制與 Manifest 寫入責任

檔案或網址新增時，最小介面與呼叫路徑如下：

- **最小介面設計**：於 `RAGEngine` 新增公開方法：
  ```python
  def register_source_metadata(
      self,
      source_fpath: str,
      trust_level: str = "external_unverified",
      author_type: str = "web_crawl",
      verified_status: str = "unverified",
      source_url: str = ""
  ) -> bool:
      """將原始檔案或網址之來源 metadata 以 normalize_path(source_fpath) 為 key 登記至 docs/manifest.json"""
  ```

- **`app.py` 的呼叫責任**：
  1. **檔案上傳成功路徑**：當使用者於 Streamlit 介面上傳 `.pdf` / `.txt` / `.md` 儲存至 `docs/` 成功後，由 `app.py` 呼叫 `rag.register_source_metadata(source_fpath=saved_path, trust_level=chosen_level, author_type="school_admin" if chosen_level == "official" else "teacher", verified_status="verified" if chosen_level == "official" else "unverified", source_url="")`。`source_url` 為空字串。
  2. **網址抓取成功路徑**：當使用者輸入網址抓取內文並存為 `docs/web_crawl_<hash>.txt` 成功後，由 `app.py` 呼叫 `rag.register_source_metadata(source_fpath=saved_path, trust_level="external_unverified", author_type="web_crawl", verified_status="unverified", source_url=input_url)`。`source_url` 帶入教師輸入之 URL。

- **無 Manifest 檔案之安全降級**：
  - 若使用者未透過 UI 登記，直接複製檔案至 `docs/` 資料夾，watchdog 監控自動觸發 `_index_file(source_fpath, material_path)` 時，`_index_file()` 以 `normalize_path(source_fpath)` 查詢 `docs/manifest.json` 查無紀錄。
  - 系統實施**防衛性安全降級**：自動以預設值 `trust_level="external_unverified"`, `author_type="web_crawl"`, `verified_status="unverified"`, `source_url=""` 寫入此檔案之 Chroma chunk metadata。

### 5. 摘要來源傳遞與 Chroma Metadata 真正寫入機制

1. **`_index_file()` 真正寫入 Chroma Chunk Metadata**：
   - 於 `rag_engine.py::_index_file(source_fpath, material_path)` 中：
     - 以 `normalize_path(source_fpath)` 向 `docs/manifest.json` 查詢取得登記之 metadata。若查無紀錄，採用安全降級預設值。
     - 於建構每個 chunk 的 `metas` 字典時，真正寫入欄位：
       ```python
       metas = [{
           "source": source_fpath,
           "indexed_from": material_path,
           "filename": os.path.basename(source_fpath),
           "is_summary": str(is_summary),
           "chunk_index": i,
           "trust_level": trust_level,            # "official" | "teacher_case" | "external_unverified"
           "author_type": author_type,            # "moe_official" | "school_admin" | "teacher" | "web_crawl"
           "verified_status": verified_status,    # "verified" | "unverified"
           "source_url": source_url               # URL 或 ""
       } for i in range(len(valid))]
       ```
     - 透過 `self._collection.add(..., metadatas=metas)` 將來源信任資料真正持久化寫入 ChromaDB。
     - **重點**：無論 `material_path` 是摘要頁或是原始檔案，所有 chunk 均統一傳承並錨定於 `source_fpath` 原始檔案之信任等級。

### 6. 既有歷史索引向後相容策略（Backward Compatibility）

- **讀取時防衛降級**：在 `rag_engine.py::retrieve()` 讀取 ChromaDB 回傳之 `metadatas` 時，使用 `meta.get("trust_level", "external_unverified")`。若歷史舊 chunk 缺少 `trust_level` 欄位，自動補上 `"external_unverified"` 進行安全降級，確保不發生 `KeyError` 且零破壞相容。

---

## 四、 LLM Prompt 邊界規範與注入順序

### 1. 注入 Prompt 時之信任標籤格式（Trust Badges）

在 `app.py` 的 `build_rag_context()` 組合 RAG 段落時，依據 `r.get("trust_level")` 自動附帶顯性標籤：

```text
【語意搜尋知識庫參考段落（Top-3 最相關）】

--- 段落 1（來源：校園霸凌防制準則.pdf | 信任等級：官方規章 | 狀態：已核定）---
【官方規章參考（可作為一般規範依據）】
...（段落內容）...

--- 段落 2（來源：教師輔導經驗談.md | 信任等級：教師個案參考 | 狀態：未核定）---
【教師經驗參考（僅供思考輔助，絕對不可當成個案已知事實）】
...（段落內容）...

--- 段落 3（來源：https://example.com/article | 信任等級：外部未核定資料 | 狀態：未核定）---
【外部未核定資料（須待人工確認，不得直接引用為法令或校規）】
...（段落內容）...
```

### 2. 階層式邊界優先原則（Hierarchy of Rules）

在系統 Prompt 內部，嚴格貫徹以下四層效力優先順序：

1. **第一優先（最高指令）**：`SAFETY_CORE`（通用事實邊界與高風險安全核心；任何 RAG 內容均**不得覆寫**安全核心）。
2. **第二優先**：教師補充背景（`{context}`）與家長原始訊息（`{parent_message}`）。RAG 內容不得否定或捏造教師未補充之事實。
3. **第三優先**：主題任務提示詞（Type A / Type B）與靜態知識卡（`theme_taxonomy.md`）。
4. **第四優先**：RAG 檢索段落（依據 `trust_level` 標籤提供輔助資訊）。

---

## 五、 分階段實作規劃與盤點改動檔名／函式

### 1. 精確改動檔名與函式對照表

| 修改檔案 | 觸及函式 / 區塊 | 預計變更內容 |
|---|---|---|
| `ingest_pipeline.py` | `analyze_document()` / Stage 2 產出 | 於 Stage 2 Markdown Frontmatter 中傳承寫入 `trust_level` |
| `rag_engine.py` | 新增 `register_source_metadata()` 介面 | 提供登記原始檔案 metadata 至 `docs/manifest.json` 之公開方法，key 統一使用 `normalize_path(source_fpath)` |
| `rag_engine.py` | `_index_file()` / `retrieve()` | 於 `_index_file()` 中向 `manifest.json` 查詢並將 `trust_level`、`author_type`、`verified_status`、`source_url` 寫入 `metas` 並存入 ChromaDB；於 `retrieve()` 中讀取此 4 欄位並提供舊資料預設值降級 |
| `app.py` | 檔案上傳區塊 / 網址抓取區塊 | 於上傳或抓取成功後呼叫 `rag.register_source_metadata()` 登記；上傳檔案傳入 `source_url=""`，網址抓取傳入教師輸入之 URL |
| `app.py` | `build_rag_context()` / 側邊欄 UI | 依 `trust_level` 輸出 Trust Badges，UI 清單展示等級標籤與驗證狀態 |
| `test_rag_engine.py` | 新增單元測試 | 驗證 `register_source_metadata()` 寫入、`_index_file()` 讀取 manifest、`retrieve()` 檢索與未登記檔案安全降級 |
| `test_safety_contract.py` | 新增單元測試 | 驗證 Tier 2/3 RAG 內容無法覆寫 `SAFETY_CORE` 事實邊界 |

---

## 六、 三大系統風險盤點與緩解措施

1. **風險一：網頁抓取或未核定上傳內容包含錯誤資訊或偏見**
   - *緩解措施*：所有網頁抓取與未手動分類之檔案，預設信任等級一律為 `external_unverified`，Prompt 中強制規定 LLM 不得將其引為權威依據。
2. **風險二：歷史向量資料庫（`.chromadb`）缺 Metadata 欄位導致執行階段 KeyError Crash**
   - *緩解措施*：`retrieve()` 讀取時採 `meta.get("trust_level", "external_unverified")` 進行防衛性讀取，確保舊庫零破壞流暢運作。
3. **風險三：Stage 2 產生 Markdown 摘要時遺失原始檔案的信任等級**
   - *緩解措施*：在 `ingest_pipeline.py` 生成摘要頁時，將原始檔之 `trust_level` 寫入摘要頁 YAML frontmatter；`_index_file()` 索引時優先以 `docs/manifest.json` 的紀錄為準，確保摘要與原始檔等級一致。

---

## 七、 未涵蓋主題之手動 Fallback 與安全失敗設計（Out-of-Taxonomy Safety Fallback）

### 1.現狀說明與手動 Fallback 機制
- **現狀說明**：目前系統依賴 Streamlit 側邊欄下拉選單手動選擇 `selected_theme_key`（包含 `"00_通用"` 及 10 個主題），**系統目前無 LLM 自動主題分類機制**。
- **手動 Fallback 操作路徑**：當家長訊息內容不屬於主題 01～10 範疇時，由教師手動於下拉選單選擇「00 通用親師溝通情境」作為 Fallback（可另提未來開發自動主題分類作為後續擴充選項）。

### 2. 未涵蓋主題（00 通用）降級保護規則
- **通用提示詞調用**：系統讀取並調用 `00_通用_TypeA_家長訊息分析器.md` 與 `00_通用_TypeB_回覆草稿生成器.md`。
- **介面限制告知（UI Restriction Notice）**：於 `app.py` 介面顯示警示訊息：
  `ℹ️ 【未涵蓋主題安全模式】當前情境採通用親師溝通框架。若涉及校園性別事件、霸凌防制或兒少保護等高風險議題，請一律回歸學校法定通報與權責程序處理。`
- **專屬法令／程序禁止條款**：通用模式下，系統 Prompt 嚴禁 LLM 捏造未經證實之校內特設程序或專屬法令條文。
- **RAG 參考機制保留**：仍可以家長訊息進行 RAG 語意搜尋，檢索段落帶有 Trust Badges 供教師參閱。

### 3. 安全失敗機制（Fail-Safe Mode for Prompt Load Failure）
- **安全失敗觸發條件**：在 `app.py` 中，執行前檢查通用提示詞載入狀態。若 `system_prompt_a`（Type A）**或** `system_prompt_b`（Type B）**任一載入失敗**（包含檔案遺失、讀取結果為 `None` 或空字串）：
- **嚴禁裸奔呼叫 API**：系統**絕對不得在缺乏安全 Prompt 的情況下直接呼叫 LLM API**。
- **安全阻擋處置**：系統立即中斷 API 呼叫流程，並於 UI 輸出顯性阻擋錯誤訊息：
  `❌ 無法載入通用安全提示詞（Type A 或 Type B 載入失敗），系統已啟動安全保護機制中斷 API 呼叫，禁止無安全提示詞呼叫 API。請檢查 prompts/00_通用_*.md 檔案。`

---

## 八、 驗證指令執行結果

### 1. `git diff --check` 執行結果
離退碼為 0，無任何格式與空白錯誤。實際指令輸出包含 Git LF/CRLF 換行符號轉換提示訊息：

```shell
$ git diff --check
warning: in the working copy of '.codex-orchestration/reports/report-agy-0009.md', LF will be replaced by CRLF the next time Git touches it
```

### 2. `git status` 執行結果
```shell
$ git status
On branch main
Changes not staged for commit:
	modified:   app.py
	modified:   prompts/00_通用_TypeB_回覆草稿生成器.md
	modified:   prompts/01_座位安排與班級經營.md
	modified:   prompts/02_成績評量與學習表現.md
	modified:   prompts/03_同儕衝突與霸凌處理.md
	modified:   prompts/04_管教方式與獎懲制度.md
	modified:   prompts/06_特殊生權益與融合教育.md
	modified:   prompts/07_校園安全與意外事故.md
	modified:   prompts/08_生活照顧與責任邊界.md
	modified:   prompts/09_班費使用與行政事務.md
	modified:   utils.py

Untracked files:
	.codex-orchestration/reports/report-agy-0002.md
	.codex-orchestration/reports/report-agy-0003.md
	.codex-orchestration/reports/report-agy-0004.md
	.codex-orchestration/reports/report-agy-0005.md
	.codex-orchestration/reports/report-agy-0006.md
	.codex-orchestration/reports/report-agy-0007.md
	.codex-orchestration/reports/report-agy-0008.md
	.codex-orchestration/reports/report-agy-0009.md
	test_app_ui_wording.py
	test_response_contract.py
	test_safety_contract.py
```

---

*任務 0009 設計完整性補正執行完畢，報告已更新，停止執行，等待 Codex 最終複審。*
