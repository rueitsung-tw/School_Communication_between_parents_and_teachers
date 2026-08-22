# 報告 agy-0013：00 通用主題安全 Fallback 與提示詞保護機制

**執行任務 ID**：0013  
**執行步驟**：Task 1 — 未涵蓋主題安全降級 UI 與通用提示詞保護機制實作  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0013.md` 與派工單要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0013.md`
- [x] 3. `.codex-orchestration/reports/report-agy-0009.md`
- [x] 4. `.codex-orchestration/reports/report-agy-0012.md`
- [x] 5. `app.py`
- [x] 6. `test_app_ui_wording.py`
- [x] 7. `test_safety_contract.py`

---

## 二、 實作內容與規則對照

1. **未涵蓋主題安全模式 UI 提示（`app.py`）**：
   - 當使用者選擇 `selected_theme_key == "00_通用"` 時，於主題下拉選單下方自動以 `st.info()` 顯示明確安全告示：
     > `ℹ️ **【未涵蓋主題安全模式】**：未在 10 項專用主題中的議題（例如性別平等、霸凌、校安、特殊個案等），系統預設切換為「00 通用親師溝通」安全模式處理。涉及「校園性別事件」、「霸凌防制」、「兒少保護」等高風險情境，僅提供同理關懷溝通草稿，絕不替代「學校法定通報與權責程序」。`
   - 不實作任何文字或模型自動分類，維持管理者與教師手動選擇。

2. **精確通用提示詞搜尋（`app.py`）**：
   - 將原提示詞比對邏輯修正為僅匹配 key 中明確包含 `"00_通用"` 之提示詞檔案（`if "00_通用" in k:`），避免誤讀取非通用主題提示詞。

3. **通用提示詞缺失保護斷路器（`app.py`）**：
   - 在 Type A 需求分析按鈕與 Type B 回覆草稿生成按鈕的兩條 API 呼叫分支最前端，加入完全相同的保護條件：
     `if selected_theme_key == "00_通用" and (not system_prompt_a or not system_prompt_b):`
   - 當通用 Type A 或 Type B 任一提示詞無法載入時，直接中斷執行並顯示指定錯誤訊息：
     > `❌ 無法載入通用安全提示詞（Type A 或 Type B 載入失敗），系統已啟動安全保護機制中斷 API 呼叫，禁止無安全提示詞呼叫 API。請檢查 prompts/00_通用_*.md 檔案。`
   - 確保在此極限保護下，任何 API 呼叫（`utils.call_llm_api()`）均無法發出。

---

## 三、 TDD 執行證據（RED & GREEN）

### 1. RED 階段測試輸出

在未修改 `app.py` 前，先於 `test_app_ui_wording.py` 新增 `test_app_ui_fallback_mode_and_prompt_guards` 靜態契約測試，執行 `pytest -q test_app_ui_wording.py test_safety_contract.py`，觸發符合預期之失敗：

```shell
...F....                                                                 [100%]
=================================== FAILURES ===================================
_________________ test_app_ui_fallback_mode_and_prompt_guards _________________

    def test_app_ui_fallback_mode_and_prompt_guards():
        app_path = os.path.join(os.path.dirname(__file__), "app.py")
        assert os.path.exists(app_path), "app.py 檔案不存在"

        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()

>       assert "【未涵蓋主題安全模式】" in content
E       AssertionError: assert '【未涵蓋主題安全模式】' in 'import os\n...'

test_app_ui_wording.py:64: AssertionError
=========================== short test summary info ============================
FAILED test_app_ui_wording.py::test_app_ui_fallback_mode_and_prompt_guards - AssertionError: assert '【未涵蓋主題安全模式】' in '...'
1 failed, 7 passed in 0.35s
```

### 2. GREEN 階段測試輸出

在 `app.py` 加入安全模式提示語、`"00_通用"` 提示詞搜尋過濾及兩條按鈕 API 斷路器後，重新執行 `pytest -q test_app_ui_wording.py test_safety_contract.py`，8 項測試全數綠燈通過：

```shell
........                                                                 [100%]
8 passed in 0.22s
```

---

## 四、 範疇控制與未變動說明

- **修改檔案**：僅修改 `app.py`、`test_app_ui_wording.py` 與本報告 `report-agy-0013.md`。
- **未變動檔案**：未修改 `utils.py`、`rag_engine.py`、`ingest_pipeline.py`、README、`config.json`、`requirements.txt`、`.gitignore`、`test_safety_contract.py`、`test_rag_engine.py`、提示詞檔案或 `docs/`／`.chromadb/` 實體資料庫。
- **未擴大範圍**：未執行任務 0014，未開啟主題提示詞或資料庫內容修改。

---

## 五、 驗證指令執行結果（逐字完整輸出）

### 1. 專屬測試 `pytest -q test_app_ui_wording.py test_safety_contract.py`
```shell
........                                                                 [100%]
8 passed in 0.22s
```

### 2. 全套測試 `pytest -q`
```shell
..................................                                       [100%]
34 passed in 0.54s
```

### 3. `git diff --check`
離退碼為 0，無格式或尾端空白錯誤：

```shell
warning: in the working copy of 'app.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'test_app_ui_wording.py', LF will be replaced by CRLF the next time Git touches it
```

### 4. `git status --short`
僅顯示 allowlist 允許之變更檔案：

```shell
 M app.py
 M test_app_ui_wording.py
```

---

*任務 0013 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
