# 報告 agy-0014：RAG 來源信任與未涵蓋主題安全降級全系統整合驗收報告

**執行任務 ID**：0014  
**執行步驟**：Task 1 — 不改碼系統全套自動化驗收與人工 Windows UI 驗收清單交付  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0014.md` 與派工單要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0014.md`
- [x] 3. `.codex-orchestration/reports/report-agy-0009.md`
- [x] 4. `.codex-orchestration/reports/report-agy-0010.md`
- [x] 5. `.codex-orchestration/reports/report-agy-0011.md`
- [x] 6. `.codex-orchestration/reports/report-agy-0012.md`
- [x] 7. `.codex-orchestration/reports/report-agy-0013.md`
- [x] 8. `app.py`、`utils.py`、`rag_engine.py`
- [x] 9. 所有測試檔案：
  - [x] `test_app_ui_wording.py`
  - [x] `test_ingest_pipeline.py`
  - [x] `test_prompts_loader.py`
  - [x] `test_rag_engine.py`
  - [x] `test_response_contract.py`
  - [x] `test_safety_contract.py`

---

## 二、 命令執行與逐字結果（無省略）

### 1. `python -m py_compile app.py utils.py rag_engine.py`
- **離退碼 (Exit Code)**：`0`
- **標準輸出與錯誤**：
```shell
$ python -m py_compile app.py utils.py rag_engine.py
(無輸出，語法檢查無誤通過)
```

### 2. `pytest -q`
- **離退碼 (Exit Code)**：`0`
- **逐字完整輸出**：
```shell
..................................                                       [100%]
34 passed in 0.54s
```

### 3. `git diff --check`
- **離退碼 (Exit Code)**：`0`
- **標準輸出與錯誤**：
```shell
$ git diff --check
(無輸出，無任何格式或尾端空白錯誤)
```

### 4. `git status --short`
- **離退碼 (Exit Code)**：`0`
- **逐字完整輸出**：
```shell
?? .codex-orchestration/reports/report-agy-0014.md
```

---

## 三、 範疇控制與未改動說明

- **新增/修改檔案**：僅建立本驗收報告檔案 `.codex-orchestration/reports/report-agy-0014.md`。
- **未改動檔案**：
  - 核心程式碼：未修改 `app.py`、`utils.py`、`rag_engine.py`、`ingest_pipeline.py`。
  - 測試檔：未修改 6 項 `test_*.py` 測試。
  - 設定與提示詞：未修改 `config.json`、`requirements.txt`、`.gitignore`、README、11 份 `prompts/` 提示詞檔、`theme_taxonomy.md` 及 `research_D_legal.md`。
  - 資料庫與文件：未建立或修改 `docs/manifest.json` 或 `.chromadb/` 實體向量庫資料。

---

## 四、 人工 Windows UI 驗收清單

為利後續在 Windows 環境執行 Streamlit 操作手動驗收，提供以下標準測試步驟與預期結果：

1. **檔案上傳來源分級與索引**：
   - 啟動 UI 並登入管理者主控台，切換至「📤 上傳檔案」。
   - 分別測試選擇 `official`（官方規章/已核定）、`teacher_case`（教師個案/未核定）及 `external_unverified`（外部資料/待人工確認）上傳 `.md` 或 `.pdf` 檔。
   - 點擊「📥 儲存檔案並更新索引」，確認介面顯示成功訊息，且背景安全登記 metadata 成功後引發向量化索引。

2. **網址抓取強制外部未核定**：
   - 切換至「🌐 輸入網址」分頁，輸入公開網頁 URL 點擊抓取。
   - 確認網頁寫入 `target_path` 後自動標記為 `external_unverified / web_crawl / unverified`，介面上不提供任何升級為官方或教師個案之選項。

3. **RAG 查詢信任標示與教師檢視**：
   - 輸入測試訊息執行 Type A 需求分析或 Type B 草稿生成。
   - 點擊「📚 查看本次 AI 參考的知識庫依據」，確認呈現之檔名後皆包含清楚的信任等級與狀態（例如 `信任等級：官方規章｜狀態：已核定`）。
   - 檢視系統送出給 LLM 之 Prompt（例如 via 測試日誌或串接），確認包含 `【官方規章參考（可作為一般規範依據）】` 等對應 Trust Badge。

4. **`00_通用` 主題安全模式與斷路器驗證**：
   - 於親師溝通主題下拉選單選擇「00 通用親師溝通情境」。
   - 確認選單下方跳出藍框 `st.info()` 告示，內容包含 `【未涵蓋主題安全模式】`、`校園性別事件`、`霸凌防制`、`兒少保護` 及 `學校法定通報與權責程序`。
   - **斷路器測試**：若暫時重命名 `prompts/00_通用_*.md` 檔案，分別點擊 Type A 及 Type B 執行按鈕，確認彈出紅框 `st.error()` 警告並完全中斷 API 呼叫，復原檔名後恢復正常運行。

---

*任務 0014 最終整合驗收報告已完成，無修改任何專案程式碼，停止執行，等待 Codex 最終結案。*
