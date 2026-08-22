# 報告 agy-0002：更新法令研究基礎與可追溯法源

**執行任務 ID**：0002  
**執行步驟**：唯一步驟 — 更新 `research_D_legal.md` 法令研究基礎與可追溯法源  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 摘要與執行範疇說明

本報告記錄任務 0002 之執行結果。依據派工單 `.codex-orchestration/codex-task-dispatch.md` 與計畫 `.codex-orchestration/plans/plan-0002.md`，本任務將任務 0001 已核准之台灣教育法令更新，精準且保守地寫入 `research_D_legal.md`，作為後續親師溝通知識卡、RAG 與提示詞修改之法令研究基礎。

本任務嚴格遵守權限界線，**僅修改 `research_D_legal.md` 與本報告 `report-agy-0002.md`**，未修改任何提示詞、Python 程式、`README.md`、`theme_taxonomy.md`、`docs/` 或 RAG 索引。

---

## 二、 `research_D_legal.md` 修改章節與內容詳情

| 修改章節 | 修改前問題 | 修改後內容與條件化說明 |
|---|---|---|
| **首段與聲明** | 欠缺權限與適用範圍限制 | 新增「免責與適用聲明」，明確規範本報告僅作為親師溝通提示詞設計參考，不得作為個案處分或訴訟依據，具體個案應依事件發生時法規及校內法定程序辦理。 |
| **《校園霸凌防制準則》** | 未區分生對生/師對生適用範疇，欠缺 2024 新制令號與調和機制條件 | 1. 修正為 113.04.17 臺教學（五）字第 1132801790A 號令（113.04.19 生效）。<br>2. 引註正確條文：依第 5 條第 1 項、第 3 項及第 7 條第 1 項第 2 款但書，規範各級學校「生對生」霸凌事件依本準則處理；高級中等以下學校編制內專任教師對學生霸凌事件依《解聘辦法》調查處理，由校事會議負責。<br>3. 載明第 4 條第 8 款「調和程序」僅適用於生對生事件且須經雙方同意始得進行。 |
| **《校園性別事件防治準則》** | 名稱舊稱（性侵害性騷擾或性霸凌防治準則）、令號舊寫 | 1. 修正正確名稱為《校園性別事件防治準則》。<br>2. 修正官方令號為 **臺教學（三）字第 1132801024A 號令**（113.03.06 修正發布，03.08 生效）。<br>3. 增訂教職員工專業倫理紅線條款，並提醒性別事件應依法通報由校內性平會處理，不得由教師或 AI 自行定性。 |
| **《學校訂定教師輔導與管教學生辦法注意事項》** | 未記載 2024 年阻卻違法條件 | 1. 修正為 113.02.05 臺教學(五)字第 1132800502A 號函。<br>2. 增列教師正當防衛、緊急避難與處置危險物品等阻卻違法事由，並規範校園安全檢查流程與保密義務，同時註明此為合法處置事由，非無條件之一般免責聲明。 |
| **《教師法》** | 法條號碼標示錯誤（原誤標為第 16 條為義務） | 修正法條號碼：第 16 條規範教師專業自主等權利，第 32 條規範教師義務（恪遵師道、維護校譽等）。 |
| **《個人資料保護法》與《刑法》誹謗罪** | 個資與誹謗敘述過度絕對化（宣稱群組傳訊絕對違法） | 改為條件式風險提示：說明 LINE 群組傳送個資是否違法須評估《個資法》第 19 條及第 5 條比例原則；言論是否構成誹謗須視《刑法》第 310 條構成要件與第 310 條第 3 項/第 311 條免責要件，禁止斷言必然犯罪。 |
| **新增《教師解聘不續聘停聘或資遣辦法》** | 原檔欠缺高級中等以下學校師對生事件之專用法規 | 新增 113.04.17 修正發布（臺教學（三）字第 1132801646A 號令）之《高級中等以下學校教師解聘不續聘停聘或資遣辦法》，作為高級中等以下學校師對生霸凌/不當管教之調查程序依據。 |

---

## 三、 每一項法源之官方一手 URL

1. **《教育基本法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020045&flno=8](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020045&flno=8)
2. **《兒童及少年福利與權益保障法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=53](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=53) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=100](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=100)
3. **《校園霸凌防制準則》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049586](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049586)
4. **《高級中等以下學校教師解聘不續聘停聘或資遣辦法》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049588](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049588)
5. **《校園性別事件防治準則》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL034837](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL034837)
6. **《學校訂定教師輔導與管教學生辦法注意事項》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL043009](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL043009)
7. **《教師法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=16](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=16) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=32](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=32)
8. **《個人資料保護法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=2](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=2)、[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=5](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=5) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=19](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=19)
9. **《中華民國刑法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=310](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=310) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=311](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=311)
10. **《學生輔導法》**：[https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=H0070066](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=H0070066)

---

## 四、 未處理項目與後續規劃

1. **`theme_taxonomy.md` 之法令同步**：因派工單 0002 禁止修改 `theme_taxonomy.md`，主題 3（霸凌處置）、主題 4（管教方式）、主題 10（LINE群組）之最新條文引註暫留待後續專屬派工任務更新。
2. **提示詞 `prompts/` 模組與 `README.md` 更新**：同受派工單範圍限制，將於後續核准任務中依據 `research_D_legal.md` 進行修訂。
3. **`docs/` 資料夾導讀文件補充**：暫未寫入 `docs/`，留待後續核准任務新增。

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
	modified:   research_D_legal.md

Untracked files:
	.codex-orchestration/reports/report-agy-0002.md
```

---

*任務 0002 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
