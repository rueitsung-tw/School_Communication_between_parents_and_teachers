# 報告 agy-0005：將 NVC 四步驟落實至所有 Type B 回覆模組（退回補正二次修正版）

**執行任務 ID**：0005
**執行步驟**：唯一步驟 — 更新 README.md 與 11 個 Type B 提示詞模組之 NVC 四步驟內部寫作流程與自然段落表達（退回補正版）
**執行者**：agy
**執行日期**：2026-08-22

---

## 一、 摘要與執行範疇說明

本報告記錄任務 0005 之執行與補正結果。依據派工單 `.codex-orchestration/codex-task-dispatch.md` 與計畫 `.codex-orchestration/plans/plan-0005.md`，本任務將 `README.md` 及 `prompts/` 目錄下全數 11 個 Type B 回覆生成模組，統一將非暴力溝通（NVC）「觀察、感受、需要、請求」轉換為內部寫作思維與步驟，並嚴格規定呈顯給家長時融合為半正式、溫暖、具呼吸感之自然段落。

本任務嚴格遵守權限界線，**僅修改 `README.md`、`prompts/*.md` 與本報告 `report-agy-0005.md`**。未修改任何 Type A 提示詞、Python 程式（`app.py` / `utils.py`）、測試檔（`test_*.py`）、`theme_taxonomy.md`、`research_D_legal.md` 或 `docs/` 文件。

---

## 二、 審查退回小範圍補正修正細節

依據 Codex 複審退回指示，本次完成了以下三項針對性補正：

1. **通用 Type B 用途摘要更正**：
   - 於 `prompts/00_通用_TypeB_回覆草稿生成器.md` 第 3 行用途說明中，將舊有「符合三段式結構」之寫法更正為「將 NVC 四步驟內化為自然段落之回覆草稿」，達到全文邏輯完全一致。

2. **校園安全 Type B 感受步驟中性化**：
   - 於 `prompts/07_校園安全與意外事故.md` Type B「感受」步驟中，刪除將家長「自責」當作既定心理狀態之表述，改為「深深同理家長心疼孩子受傷與擔憂的情緒，接住對方焦慮，不得擅自預設或推定家長自責等未提及之心理狀態」。

3. **報告標題繁體化與補正紀錄**：
   - 將本報告標題之「回覆模组」更正為繁體「回覆模組」，並記錄補正與全套驗證結果。

---

## 三、 NVC 四步驟內部化與自然段落設計規範

### 1. NVC 內部寫作四步驟（AI 寫作核心原則）
- **觀察（Observation）**：客觀說明已知／已確認事實與已採取之措施。未經雙方確認之事項承諾查證說明，絕對不可隨意捏造過程、盲目猜測或無條件承諾過失過錯。
- **感受（Feeling）**：真誠同理家長合理的擔心、焦慮或心疼，接住對方情緒，但不替家長診斷、貼標籤、誇大其情緒或擅自預設其心理狀態（如預設自責）。
- **需要（Need）**：回應本次對話中可辨識的核心需要（如孩子安全受保護、學習獲支持、資訊透明、被尊重知情、親師合作等）。
- **請求／下一步（Request / Action）**：提出具體、可行且可邀請家長共同合作的下一步；最好是「邀請」而非冷漠告知，且不得私下承諾未確認之調查結論、處分或法律責任。

### 2. 對家長呈顯之自然段落規範
- 將上述 NVC 四步驟自然融合為 2～3 段溫暖、半正式且具呼吸感的連貫內文。
- **絕對禁止對家長輸出「觀察」、「感受」、「需要」、「請求」等標題、學術術語或「1. 2. 3.」／「•」條列清單**。

---

## 四、 逐檔變更明細

| 檔案名稱 | 變更區塊 | 修改內容與自然段落處置 |
|---|---|---|
| `README.md` | 理論基礎與使用指南 | 修正 NVC 說明為內部寫作四步驟（觀察、感受、需要、請求），明確補充對家長呈顯時融合為自然流暢段落，避免機械標題或條列。 |
| `00_通用_TypeB_回覆草稿生成器.md` | 用途摘要與 Type B 提示詞 | 1. 用途摘要更正為 NVC 四步驟內化與自然段落表達。<br>2. 提示詞內化 NVC 四步驟規範與自然段落呈現規範。 |
| `01_座位安排與班級經營.md` | Type B 提示詞 code block | 內化 NVC 四步驟，保持同理視力與專注需要、保留地雷句「座位是公平輪換，每個人都一樣」提醒，並規範 2~3 段自然段落。 |
| `02_成績評量與學習表現.md` | Type B 提示詞 code block | 內化 NVC 四步驟，回應化解認知失調、保留地雷句「分數就是這樣算的，你去看評量標準」提醒，規範自然段落呈現。 |
| `03_同儕衝突與霸凌處理.md` | Type B 提示詞 code block | 內化 NVC 四步驟，規範觀察不私下定性霸凌、保留地雷句「小孩子打打鬧鬧很正常」提醒、引導生對生調和與法定程序，規範自然段落。 |
| `04_管教方式與獎懲制度.md` | Type B 提示詞 code block | 內化 NVC 四步驟，說明管教教育用意與客觀事由但不宣稱無條件免責、保留地雷句「如果不罰，班上秩序怎麼維持？」提醒，規範自然段落。 |
| `05_作業量與課業壓力.md` | Type B 提示詞 code block | 內化 NVC 四步驟，同理陪讀情緒勞動、保留地雷句「別人都寫得完，是不是你們家沒有盯？」提醒，結合 SFBT 彈性解方與自然段落。 |
| `06_特殊生權益與融合教育.md` | Type B 提示詞 code block | 內化 NVC 四步驟，區分特殊生/一般生家長需求、保留地雷句「要不要考慮轉班」與「你要多包容」提醒，規範自然段落。 |
| `07_校園安全與意外事故.md` | Type B 提示詞 code block | 內化 NVC 四步驟，中性同理心疼與焦慮不擅自預設自責、說明受傷狀況與關懷不盲目承諾法律責任過失、保留地雷句「小孩子跑跑跳跳難免受傷」提醒，規範自然段落。 |
| `08_生活照顧與責任邊界.md` | Type B 提示詞 code block | 內化 NVC 四步驟，引導獨立自理能力、保留地雷句「我一個人要顧這麼多小孩沒辦法特別照顧」提醒，劃清界線並規範自然段落。 |
| `09_班費使用與行政事務.md` | Type B 提示詞 code block | 內化 NVC 四步驟，說明財務透明與資訊公開、保留地雷句「這沒多少錢不用計較」提醒，規範自然段落。 |
| `10_LINE群組溝通禮儀與界線.md` | Type B 提示詞 code block | 內化 NVC 四步驟，群組穩定情緒與個資保護、保留地雷句「絕對不能在群組裡跟家長公開爭論」提醒、引導轉私訊面談與自然段落。 |

---

## 五、 未變動檔案與範疇說明

1. **所有 Type A 提示詞**（含 `00_通用_TypeA_家長訊息分析器.md` 及各主題 Type A 區塊）：未作任何修改，維持既有情緒與冰山分析邏輯。
2. **Python 程式**（`app.py`、`utils.py`、`rag_engine.py`）：未作任何修改。
3. **測試檔案**（`test_prompts_loader.py`、`test_safety_contract.py`）：未作任何修改。
4. **`theme_taxonomy.md`、`research_D_legal.md`、`docs/`**：未作任何修改。

---

## 六、 驗證指令執行結果

### 1. `pytest -q` 執行結果
全套 13 項測試全數綠燈通過：

```shell
$ pytest -q
.............                                                            [100%]
13 passed in 0.52s
```

### 2. `git diff --check` 執行結果
```shell
$ git diff --check
(離退碼: 0，無任何空白或格式錯誤)
```

### 3. `git status` 執行結果
```shell
$ git status
On branch main
Changes not staged for commit:
	modified:   README.md
	modified:   prompts/00_通用_TypeB_回覆草稿生成器.md
	modified:   prompts/01_座位安排與班級經營.md
	modified:   prompts/02_成績評量與學習表現.md
	modified:   prompts/03_同儕衝突與霸凌處理.md
	modified:   prompts/04_管教方式與獎懲制度.md
	modified:   prompts/05_作業量與課業壓力.md
	modified:   prompts/06_特殊生權益與融合教育.md
	modified:   prompts/07_校園安全與意外事故.md
	modified:   prompts/08_生活照顧與責任邊界.md
	modified:   prompts/09_班費使用與行政事務.md
	modified:   prompts/10_LINE群組溝通禮儀與界線.md

Untracked files:
	.codex-orchestration/reports/report-agy-0002.md
	.codex-orchestration/reports/report-agy-0003.md
	.codex-orchestration/reports/report-agy-0004.md
	.codex-orchestration/reports/report-agy-0005.md
	test_safety_contract.py
```

---

*任務 0005 補正執行完畢，報告已覆寫，停止執行，等待 Codex 審查。*
