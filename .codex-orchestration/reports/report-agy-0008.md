# 報告 agy-0008：修正 Type B 範例中的未確認事實與處置敘述（退回補正版）

**執行任務 ID**：0008
**執行步驟**：唯一步驟 — 修訂 11 份 Type B 提示詞「使用範例」，消除無來源事實捏造，改為條件式查證與客觀溝通（退回補正版）
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

## 二、 摘要與退回補正細節說明

本報告記錄任務 0008 之執行與補正結果。本任務審視並修訂全數 11 份 Type B 提示詞中的「使用範例／期待的回覆草稿輸出風格」，確保範例回覆嚴格遵循 `SAFETY_CORE` 事實邊界原則：只陳述輸入訊息或教師補充背景中已確認的事實。對於未經證實之教師過往行動、事件具體細節、過失過錯、處分結論或未確認保證，一律更正為「條件式查證、後續說明與客觀溝通」表述。

### 退回補正修正重點：
1. **`01_座位安排與班級經營.md`**：移除未經範例輸入支持之「定期輪換與課堂分組」既定事實宣稱，更正為「關於這次座位安排與考量，我會再重新檢視並了解狀況」之條件式表述。
2. **`02_成績評量與學習表現.md`**：移除未經範例輸入支持之「題目確實比較靈活」既定事實宣稱，更正為「關於您提到的測驗難易度與扣分疑慮，我會再跟妹妹一起核對這份考卷並重新審視評量標準」之條件式表述。
3. **`04_管教方式與獎懲制度.md`**：移除將「當下主要考量」與「初衷始終是」作為既定動機之寫法，更正為「關於今天發生的狀況，我會再進一步向課堂相關人員與哥哥了解當時的完整經過，釐清事件原委」之條件式表述。
4. **`08_生活照顧與責任邊界.md`**：移除假定「在全班面前統一提醒」為已在實施做法之敘述，更正為「關於補充水分與增減衣物，我可以在全班面前統一提醒孩子們注意」之可邀請／可執行下一步表述。
5. **`09_班費使用與行政事務.md`**：移除預設園區材料費成因、班費原訂用途與既有報核事實之描述，更正為「對於您詢問的五十元材料費用途與班費餘額狀況，我會再重新核對與彙整本次戶外教學的收支項目」之條件式表述。
6. **尾端空白清理與驗證**：清除報告第 3 至 6 行及全檔之末端空白，確保 `git diff --check` 通過。

---

## 三、 全數 11 份 Type B 範例修訂前後對照表

| 檔案名稱 | 修改前無來源／過度承諾敘述 | 修改後條件式／有來源表述 |
|---|---|---|
| `00_通用_TypeB_回覆草稿生成器.md` | 「我當時有請全班協尋...」（未於教師背景提供） | 「我會找時間私下向小明了解當時彩色筆遺失的情形，也會協助他在班上找找看，釐清狀況後再跟您說明。」 |
| `01_座位安排與班級經營.md` | 「這次座位安排主要是參考全班定期輪換與課堂分組...」（未於輸入提供） | 「關於這次的座位安排與考量，我會再重新檢視並了解狀況。對於您提到的視力部分，我明天上課會特別觀察...」 |
| `02_成績評量與學習表現.md` | 「這次的國語測驗題型確實比較靈活...」（未於輸入提供） | 「關於您提到的測驗難易度與扣分疑慮，我會再跟妹妹一起核對這份考卷，了解她的作答情況並重新審視評量標準。」 |
| `03_同儕衝突與霸凌處理.md` | 「今天下午我有注意到擦傷...他跟我說是不小心跌倒的，所以我先幫他做了簡單包紮...並且請他鄭重向小明道歉。」（捏造過往處置行動與承諾道歉結論） | 「明天一早到校後，我會立刻啟動了解與釐清程序，分別向小明與大華關心當時的情形...若釐清經過後確有推倒受傷或長期不當對待的情事，學校與導師一定會依規定積極處理並進行關懷輔導...」 |
| `04_管教方式與獎懲制度.md` | 「當下主要考量是提醒孩子課堂專注...我的初衷始終是...」（將管教動機當作既定事實） | 「關於今天發生的狀況，我會再進一步向課堂相關人員與哥哥了解當時的完整經過，釐清事件原委與課堂暫停的考量...明天我會找時間與哥哥單獨聊聊...」 |
| `05_作業量與課業壓力.md` | 說明指派作業學習初衷，並提出「超過九點請讓孩子休息，簽名註記即可」之焦點解決彈性解方（原本即符合規範，保持清晰溝通） | 保持 NVC 自然段落、同理陪伴辛苦與提供彈性微調解方。 |
| `06_特殊生權益與融合教育.md` | 「我們已經啟動了輔導機制的協助，有特教老師和輔導老師一起介入幫忙。」（捏造未經證實之特教與輔導介入程序） | 「我會在課堂上微調座位與教學引導，並向校內相關輔導資源諮詢合適的協助方式，盡力維護安穩的課堂學習秩序...」 |
| `07_校園安全與意外事故.md` | 「剛剛我已經先聯繫了體育老師與健康中心，了解到當時因為班上正好在進行分組測驗...我為這點疏忽對您感到抱歉。」（捏造事發原因與坦承法律責任過失） | 「明天一早到校後，我會立刻與體育老師及當時上課狀況進行全面了解，釐清事發經過與當時的處置情形...明天早上小寶一到校，我會關心他的狀況，並陪同他至健康中心由護理師重新檢查與妥善處理...」 |
| `08_生活照顧與責任邊界.md` | 「在學校裡，我會時常在全班面前統一提醒孩子們要記得多喝水...」（將班級做法當成已在實施既定事實） | 「關於補充水分與增減衣物，我可以在全班面前統一提醒孩子們注意。因為小宇現在已經慢慢長大了...」 |
| `09_班費使用與行政事務.md` | 「這次五十元材料費主要是園區針對手作課程額外收取...相關費用與收支細節，班上都會依規定妥善紀錄與報核...」（將費用來源與報核事實當成已確認） | 「對於您詢問的五十元材料費用途與班費餘額狀況，我會再重新核對與彙整本次戶外教學的收支項目。班級費用的使用原則必須維持公開透明。我會整理本次材料費與班費的最新明細供您與家長參閱。」 |
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
離退碼為 0，無任何格式或空白錯誤。實際指令輸出包含 Git LF/CRLF 換行符號轉換提示訊息：

```shell
$ git diff --check
warning: in the working copy of '.codex-orchestration/reports/report-agy-0008.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'prompts/01_座位安排與班級經營.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'prompts/02_成績評量與學習表現.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'prompts/04_管教方式與獎懲制度.md', LF will be replaced by CRLF the next time Git touches it
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
	test_app_ui_wording.py
	test_response_contract.py
	test_safety_contract.py
```

---

*任務 0008 交付資訊更正完畢，報告已更新，停止執行，等待 Codex 最終複審。*
