# 報告 agy-0008：修正 Type B 範例中的未確認事實與處置敘述

**執行任務 ID**：0008  
**執行步驟**：唯一步驟 — 修訂 11 份 Type B 提示詞「使用範例」，消除無來源事實捏造，改為條件式查證與客觀溝通  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 必讀檔案與順序勾列清單

依據計畫 `plan-0008.md` 要求，本任務執行前已依序完整讀取以下檔案：

- [x] 1. `.codex-orchestration/codex-task-dispatch.md`
- [x] 2. `.codex-orchestration/plans/plan-0008.md`
- [x] 3. `utils.py`（包含 `SAFETY_CORE` 常數與 `compose_system_prompt`）
- [x] 4. `README.md`
- [x] 5. `prompts/00_通用_TypeB_回覆草稿生成器.md`
- [x] 6. `prompts/01_座位安排與班級經營.md`
- [x] 7. `prompts/02_成績評量與學習表現.md`
- [x] 8. `prompts/03_同儕衝突與霸凌處理.md`
- [x] 9. `prompts/04_管教方式與獎懲制度.md`
- [x] 10. `prompts/05_作業量與課業壓力.md`
- [x] 11. `prompts/06_特殊生權益與融合教育.md`
- [x] 12. `prompts/07_校園安全與意外事故.md`
- [x] 13. `prompts/08_生活照顧與責任邊界.md`
- [x] 14. `prompts/09_班費使用與行政事務.md`
- [x] 15. `prompts/10_LINE群組溝通禮儀與界線.md`
- [x] 16. `.codex-orchestration/reports/report-agy-0004.md`
- [x] 17. `.codex-orchestration/reports/report-agy-0007.md`

---

## 二、 摘要與執行範疇說明

本報告記錄任務 0008 之執行結果。本任務審視並修訂全數 11 份 Type B 提示詞中的「使用範例／期待的回覆草稿輸出風格」，確保範例回覆嚴格遵循 `SAFETY_CORE` 事實邊界原則：只陳述輸入訊息或教師補充背景中已確認的事實。對於未經證實之教師過往行動、事件具體細節、過失過錯、處分結論或未確認保證，一律更正為「條件式查證、後續說明與客觀溝通」表述。

本任務嚴格遵守權限界線，**僅修改 `prompts/` 下 11 份檔案之 Type B 使用範例，以及本報告 `report-agy-0008.md`**。未修改任何 Type A 提示詞、Type B 提示詞規範、Python 程式（`app.py` / `utils.py`）、測試檔（`test_*.py`）、`README.md`、`theme_taxonomy.md`、`research_D_legal.md` 或 `docs/` 文件。

---

## 三、 全數 11 份 Type B 範例修訂前後對照表

| 檔案名稱 | 修改前無來源／過度承諾敘述 | 修改後條件式／有來源表述 |
|---|---|---|
| `00_通用_TypeB_回覆草稿生成器.md` | 「我當時有請全班協尋...」（未於教師背景提供） | 「我會找時間私下向小明了解當時彩色筆遺失的情形，也會協助他在班上找找看，釐清狀況後再跟您說明。」 |
| `01_座位安排與班級經營.md` | 「我觀察到弟弟最近在課堂上很願意發表意見...弟弟其實很有耐心，常常能發揮穩定對方的作用。」（捏造過去未提供之學生行為細節） | 「這次的座位安排主要是參考全班定期輪換與課堂分組...同桌互動的部分，我也會在課堂中特別關注兩位孩子的相處與學習專注度。」 |
| `02_成績評量與學習表現.md` | 「我在改考卷時發現，妹妹在基礎的字詞部分掌握得非常好...可能因為緊張而沒有把題目看完就作答了...」（捏造未提供之改卷診斷細節） | 「這次的國語測驗題型確實比較靈活。我會再跟妹妹一起核對這份考卷，了解她是在哪個題型卡關，並重新檢視相關細節與評量標準。」 |
| `03_同儕衝突與霸凌處理.md` | 「今天下午我有注意到擦傷...他跟我說是不小心跌倒的，所以我先幫他做了簡單包紮...並且請他鄭重向小明道歉。」（捏造過往處置行動與承諾道歉結論） | 「明天一早到校後，我會立刻啟動了解與釐清程序，分別向小明與大華關心當時的情形...若釐清經過後確有推倒受傷或長期不當對待的情事，學校與導師一定會依規定積極處理並進行關懷輔導...」 |
| `04_管教方式與獎懲制度.md` | 「其實是因為哥哥在課堂上已經連續幾次轉過去聊天...我當下提醒了他兩次...請您放心，我還是有讓他去喝水和上廁所的。」（捏造課堂管教經過細節） | 「關於今天課堂上的輔導管教狀況，當下主要考量是提醒孩子課堂專注與維護上課常規...明天我會找時間與哥哥單獨聊聊，聽聽他的想法並說明老師的用心。」 |
| `05_作業量與課業壓力.md` | 說明指派作業學習初衷，並提出「超過九點請讓孩子休息，簽名註記即可」之焦點解決彈性解方（原本即符合規範，保持清晰溝通） | 保持 NVC 自然段落、同理陪伴辛苦與提供彈性微調解方。 |
| `06_特殊生權益與融合教育.md` | 「我們已經啟動了輔導機制的協助，有特教老師和輔導老師一起介入幫忙。」（捏造未經證實之特教與輔導介入程序） | 「我會在課堂上微調座位與教學引導，並向校內相關輔導資源諮詢合適的協助方式，盡力維護安穩的課堂學習秩序...」 |
| `07_校園安全與意外事故.md` | 「剛剛我已經先聯繫了體育老師與健康中心，了解到當時因為班上正好在進行分組測驗...我為這點疏忽對您感到抱歉。」（捏造事發原因與坦承法律責任過失） | 「明天一早到校後，我會立刻與體育老師及當時上課狀況進行全面了解，釐清事發經過與當時的處置情形...明天早上小寶一到校，我會關心他的狀況，並陪同他至健康中心由護理師重新檢查與妥善處理...」 |
| `08_生活照顧與責任邊界.md` | 說明導師於全班常規提醒之作法，並引導孩子自我照顧與親師放手（原本即符合規範，保持清晰溝通） | 保持 NVC 自然段落、肯定家長愛護與引導學生自理能力。 |
| `09_班費使用與行政事務.md` | 「這學期的班費收支明細我都已經整理好了，原本預計這週五會統一發下去給所有家長過目。我晚點先拍一份明細的照片傳給您...」（捏造整理進度與發放承諾） | 「班級費用的使用原則必須維持公開透明。相關費用與收支細節，班上都會依規定妥善紀錄與報核。我會整理並公布本次材料費與班費的最新明細供家長參閱。」 |
| `10_LINE群組溝通禮儀與界線.md` | 群組中表達關切，並引導轉為私訊與隔日個別電話討論以保護個資（原本即符合規範，保持清晰溝通） | 保持 NVC 自然段落、穩健回應群組與保護學生隱私管道。 |

---

## 四、 未變動檔案與範疇說明

1. **所有 Type A 提示詞與 Type B 提示詞規範**：未作任何修改。
2. **Python 程式**（`app.py`、`utils.py`、`rag_engine.py`）：未作任何修改。
3. **測試檔案**（`test_prompts_loader.py`、`test_safety_contract.py`、`test_app_ui_wording.py`、`test_response_contract.py`）：未作任何修改。
4. **`README.md`、`theme_taxonomy.md`、`research_D_legal.md`、`docs/`**：未作任何修改。

---

## 五、 驗證指令執行結果

### 1. `pytest -q` 執行結果
全套 23 項測試全數綠燈通過：

```shell
$ pytest -q
.......................                                                  [100%]
23 passed in 0.52s
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
	modified:   app.py
	modified:   prompts/00_通用_TypeB_回覆草稿生成器.md
	modified:   prompts/01_座位安排與班級經營.md
	modified:   prompts/02_成績評量與學習表現.md
	modified:   prompts/03_同儕衝突與霸凌處理.md
	modified:   prompts/04_管教方式與獎懲制度.md
	modified:   prompts/06_特殊生權益與融合教育.md
	modified:   prompts/07_校園安全與意外事故.md
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
	test_app_ui_wording.py
	test_response_contract.py
	test_safety_contract.py
```

---

*任務 0008 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
