# 親師溝通 RAG — 兩階段智慧 Ingest 升級計畫

## 背景說明

目前 v2.0 的 RAG 機制是「**直接切段**」：
```
PDF → PyMuPDF 提取原始文字 → 切成 500 字段落 → ChromaDB 向量索引
```

問題：法令條文、教育研究報告的原始文字往往雜亂（頁碼、頁首、表格殘缺），切出來的段落語意不完整，搜尋品質不穩定。

本計畫借鑑 [llm_wiki 的 Two-Step Chain-of-Thought Ingest](https://github.com/nashsu/llm_wiki) 概念，升級為：
```
PDF → 原始文字提取 → [Step 1: LLM 分析理解] → [Step 2: LLM 生成結構化摘要 .md] → 切段 → ChromaDB 索引
```

知識只需「編譯一次」，之後查的是高品質 Wiki 頁，而非雜亂的原始 PDF 段落。

---

## 核心差異

| | 現在（v2.0 直接切段） | 升級後（兩階段 Ingest） |
|---|---|---|
| **索引材料** | PDF 原始切段（含雜訊） | LLM 精煉後的結構化摘要 |
| **大型 PDF** | 可能產生無意義段落 | 每份文件生成 1 份摘要 .md |
| **法令條文** | 條號被截斷、難以搜尋 | 條文名稱、摘要、應用情境完整保留 |
| **新增文件時間** | 快（純切段） | 慢一點（需呼叫 LLM），但只做一次 |
| **搜尋品質** | 中等 | 高（語意更完整） |

---

## 提出的兩個選項

> [!IMPORTANT]
> **選項 1（推薦）：自動兩階段 Ingest**
> 每次新增文件到 `docs/`，系統自動觸發 LLM 分析並生成 `.md` 摘要存入 `docs/summaries/`，再對摘要做向量索引。完全自動，使用者無感。

> [!IMPORTANT]
> **選項 2：手動觸發**
> 在側邊欄「知識庫管理」面板新增「🧠 智慧摘要」按鈕，使用者自行選擇要對哪些文件做 LLM 摘要。適合想控制 LLM 呼叫時機（避免索引期間拖慢系統）的場景。

---

## 詳細實作計畫（選項 1：自動兩階段）

### 新增模組：`ingest_pipeline.py`

負責協調兩階段流程：

```
Stage 1 — 分析（Analysis）
  輸入：原始文件文字（full text）
  呼叫：LLM（現有 Ollama gemma3:12b）
  系統提示：「你是教育知識整理專家，請分析以下文件，輸出 JSON 格式包含：
    - main_topics: 主要主題列表
    - key_concepts: 重要概念與定義
    - legal_references: 法令條文引用（條號 + 摘要）
    - connections: 與親師溝通的關聯性說明」

Stage 2 — 生成摘要（Wiki Generation）
  輸入：Stage 1 的 JSON 分析結果 + 原始文件名稱
  呼叫：LLM
  系統提示：「根據以下分析結果，生成一份 Markdown 格式的知識摘要頁，
    包含 YAML frontmatter（source, topics, generated_at）、
    各主題條目、法令引用、親師溝通應用建議」
  輸出：儲存為 docs/summaries/<原始檔名>_summary.md
```

---

## 修改範圍

### [NEW] `ingest_pipeline.py`（新增）

兩階段 Ingest 的主要邏輯：
- `analyze_document(text, llm_caller)` → Stage 1，回傳 JSON 分析
- `generate_summary(analysis, source_name, llm_caller)` → Stage 2，回傳 Markdown 字串
- `run_two_step_ingest(filepath, ollama_url, model_name)` → 整合兩步驟，儲存摘要 `.md`

---

### [MODIFY] [`rag_engine.py`](file:///f:/親師溝通提示詞/rag_engine.py)

#### `_index_file()` 方法修改
- 新增判斷：若 `docs/summaries/` 已存在對應摘要 `.md`，優先索引摘要而非原始文字
- 若無摘要（舊文件或跳過 LLM 情況），fallback 回現有直接切段邏輯
- 確保**向後相容**，不影響現有功能

#### `_sync_index()` 方法修改
- 新增文件偵測到後，先呼叫 `ingest_pipeline.run_two_step_ingest()`
- 成功生成摘要後，再對摘要 `.md` 進行向量索引
- 失敗時記錄警告並 fallback 到直接切段（不中斷流程）

#### `scan_directory_files()` 修改
- 排除 `docs/summaries/` 目錄本身（避免摘要又被當原始文件二次處理）

---

### [MODIFY] [`app.py`](file:///f:/親師溝通提示詞/app.py)

#### 側邊欄「知識庫管理」新增資訊
- 顯示「已有 LLM 摘要 / 全部文件」比例（例如：`2/3 份文件已智慧摘要`）
- 新增「🧠 重新摘要」按鈕（強制重新對所有文件跑兩階段 Ingest）

---

### [MODIFY] [`config.json`](file:///f:/親師溝通提示詞/config.json)

新增可選設定欄位：
```json
{
  "two_step_ingest": true,
  "ingest_model": "gemma3:12b"
}
```
`two_step_ingest: false` 可關閉兩階段，退回直接切段（供效能考量時使用）。

---

### [MODIFY] [`requirements.txt`](file:///f:/親師溝通提示詞/requirements.txt)

無需新增套件（呼叫 LLM 使用現有 `openai` 套件通過 Ollama 呼叫）。

---

### [MODIFY] `README.md`

更新文件，說明：
- 兩階段 Ingest 的工作原理
- `docs/summaries/` 目錄用途
- `config.json` 新增的 `two_step_ingest` 設定

---

## 目錄結構變化

```diff
 docs/
 ├── 大型法令彙編.pdf          ← 原始文件（不變）
 ├── pdf_extracted.txt         ← 舊的手動提取（保留）
+└── summaries/                ← 新增：LLM 生成的結構化摘要
+    └── 大型法令彙編_summary.md
```

---

## 兩階段 Ingest 的 Prompt 設計（草稿）

### Stage 1 — 分析 Prompt（系統提示）
```
你是國小教育領域的知識整理專家，專精台灣教育法令與親師溝通。
請分析以下文件內容，以 JSON 格式輸出：
{
  "main_topics": ["主題1", "主題2"],
  "key_concepts": [{"term": "概念名稱", "definition": "簡短定義"}],
  "legal_references": [{"article": "條號", "summary": "條文摘要"}],
  "parent_teacher_relevance": "此文件與親師溝通的關聯性說明（2-3句）"
}
```

### Stage 2 — 生成 Wiki 摘要 Prompt（系統提示）
```
你是國小教育知識庫的編輯，請根據以下分析結果，
生成一份繁體中文的 Markdown 知識摘要頁。
格式要求：
1. YAML frontmatter（source, topics, generated_at）
2. ## 摘要 — 2-3 段說明文件核心內容
3. ## 重要概念 — 表格格式（概念 | 說明）
4. ## 相關法令 — 列出條號與重點摘要
5. ## 親師溝通應用 — 具體說明如何應用於親師溝通情境
禁止條列式、禁止官腔、使用台灣繁體中文慣用語。
```

---

## 驗證計畫

### 自動驗證
1. 放入一份 PDF 到 `docs/`，按增量更新，確認 `docs/summaries/` 自動生成摘要 `.md`
2. 確認摘要 `.md` 有正確的 YAML frontmatter
3. 執行 Type A 分析，確認知識庫依據欄位顯示「來源：`xxx_summary.md`」

### 效果對比驗證
- 用「《兒童及少年福利與權益保障法》第53條通報義務」為 query
- 比較直接切段 vs 兩階段 Ingest 的搜尋結果品質

### 邊界測試
- `two_step_ingest: false` 時確認 fallback 正常（直接切段）
- Stage 1 或 Stage 2 LLM 呼叫失敗時確認 fallback 並記錄警告

---

## Open Questions

> [!IMPORTANT]
> **Q1：LLM 摘要模型**
> Stage 1 + Stage 2 預設使用 `config.json` 中的 `gemma3:12b`（與問答相同）。
> 是否要分開設定（例如用較小的模型做 Ingest，節省資源）？

> [!NOTE]
> **Q2：摘要語言**
> Stage 2 生成的摘要 `.md` 預設用**繁體中文**。
> 如果原始 PDF 是英文（例如國際期刊），是否要保留原文部分，或全部翻譯成中文？

> [!NOTE]
> **Q3：`docs/summaries/` 是否納入 git 版控？**
> 摘要是由 LLM 自動生成，屬於「可重新產生的衍生物」，建議加入 `.gitignore`（各環境自己重新生成）。
> 或者，您希望把摘要也納入版控（方便備份與審閱）？
