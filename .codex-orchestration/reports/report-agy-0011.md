# 報告 agy-0011：管理端新增來源分級登記與重新索引觸發

**執行任務 ID**：0011  
**執行步驟**：Task 1 — 管理端新增來源分級 UI 與可靠重新索引觸發實作  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0011.md` 與派工單要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0011.md`
- [x] 3. `.codex-orchestration/reports/report-agy-0009.md`
- [x] 4. `.codex-orchestration/reports/report-agy-0010.md`
- [x] 5. `app.py`
- [x] 6. `rag_engine.py`
- [x] 7. `utils.py`
- [x] 8. `test_app_ui_wording.py`
- [x] 9. `test_rag_engine.py`
- [x] 10. `test_safety_contract.py`

---

## 二、 實作內容與規則對照

1. **管理員檔案上傳分級 UI（`app.py`）**：
   - 於管理員選單「📤 上傳檔案」區塊中新增 `st.selectbox`（key為 `"rag_upload_trust_level"`），提供三種選項：
     - `"official"` → 顯示「官方規章（已核定）」，對應 `author_type="school_admin"`, `verified_status="verified"`
     - `"teacher_case"` → 顯示「教師個案／經驗（未核定）」，對應 `author_type="teacher"`, `verified_status="unverified"`
     - `"external_unverified"` → 顯示「外部資料（待人工確認）」，對應 `author_type="teacher"`, `verified_status="unverified"`
   - 新增警語提示：個案經驗與外部資料僅供溝通參考，不可作為現行個案事實或法規依據。
   - 上傳成功時呼叫 `rag.register_source_metadata()` 進行登記；僅在所有檔案皆登記成功（`saved_count > 0`）時才進行 `rag._sync_index()`，若登記失敗顯不呼叫同步並輸出錯誤訊息。

2. **網址抓取強制外部未核定（`app.py`）**：
   - 於「🌐 輸入網址」成功寫入 `target_path` 後、既有 `_sync_index()` 前，強制呼叫 `rag.register_source_metadata(source_fpath=target_path, trust_level="external_unverified", author_type="web_crawl", verified_status="unverified", source_url=input_url.strip())`。
   - 網址不提供人工升級入口，固定為外部未核定資料。登記失敗時輸出錯誤且不執行同步。

3. **重新索引觸發與指紋失效（`rag_engine.py`）**：
   - 於 `register_source_metadata()` 原子寫入 `manifest.json` 成功後、傳回 `True` 前，新增 `self._index_fingerprints.pop(normalize_path(source_fpath), None)`。
   - 效果：成功登記後使該來源檔案之舊索引指紋失效，隨後執行的 `rag._sync_index()` 能偵測變更並自動刪除舊 chunk、以最新 manifest metadata 重新寫入 ChromaDB，過程無需重新跑摘要或呼叫 LLM 模型。

---

## 三、 TDD 執行證據（RED & GREEN）

### 1. RED 階段測試輸出

在未修改 `app.py` 與 `rag_engine.py` 前，先於 `test_rag_engine.py` 新增指紋失效測試、於 `test_app_ui_wording.py` 新增 UI 契約測試，執行 `pytest -q test_rag_engine.py test_app_ui_wording.py`，確認符合預期失敗：

```shell
$ pytest -q test_rag_engine.py test_app_ui_wording.py
........F.F                                                              [100%]
================================== FAILURES ===================================
______ test_register_source_metadata_invalidates_only_index_fingerprint _______
E           AssertionError: assert 'C:\\...\\new-source.md' not in {'C:\\...\\new-source.md': 'old-index-fingerprint'}
____________ test_app_ui_admin_panel_has_source_trust_registration ____________
E       assert 'key="rag_upload_trust_level"' in 'with tab_file:\n ...'
=========================== short test summary info ===========================
FAILED test_rag_engine.py::test_register_source_metadata_invalidates_only_index_fingerprint
FAILED test_app_ui_wording.py::test_app_ui_admin_panel_has_source_trust_registration
2 failed, 9 passed in 0.36s
```

### 2. GREEN 階段測試輸出

在 `rag_engine.py` 與 `app.py` 完成實作後，重新執行 `pytest -q test_rag_engine.py test_app_ui_wording.py`，專屬測試 11 passed 綠燈通過：

```shell
$ pytest -q test_rag_engine.py test_app_ui_wording.py
...........                                                              [100%]
11 passed in 0.24s
```

---

## 四、 範疇控制與未變動說明

- **修改檔案**：僅修改 `app.py`、`rag_engine.py`、`test_app_ui_wording.py`、`test_rag_engine.py` 與本報告 `report-agy-0011.md`。
- **未變動檔案**：未修改 `utils.py`、`ingest_pipeline.py`、README、`config.json`、`requirements.txt`、`.gitignore`、提示詞檔或 `docs/`／`.chromadb/` 實體資料庫。
- **未擴大範圍**：未實作 Trust Badges 輸出、RAG Prompt 邊界、`00_通用` fallback 或主題分類。
- **無實體 Manifest 提交**：測試完全於 `tempfile.TemporaryDirectory()` 中進行，未在專案 `docs/` 留下實體 `manifest.json`。

---

## 五、 驗證指令執行結果

### 1. 全套 `pytest -q` 執行結果
全套 29 項測試（含既有與新增）全數綠燈通過：

```shell
$ pytest -q
.............................                                            [100%]
29 passed in 0.53s
```

### 2. `git diff --check` 執行結果
離退碼為 0，無任何格式或空白錯誤。實際指令輸出包含 Git LF/CRLF 換行符號轉換提示訊息：

```shell
$ git diff --check
warning: in the working copy of 'app.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'rag_engine.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'test_app_ui_wording.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'test_rag_engine.py', LF will be replaced by CRLF the next time Git touches it
```

### 3. `git status --short` 實際執行結果
僅顯示 allowlist 所列修改之 4 份程式與測試檔案：

```shell
$ git status --short
 M app.py
 M rag_engine.py
 M test_app_ui_wording.py
 M test_rag_engine.py
```

---

*任務 0011 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
