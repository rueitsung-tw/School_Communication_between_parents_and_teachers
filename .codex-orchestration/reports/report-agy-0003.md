# 報告 agy-0003：同步高風險主題的法令知識卡

**執行任務 ID**：0003  
**執行步驟**：唯一步驟 — 更新 `theme_taxonomy.md` 主題 3、4、10 之法令欄位與必要溝通策略  
**執行者**：agy  
**執行日期**：2026-08-22  

---

## 一、 摘要與執行範疇說明

本報告記錄任務 0003 之執行結果。依據派工單 `.codex-orchestration/codex-task-dispatch.md` 與計畫 `.codex-orchestration/plans/plan-0003.md`，本任務將 `theme_taxonomy.md` 中三個高風險主題（主題 3、主題 4、主題 10）之「相關法令依據」與「建議溝通策略」欄位，與已核准之 `research_D_legal.md` 保持完全一致，避免 UI 知識卡與後續提示詞使用過時或絕對化之法令描述。

本任務嚴格遵守權限界線，**僅修改 `theme_taxonomy.md` 與本報告 `report-agy-0003.md`**，未修改任何提示詞、Python 程式、`README.md`、`research_D_legal.md`、`docs/` 或 RAG 索引。

---

## 二、 `theme_taxonomy.md` 主題欄位更新細節對照表

| 主題編號與名稱 | 修改欄位 | 更新前內容問題 | 更新後內容與條件化說明 |
|---|---|---|---|
| **主題 3：同儕衝突與霸凌處理** | 相關法令依據 | 僅記載舊版《校園霸凌防制準則》概括通報義務，未區分生對生/師對生分流，亦欠缺 2024 新制令號與條文號 | 1. 引註《校園霸凌防制準則》（113.04.17 修正發布，臺教學（五）字第 1132801790A 號令）。<br>2. 載明第 17 條：知悉疑似事件應立即向學校權責人員通報，通報主管機關至遲不得超過 24 小時。<br>3. 載明第 5 條及第 7 條第 1 項第 2 款但書：高級中等以下學校生對生霸凌依本準則處理，師對生霸凌依解聘辦法移由校事會議處理。<br>4. 載明第 4 條第 8 款：調和程序僅適用於生對生事件且須雙方同意，不得替代法定程序。<br>5. 附《兒少法》第 53 條 24 小時社政通報與官方直連。 |
| **主題 3：同儕衝突與霸凌處理** | 建議溝通策略 | 欠缺調查前不私下定性之提醒 | 新增提醒：說明校內已採取的安全觀察與處置步驟（勿於調查前私下給予霸凌定性結論），並說明法定通報與調和程序條件（生對生霸凌得在雙方同意下啟動調和）。 |
| **主題 4：管教方式與獎懲制度** | 相關法令依據 | 僅引註舊版管教辦法與判例摘要，欠缺 2024 新增之阻卻違法條件，且誤引《教師法》第 16 條為義務 | 1. 引註《學校訂定教師輔導與管教學生辦法注意事項》（113.02.05 修正發布，臺教學(五)字第 1132800502A 號函）。<br>2. 載明第 22 點等增列教師阻卻違法事由（維護秩序、避免緊急危難如防衛/避難或處置危險物品得採必要強制措施，具合法處置條件，非一般無條件免責）。<br>3. 修正引註《教師法》第 32 條（輔導管教義務）與官方直連。 |
| **主題 4：管教方式與獎懲制度** | 建議溝通策略 | 僅寫說明法規依據 | 補充說明：說明採取必要輔導管教措施之客觀事由與正當性，避免宣稱教師當然無條件免責。 |
| **主題 10：LINE 群組溝通禮儀與界線** | 相關法令依據 | 概括標示個資法與公然侮辱判例，未區分公私立學校個資條文，表述過度絕對 | 1. 區分《個資法》：公立學校（公務機關）依第 15 條（蒐集）與第 16 條（利用）；私立學校（非公務機關）依第 19 條（蒐集）與第 20 條（利用）；於群組傳送學生個資須依機關屬性與第 5 條比例原則評估，具條件性風險。<br>2. 附《刑法》第 310 條誹謗罪構成要件與第 310 條第 3 項/第 311 條免責要件與官方直連。 |
| **主題 10：LINE 群組溝通禮儀與界線** | 建議溝通策略 | 僅寫私下個別溝通 | 補充說明：私下轉為個別電話或面談溝通（避免於群組中公開爭論或評論學生個人隱私）。 |

---

## 三、 每一項法源之官方一手 URL

1. **《校園霸凌防制準則》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049586](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL049586)
2. **《兒童及少年福利與權益保障法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=53](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0050001&flno=53)
3. **《學校訂定教師輔導與管教學生辦法注意事項》**：[https://edu.law.moe.gov.tw/LawContent.aspx?id=FL043009](https://edu.law.moe.gov.tw/LawContent.aspx?id=FL043009)
4. **《教師法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=32](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=H0020040&flno=32)
5. **《個人資料保護法》**：
   - 公務機關：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=15](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=15)、[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=16](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=16)
   - 非公務機關：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=19](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=19)、[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=20](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=20)
6. **《中華民國刑法》**：[https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=310](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=310) 及 [https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=311](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=311)

---

## 四、 未修改項目與原因

1. **主題 1、2、5、6、7、8、9**：因派工單 0003 範圍嚴格限定僅修改高風險主題 3、4、10，其他主題未受本次法令修正直接影響，故維持原狀。
2. **`prompts/` 提示詞模組與 `README.md`**：受派工單範圍限制，留待後續專屬派工任務進行同步。
3. **`docs/` 資料夾導讀文件**：留待後續核准任務新增。

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
	modified:   theme_taxonomy.md

Untracked files:
	.codex-orchestration/reports/report-agy-0002.md
	.codex-orchestration/reports/report-agy-0003.md
```

---

*任務 0003 執行完畢，報告已寫入，停止執行，等待 Codex 審查。*
