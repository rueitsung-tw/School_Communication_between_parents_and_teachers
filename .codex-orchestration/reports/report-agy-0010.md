# 報告 agy-0010：RAG 來源信任核心與 Manifest Metadata 實作

**執行任務 ID**：0010
**執行步驟**：Task 1 — 建立 manifest 來源登記與 Chroma metadata 核心能力
**執行者**：agy
**執行日期**：2026-08-22

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0010.md` 要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0010.md`
- [x] 3. `.codex-orchestration/reports/report-agy-0009.md`
- [x] 4. `rag_engine.py`
- [x] 5. `test_rag_engine.py`
- [x] 6. `test_safety_contract.py`
- [x] 7. `.gitignore`

---

## 二、 實作內容與 Manifest 契約

1. **Manifest 來源信任登記介面**：
   - 於 `rag_engine.py` 之 `RAGEngine` 類別中新增公開方法 `register_source_metadata(source_fpath, trust_level, author_type, verified_status, source_url)`。
   - 字典 Key 統一採 `normalize_path(source_fpath)` 正規化絕對路徑。
   - 實施嚴格 Enum 驗證與權限約束：僅有 `trust_level == "official"` 時才允許 `verified_status = "verified"`；非 `official` 強制拒絕 `verified` 寫入（傳回 `False` 且不寫入 manifest）。
   - 寫入採用暫存檔 `.tmp` + `os.replace()` 原子更新機制，防止檔案半寫入損毀。

2. **Chroma Chunk 索引與檢索安全傳遞**：
   - `_index_file(source_fpath, material_path)`：固定以 `normalize_path(source_fpath)` 向 `docs/manifest.json` 查詢來源 metadata，並寫入 `trust_level`、`author_type`、`verified_status`、`source_url` 4 個欄位至每個 chunk metas 中。
   - `retrieve(query, top_k)`：回傳字典新增上述 4 個欄位。若歷史舊 chunk 缺少此 4 欄位，自動以安全預設值（`external_unverified` / `web_crawl` / `unverified` / `""`）防衛性降級。

3. **版本控制過濾**：
   - 在 `.gitignore` 追加 `docs/manifest.json` 一行，確保本地登記檔不納入 Git 版控。

---

## 三、 TDD 執行證據（RED & GREEN）

### 1. RED 階段測試輸出

在未修改 `rag_engine.py` 前，先於 `test_rag_engine.py` 新增 4 項新增單元測試並執行 `pytest -q test_rag_engine.py`，確認因 `register_source_metadata` 與 `_get_source_metadata` 尚不存在而符合預期失敗：

```shell
$ pytest -q test_rag_engine.py
...FFFF                                                                  [100%]
================================== FAILURES ===================================
_____ test_register_source_metadata_normalizes_key_and_persists_contract ______
E           AttributeError: 'RAGEngine' object has no attribute 'register_source_metadata'
_________ test_register_source_metadata_rejects_verified_non_official _________
E           AttributeError: 'RAGEngine' object has no attribute 'register_source_metadata'
_____________ test_unregistered_source_uses_safe_default_metadata _____________
E           AttributeError: 'RAGEngine' object has no attribute '_get_source_metadata'
____ test_indexed_and_retrieved_chunks_preserve_or_default_source_metadata ____
E           AttributeError: 'RAGEngine' object has no attribute 'register_source_metadata'

=========================== short test summary info ===========================
FAILED test_rag_engine.py::test_register_source_metadata_normalizes_key_and_persists_contract
FAILED test_rag_engine.py::test_register_source_metadata_rejects_verified_non_official
FAILED test_rag_engine.py::test_unregistered_source_uses_safe_default_metadata
FAILED test_rag_engine.py::test_indexed_and_retrieved_chunks_preserve_or_default_source_metadata
4 failed, 3 passed in 0.29s
```

### 2. GREEN 階段測試輸出

在 `rag_engine.py` 完成最小實作後，重新執行 `pytest -q test_rag_engine.py`，專屬測試 7 passed 綠燈通過：

```shell
$ pytest -q test_rag_engine.py
.......                                                                  [100%]
7 passed in 0.24s
```

---

## 四、 範疇控制與未變動說明

- **修改檔案**：僅修改 `rag_engine.py`、`test_rag_engine.py`、`.gitignore` 及本報告 `report-agy-010.md`。
- **未變動檔案**：未修改 `app.py`、`utils.py`、`ingest_pipeline.py`、README、任何提示詞檔、設定檔或 `docs/` 既有檔案。
- **無實體 Manifest 提交**：測試完全於 `tempfile.TemporaryDirectory()` 中進行，未在專案 `docs/` 留下實體 `manifest.json`。

---

## 五、 驗證指令執行結果

### 1. 全套 `pytest -q` 執行結果
全套 27 項測試（含既有 23 項及新增 4 項）全數綠燈通過：

```shell
$ pytest -q
...........................                                              [100%]
27 passed in 0.54s
```

### 2. `git diff --check` 執行結果
離退碼為 0，無任何格式或空白錯誤。實際指令輸出包含 Git LF/CRLF 換行符號轉換提示訊息：

```shell
$ git diff --check
warning: in the working copy of '.gitignore', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'rag_engine.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'test_rag_engine.py', LF will be replaced by CRLF the next time Git touches it
```

### 3. `git status` 執行結果
```shell
$ git status
On branch main
Changes not staged for commit:
	modified:   .gitignore
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
	modified:   rag_engine.py
	modified:   test_rag_engine.py
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
	.codex-orchestration/reports/report-agy-0010.md
	test_app_ui_wording.py
	test_response_contract.py
	test_safety_contract.py
```

---

*任務 0010 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
