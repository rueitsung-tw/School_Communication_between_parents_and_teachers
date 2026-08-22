# 報告 agy-0007：建立 Type B 草稿格式品質關卡（退回補正二次修正版）

**執行任務 ID**：0007
**執行步驟**：唯一步驟 — 建立 Type B 草稿格式品質驗證器並整合至 `app.py` 顯示前品質關卡（退回補正版）
**執行者**：agy
**執行日期**：2026-08-22

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0007.md` 要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0007.md`
- [x] 3. `utils.py`（包含 `SAFETY_CORE`、`compose_system_prompt` 及匯入區）
- [x] 4. `app.py`（包含 Type B 生成按鈕、API 呼叫與 `response` 顯示區）
- [x] 5. `test_safety_contract.py`
- [x] 6. `test_app_ui_wording.py`
- [x] 7. `.codex-orchestration/reports/report-agy-0004.md`
- [x] 8. `.codex-orchestration/reports/report-agy-0005.md`
- [x] 9. `.codex-orchestration/reports/report-agy-0006.md`

---

## 二、 摘要與小範圍退回補正細節

本報告記錄任務 0007 之 TDD 執行、品質關卡實作與二次補正結果。

### 本次補正重點：
1. **補齊真正的符號條列測試**：
   - 於 `test_response_contract.py` 中新增 `test_validate_parent_reply_bullet_points_with_dash_and_bullet()` 測試案例，分別以真正的 `-`（連字號/減號）與 `•`（項目圓點符號）測試段首條列，確認能精準攔截並回傳條列違規原因。
2. **實作與驗證 NVC 括號標題變體**：
   - 於 `utils.py` 之 `validate_parent_reply` 強化正則表達式，並於 `test_response_contract.py` 中新增 `test_validate_parent_reply_visible_nvc_headers_with_brackets()` 測試案例，驗證 `【需要】`、`[請求]`、`【觀察】`、`[感受]` 等全/半形中英文括號標題變體皆被嚴格禁止。
3. **專屬測試與全套測試通過**：
   - 專屬測試 `test_response_contract.py` 共 9 項單元測試全數通過；全套 `pytest -q` 提升至 23 項測試全綠燈通過。

---

## 三、 `utils.validate_parent_reply` 純函式契約

```python
def validate_parent_reply(reply: str) -> List[str]:
    """
    純函式格式品質驗證契約：
    1. 空白內容檢查：若草稿為空或僅含空白，回傳違規原因。
    2. 段落數檢查：草稿須恰有 2 或 3 個以空白行分隔之非空段落。
    3. 可見 NVC 標題檢查：不得包含『觀察：』、『感受：』、『【需要】』、『[請求]』等段首或獨立標題及其全/半形括號變體。
    4. 條列或編號檢查：不得包含段首條列符號（-、*、•、◦、▪）或數字編號（1.、(1)、一、）。
    5. 不檢查、不改寫、不判定任何事實、情緒、法律責任或內容品質。
    回傳：違規原因清單 List[str]（合格時回傳 []）。
    """
```

---

## 四、 `app.py` 兩大 UI 分支行為

在 `app.py` 的 Type B 流程中，取得 API 回傳之 `response` 後：

1. **不合格分支（`validation_errors` 非空）**：
   - 僅顯示簡短警告 `st.warning("⚠️ 本次 AI 生成之草稿未符合格式品質規範（原因：...），未予顯示。請點擊按鈕重新生成。")`。
   - **絕對不顯示** 原不合格草稿、`st.success` 成功訊息、說明卡、複製提示及 `st.text_area` 編輯框。
2. **合格分支（`validation_errors` 為空）**：
   - 保持既有 UI 行為，正常顯示 `st.success("✅ 兩階段草稿生成完成！")`、`st.markdown` 標題、`st.info` 說明卡、`st.text_area` 編輯框及複製提示。

---

## 五、 TDD 測試證據

### 1. 專屬測試 `test_response_contract.py` 執行結果
```shell
$ pytest -q test_response_contract.py
.........                                                                [100%]
9 passed in 0.28s
```

### 2. 全套 `pytest -q` 執行結果
```shell
$ pytest -q
.......................                                                  [100%]
23 passed in 0.52s
```

---

## 六、 修改與新增檔案清單

| 檔案名稱 | 變更類型 | 說明 |
|---|---|---|
| `utils.py` | [MODIFY] | 實作並強化純函式 `validate_parent_reply`（包含括號標題變體與符號條列檢查） |
| `app.py` | [MODIFY] | 於 Type B 草稿顯示前加入 `validate_parent_reply` 品質關卡分流（本次補正未變動） |
| `test_response_contract.py` | [NEW] | 新增 Type B 草稿格式品質驗證單元測試（共 9 項單元測試，包含合格 2/3 段、空白、單/四段落、NVC 冒號標題、NVC 括號標題 `【需要】`/`[請求]`、數字編號及 `-`/`•` 符號條列） |
| `.codex-orchestration/reports/report-agy-0007.md` | [NEW] | 本任務執行報告（補正版） |

---

## 七、 未變動檔案與範疇說明

1. **`README.md` 及 `prompts/*.md`**：未作任何修改。
2. **`test_safety_contract.py` 及 `test_app_ui_wording.py`**：未作任何修改。
3. **法律與安全核心（`SAFETY_CORE` / `compose_system_prompt`）**：未作任何修改。
4. **模型呼叫流程、RAG 引擎（`rag_engine.py`）、`theme_taxonomy.md`、`docs/`**：未作任何修改。

---

## 八、 驗證指令執行結果

### 1. `git diff --check` 執行結果
```shell
$ git diff --check
(離退碼: 0，無任何空白或格式錯誤)
```

### 2. `git status` 執行結果
```shell
$ git status
On branch main
Changes not staged for commit:
	modified:   app.py
	modified:   utils.py

Untracked files:
	.codex-orchestration/reports/report-agy-0002.md
	.codex-orchestration/reports/report-agy-0003.md
	.codex-orchestration/reports/report-agy-0004.md
	.codex-orchestration/reports/report-agy-0005.md
	.codex-orchestration/reports/report-agy-0006.md
	.codex-orchestration/reports/report-agy-0007.md
	test_app_ui_wording.py
	test_response_contract.py
	test_safety_contract.py
```

---

*任務 0007 補正執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
