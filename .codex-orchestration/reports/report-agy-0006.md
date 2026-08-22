# 報告 agy-0006：同步介面中的 NVC 四步驟說明

**執行任務 ID**：0006  
**執行步驟**：唯一步驟 — 更新 `app.py` 介面文案，消除舊「三段式」描述，並同步為 NVC 四步驟內部思維與自然段落表達  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 摘要與執行範疇說明

本報告記錄任務 0006 之 TDD 執行與介面文案同步結果。依據派工單 `.codex-orchestration/codex-task-dispatch.md` 與計畫 `.codex-orchestration/plans/plan-0006.md`，本任務將 `app.py` 中殘留的使用者可見舊文案（「三段式結構」及「同理 -> 事實 -> 解方」）全數更正，使其與 `README.md`、`theme_taxonomy.md` 及全數 11 個 Type B 提示詞模組完全一致。

本任務嚴格採 **TDD (Test-Driven Development)** 流程：
1. **RED 階段**：先建立獨立單元測試 `test_app_ui_wording.py`，專門檢查 `app.py` 中的 NVC 介面文案。在 `app.py` 未修改前執行 `pytest -q test_app_ui_wording.py`，獲得預期之 `AssertionError: app.py 仍包含舊版『三段式』文案` 失敗。
2. **GREEN 階段**：重構 `app.py` 中 4 處舊文案，將其更新為「將非暴力溝通（NVC）觀察、感受、需要、請求四步驟內化為自然段落」。測試全數綠燈通過。
3. **REFACTOR 與驗證**：確認 `pytest -q` 全套 14 項測試通過，且 `git diff --check` 為零錯誤。

本任務嚴格遵守權限界線，**僅修改 `app.py`，並新增 `test_app_ui_wording.py` 與本報告 `report-agy-0006.md`**。未修改 `utils.py`、RAG 引擎、模型呼叫邏輯、`README.md`、`prompts/*.md`、`theme_taxonomy.md`、`research_D_legal.md` 或 `docs/` 文件。

---

## 二、 `app.py` 介面文案更新對照表

| 位置 | 變更前舊文案 | 變更後新文案 |
|---|---|---|
| 側邊欄（通用主題提示 line 296） | `建議運用非暴力溝通三段式結構。` | `建議將非暴力溝通（NVC）觀察、感受、需要、請求四步驟內化為自然段落。` |
| 側邊欄（通用主題提示 line 298） | `建議運用非暴力溝通三段式結構。` | `建議將非暴力溝通（NVC）觀察、感受、需要、請求四步驟內化為自然段落。` |
| 兩階段生成注入訊息（line 479） | `...生成溫暖且符合非暴力溝通三段式結構的回覆草稿。` | `...將非暴力溝通（NVC）觀察、感受、需要、請求內化為自然段落，生成溫暖之回覆草稿。` |
| 草稿顯示說明卡（line 494） | `...已融合 Type A 冰山診斷與非暴力溝通三段式結構（同理 -> 事實 -> 解方）生成...` | `...已融合 Type A 冰山診斷與非暴力溝通（NVC）四步驟內部思維生成，以自然段落表達...` |

---

## 三、 TDD 測試證據

### 1. RED 階段測試失敗證據
在 `app.py` 尚未修訂舊文案前，執行 `pytest -q test_app_ui_wording.py` 獲得預期之 `AssertionError` 失敗：

```shell
$ pytest -q test_app_ui_wording.py
F                                                                        [100%]
================──────────────── FAILURES ────────────────────────────────
__________ test_app_ui_wording_has_no_obsolete_nvc_three_stage_text ___________

    def test_app_ui_wording_has_no_obsolete_nvc_three_stage_text():
        app_path = os.path.join(os.path.dirname(__file__), "app.py")
        assert os.path.exists(app_path), "app.py 檔案不存在"

        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. 介面文案不得再出現舊版「三段式」或「同理 -> 事實 -> 解方」字樣
>       assert "三段式" not in content, "app.py 仍包含舊版『三段式』文案"
E       AssertionError: app.py 仍包含舊版『三段式』文案

test_app_ui_wording.py:12: AssertionError
100% Failure - 1 failure in 0.28s
```

### 2. GREEN 階段與全套測試通過證據
在 `app.py` 完成 4 處文案更正後，執行 `pytest -q`（全套 14 項測試，含新增之 UI 文案測試）：

```shell
$ pytest -q test_app_ui_wording.py
.                                                                        [100%]
1 passed in 0.01s

$ pytest -q
..............                                                           [100%]
14 passed in 2.43s
```

---

## 四、 未變動檔案與範疇說明

1. **`utils.py` 及 LLM API 呼叫邏輯**：未作任何修改。
2. **Prompt 組裝與 Prompt 模組**（`prompts/*.md`）：未作任何修改。
3. **`README.md` 及 `theme_taxonomy.md`**：未作任何修改。
4. **RAG 引擎（`rag_engine.py`）與 `docs/` 文件**：未作任何修改。

---

## 五、 驗證指令執行結果

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

Untracked files:
	.codex-orchestration/reports/report-agy-0002.md
	.codex-orchestration/reports/report-agy-0003.md
	.codex-orchestration/reports/report-agy-0004.md
	.codex-orchestration/reports/report-agy-0005.md
	.codex-orchestration/reports/report-agy-0006.md
	test_app_ui_wording.py
	test_safety_contract.py
```

---

*任務 0006 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
