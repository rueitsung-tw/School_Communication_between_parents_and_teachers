# 報告 agy-0002：更新法令研究基礎與可追溯法源（三次審查修正版）

**執行任務 ID**：0002
**執行步驟**：唯一步驟 — 更新 `research_D_legal.md` 法令研究基礎與可追溯法源（三次審查修正版）
**執行者**：agy
**執行日期**：2026-08-22

---

## 一、 摘要與補正範疇說明

本報告記錄任務 0002 第三次修正作業之執行結果。依據派工單 `.codex-orchestration/codex-task-dispatch.md` 第三次退回指示，本補正針對 `research_D_legal.md` 完成以下三項精準修正：

1. **霸凌通報條文更正為第 17 條**：更正《校園霸凌防制準則》通報條文為**第 17 條**，載明校長及教職員工知悉疑似校園霸凌事件時，應立即向學校權責人員通報，並由學校權責人員向主管機關通報，至遲不得超過 24 小時。
2. **移除無案號之經驗性結論與判斷字眼**：徹底移除「實務上多認定」、「法院或檢察官主要審酌」等經驗性用語，改為客觀中性之條件式風險說明（如說明涉訟時主要評估是否具備輔導目的、比例原則、言論是否有據或具備免責條款）。
3. **報告與檔案格式驗證**：確保 `research_D_legal.md` 與本報告檔 `report-agy-0002.md` 尾端無任何多餘空白，實際執行 `git diff --check` 達到零錯誤。

本任務嚴格遵守權限界線，**僅修改 `research_D_legal.md` 與本報告 `report-agy-0002.md`**，未修改任何提示詞、Python 程式、`README.md`、`theme_taxonomy.md`、`docs/` 或 RAG 索引。

---

## 二、 `research_D_legal.md` 修改章節與內容詳情

| 修改章節 | 修改前問題 | 修改後內容與條件化說明 |
|---|---|---|
| **《校園霸凌防制準則》通報條文** | 誤引為第 11 條 | 修正為 **第 17 條**（第 17 條第 1 項：知悉疑似事件應立即向學校權責人員通報；第 17 條第 2 項：學校權責人員向主管機關通報至遲不得超過 24 小時）。 |
| **第 2 節風險分析** | 含有「法院多認定」、「法院主要審酌」等經驗性傾向表述 | 移除經驗性斷言，改為中性條件式分析（如「涉及評估是否符合輔導目的與比例原則」、「須視是否符合《刑法》第 310 條/第 311 條免責要件」）。 |
| **《個人資料保護法》** | 未區分公立與私立學校適用條文 | 明確標示公立學校（公務機關）適用第 15、16 條，私立學校（非公務機關）適用第 19、20 條。 |
| **《校園性別事件防治準則》** | 令號與名稱標示 | 標示修正令號 **臺教學（三）字第 1132801024A 號令**，官方直連至 `https://edu.law.moe.gov.tw/LawContent.aspx?id=FL034837`。 |

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

*任務 0002 第三次修正執行完畢，報告已覆寫寫入，停止執行，等待 Codex 審查。*
