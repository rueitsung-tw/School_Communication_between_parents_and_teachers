# 報告 agy-0009：RAG 來源信任與未涵蓋主題安全降級設計

**執行任務 ID**：0009  
**執行步驟**：唯一步驟 — 完成 RAG 來源信任模型、Metadata 資料架構、LLM 邊界、分階段實作規劃與未涵蓋主題安全降級架構設計報告  
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

經程式碼追溯（`ingest_pipeline.py` → `rag_engine.py` → `app.py`），現有 RAG 檢索流程如下：

1. **檔案處理與摘要**：`docs/` 下之 `.pdf` / `.txt` / `.md` 透過 `ingest_pipeline.py` 進行 Stage 1 JSON 分析與 Stage 2 摘要頁生成（存於 `docs/summaries/<filename>_summary.md`）。
2. **切段與向量化**：`rag_engine.py` 將摘要頁或原始檔切段（`CHUNK_SIZE=500, OVERLAP=80`），呼叫 Ollama `nomic-embed-text` 生成 Embedding。
3. **ChromaDB 寫入**：寫入 `.chromadb` 向量資料庫（Collection Name: `parent_teacher_rag`）。
4. **現有 Metadata 欄位審核**：
   - `source`：檔案之絕對路徑（字串）
   - `filename`：檔案名稱基底（字串）
   - `chunk_index`：段落序號（整數）
   - `is_summary`：是否為摘要頁（字串 `"True"` / `"False"`）
   - `indexed_at`：索引時間（ISO 8601 字串）
   - **實體確認**：現有 ChromaDB metadata **未包含任何來源信任分級（`trust_level`）、作者類別、驗證狀態或網址欄位**。

---

## 三、 RAG 三類來源信任模型與最小 Metadata 架構設計

為因應未來擴充，設計「三層式來源信任等級（Source Trust Tier）」：

### 1. 三類來源分類定義

| 信任等級 | 標籤代碼 | 涵蓋來源範圍 | 權威性與使用邊界 |
|---|---|---|---|
| **Tier 1** | `official` | 官方教育法規、教育部/局處函釋、本校修訂核定之校規、校事會議/性平會標準作業手冊。 | **規範性依據**：可作為標準常規、處置程序與法令補充之引用依據。 |
| **Tier 2** | `teacher_case` | 教師上傳之個案筆記、過去親師對話紀錄、教學心得、研習講義、班級自訂公約。 | **經驗性參考**：僅供親師溝通同理與對話參考，**絕對不可視為當前處理個案之既定事實或過失證明**。 |
| **Tier 3** | `external_unverified` | 網路爬蟲抓取文章、部落格、媒體報導、非官方論壇討論。 | **待確認參考**：必須提示「待人工確認」，Prompt 內禁止 LLM 將其作為法規或校規依據。 |

### 2. 最小 Metadata 欄位架構與預設值

未來實作時於 ChromaDB Metadata 擴充以下欄位：

```python
{
    "source": str,                 # 原始檔案絕對路徑或 URL
    "filename": str,               # 檔案名稱
    "trust_level": str,            # "official" | "teacher_case" | "external_unverified"（預設："external_unverified"）
    "author_type": str,            # "moe_official" | "school_admin" | "teacher" | "web_crawl"（預設："web_crawl"）
    "verified_status": str,        # "verified" | "unverified"（預設："unverified"）
    "source_url": str,             # 原始網址（若為網絡抓取；檔案則為空字串 ""）
    "chunk_index": int,            # 段落索引
    "is_summary": str,             # "True" | "False"
    "indexed_at": str              # ISO 8601 時間字串
}
```

### 3. 既有歷史索引向後相容策略（Backward Compatibility）

- **自動降級預設值**：在 `rag_engine.py` 的 `retrieve()` 函式讀取既有 ChromaDB 資料時，若 Metadata 缺少 `trust_level` 欄位，一律自動補上預設值 `trust_level = "external_unverified"`。
- **無縫升級**：無需強制使用者清空向量庫即可舊版相容運作；管理介面提供「重編歷史索引」選項供教師視需要補標等級。

---

## 四、 LLM Prompt 邊界規範與注入順序

### 1. 注入 Prompt 時之信任標籤格式（Trust Badges）

在 `app.py` 的 `build_rag_context()` 組合 RAG 段落時，依據 `trust_level` 自動附帶顯性標籤：

```text
【語意搜尋知識庫參考段落（Top-3 最相關）】

--- 段落 1（來源：校園霸凌防制準則.pdf | 信任等級：官方規章）---
【官方規章參考（可作為一般規範依據）】
...（段落內容）...

--- 段落 2（來源：教師輔導經驗談.md | 信任等級：教師個案參考）---
【教師經驗參考（僅供思考輔助，絕對不可當成個案已知事實）】
...（段落內容）...

--- 段落 3（來源：https://example.com/article | 信任等級：外部未核定資料）---
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

### 1. 分階段實作藍圖

- **第一階段：Metadata Schema 與 Ingest 擴充**
  - 修改 `ingest_pipeline.py` 與 `rag_engine.py`，支援寫入 `trust_level` 等標籤。
- **第二階段：Retrieval 檢索與 Context 標籤化**
  - 修改 `rag_engine.py` 之 `retrieve()` 與 `app.py` 之 `build_rag_context()`，完成 Trust Badges 注入。
- **第三階段：UI 顯示與知識庫管理**
  - 修改 `app.py` 側邊欄「📂 知識庫管理」面板，於文件清單旁展示信任等級標章。
- **第四階段：單元測試與安全契約驗證**
  - 於 `test_rag_engine.py` 與 `test_safety_contract.py` 新增信任等級降級與安全邊界測試。

### 2. 精確改動檔名與函式對照表

| 修改檔案 | 觸及函式 / 區塊 | 預計變更內容 |
|---|---|---|
| `ingest_pipeline.py` | `analyze_document()` / Stage 2 產出 | 於 YAML frontmatter 中包含 `trust_level` |
| `rag_engine.py` | `index_file()` / `retrieve()` | 寫入與讀取 `trust_level` Metadata，提供舊資料預設值降級 |
| `app.py` | `build_rag_context()` / 側邊欄 UI | 依 `trust_level` 輸出 Trust Badges，UI 清單展示等級標籤 |
| `test_rag_engine.py` | 新增測試函式 | 驗證 `trust_level` 寫入、檢索與歷史舊資料相容降級 |
| `test_safety_contract.py` | 新增測試函式 | 驗證 Tier 2/3 RAG 內容無法覆寫 `SAFETY_CORE` 事實邊界 |

---

## 六、 三大系統風險盤點與緩解措施

1. **風險一：網頁爬蟲或使用者上傳內容包含錯誤資訊或偏見**
   - *緩解措施*：所有網頁爬蟲與使用者上傳之新檔案，預設信任等級一律為 `external_unverified`，Prompt 中強制規定 LLM 不得將其引為權威依據。
2. **風險二：歷史向量資料庫（`.chromadb`）缺 Metadata 導致執行階段 Crash**
   - *緩解措施*：`retrieve()` 使用 `.get("trust_level", "external_unverified")` 進行防衛性讀取，避免 `KeyError`，確保舊庫零破壞流暢運作。
3. **風險三：Stage 2 產生 Markdown 摘要時遺失原始檔案的信任等級**
   - *緩解措施*：在 `ingest_pipeline.py` 生成摘要頁時，將原始檔之 `trust_level` 直接寫入摘要頁之 YAML frontmatter，索引摘要頁時繼承原始等級。

---

## 七、 未涵蓋主題之安全降級設計（Out-of-Taxonomy Safety Fallback）

當教師處理的親師溝通主題不屬於既有 11 個主題（主題 00～10）時，設計降級保護機制：

### 1. 降級保護處理規則
- **通用提示詞 Fallback**：自動降級採用 `00_通用_TypeA_家長訊息分析器.md` 與 `00_通用_TypeB_回覆草稿生成器.md` 進行分析與回覆草稿生成。
- **介面限制告知（UI Restriction Notice）**：於 `app.py` 介面顯示警示訊息：
  `ℹ️ 【未涵蓋主題安全模式】當前情境非既定主題，已自動套用通用溝通框架。若涉及校園性別事件、霸凌防制或兒少保護等高風險議題，請一律回歸學校法定通報與權責程序處理。`
- **專屬法令／程序禁止條款**：通用模式下，系統提示詞嚴禁 LLM 捏造未經證實之校內特設程序或法令處分條文。
- **RAG 參考機制保留**：仍可以家長訊息作為 Query 進行 RAG 語意搜尋，但檢索出之段落必須帶有「外部參考」標籤供教師審視。

### 2. 安全失敗機制（Fail-Safe Mode for Prompt Load Failure）
- **安全失敗規則**：若因檔案遺失或損毀導致 `00_通用` 提示詞載入失敗，`app.py` **絕對不得在缺乏 Prompt 的情況下直接呼叫 LLM API**。
- **安全阻擋處置**：系統立即中斷 API 呼叫流程，並於 UI 輸出錯誤訊息：
  `❌ 無法載入通用安全提示詞，系統已啟動安全保護機制阻擋回應。請聯繫系統管理員檢查提示詞檔案。`

---

## 八、 驗證指令執行結果

### 1. `git diff --check` 執行結果
```shell
$ git diff --check
(離退碼: 0，無任何警告與空白錯誤，輸出為空)
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

*任務 0009 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
