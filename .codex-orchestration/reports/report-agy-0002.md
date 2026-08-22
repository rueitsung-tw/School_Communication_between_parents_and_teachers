# 報告 agy-0002：更新法令研究基礎與可追溯法源（退回補正二次修正版）

**執行任務 ID**：0002  
**執行步驟**：唯一步驟 — 更新 `research_D_legal.md` 法令研究基礎與可追溯法源（退回補正版）  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 摘要與補正範疇說明

本報告記錄任務 0002 補正作業之執行結果。依據派工單 `.codex-orchestration/codex-task-dispatch.md` 第二次退回指示，本補正針對 `research_D_legal.md` 完成以下三項核心修正：

1. **個資法公私立學校分流**：明確區分公立學校屬「公務機關」（依《個資法》第 15 條蒐集、第 16 條利用），私立學校屬「非公務機關」（依《個資法》第 19 條蒐集、第 20 條利用），避免將第 19 條當作所有學校 LINE 群組之唯一依據。
2. **判例章節更名與中性化**：將第 2 節標題更名為「常見親師衝突情境與法律風險分析（非判例整理）」，並明確聲明本區塊為實務情境法律風險分析，非司法院特例案號之判例摘錄。
3. **通報時限與條文分流**：將通報責任改為依各該專用法規及校內程序的條件式提醒，分別引註《兒少法》第 53 條（24 小時內）、《性別平等教育法》第 22 條與《校園性別事件防治準則》第 16 條（24 小時內），以及《校園霸凌防制準則》第 11 條（知悉後立即通報），避免合併成單一絕對 24 小時規則。

本任務嚴格遵守權限界線，**僅修改 `research_D_legal.md` 與本報告 `report-agy-0002.md`**，未修改任何提示詞、Python 程式、`README.md`、`theme_taxonomy.md`、`docs/` 或 RAG 索引。

---

## 二、 `research_D_legal.md` 修改章節與內容詳情

| 修改章節 | 修改前問題 | 修改後內容與條件化說明 |
|---|---|---|
| **《個人資料保護法》** | 未區分公立與私立學校適用條文，將第 19 條當作唯一依據 | 1. **公立學校（公務機關）**：個人資料之蒐集依第 15 條，利用依第 16 條。<br>2. **私立學校/非公務機關**：個人資料之蒐集依第 19 條，利用依第 20 條。<br>3. 評估 LINE 群組傳訊風險時須評估主體機關屬性、特定目的與第 5 條比例原則。 |
| **第 2 節判例章節** | 標題為「關鍵實務判例」，內文欠缺裁判書案號與司法院連結 | 1. 標題更名為「常見親師衝突情境與法律風險分析（非判例整理）」。<br>2. 增加顯性聲明：本區塊為常見親師情境之法律風險分析，非司法院具體案號判例整理，實際責任判定仍須視個案事證與法院判決。 |
| **通報時限與條文** | 將兒少保護、霸凌與性別事件簡化合併為單一「24 小時通報」 | 依各專用法規明確分流：<br>1. **兒少保護**：依《兒少法》第 53 條，至遲不得超過 24 小時通報社政主管機關。<br>2. **校園性別事件**：依《性平法》第 22 條及《校園性別事件防治準則》第 16 條，至遲不得超過 24 小時向校內權責人員通報。<br>3. **校園霸凌事件**：依《校園霸凌防制準則》第 11 條，知悉後**立即通報**校內權責單位。 |
| **《校園霸凌防制準則》** | 修正發文字號與程序分流法源 | 引註 **臺教學（五）字第 1132801790A 號令**，載明高級中等以下學校生對生依本準則（第 5 條第 1 項），師對生依《解聘辦法》（第 5 條第 3 項與第 7 條第 1 項第 2 款但書）；第 4 條第 8 款調和程序僅限生對生且須雙方同意。 |
| **《校園性別事件防治準則》** | 修正令號與名稱 | 修正為 **臺教學（三）字第 1132801024A 號令**，直連至教育部官方頁 `https://edu.law.moe.gov.tw/LawContent.aspx?id=FL034837`。 |

---

## 三、 每一項法源之官方一手 URL

1. **《教育基本法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020045&flno=8](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020045&flno=8)
2. **《兒童及少年福利與權益保障法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=53](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=53) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=100](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=100)
3. **《校園霸凌防制準則》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049586](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049586)
4. **《高級中等以下學校教師解聘不續聘停聘或資遣辦法》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049588](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049588)
5. **《校園性別事件防治準則》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL034837](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL034837) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0080067&flno=22](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0080067&flno=22)
6. **《學校訂定教師輔導與管教學生辦法注意事項》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL043009](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL043009)
7. **《教師法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=16](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=16) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=32](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=32)
8. **《個人資料保護法》**：
   - 公務機關：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=15](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=15)、[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=16](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=16)
   - 非公務機關：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=19](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=19)、[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=20](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=20)
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

*任務 0002 補正執行完畢，報告已覆寫寫入，停止執行，等待 Codex 審查。*
