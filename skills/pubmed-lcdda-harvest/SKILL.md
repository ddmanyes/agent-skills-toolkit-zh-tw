---
name: pubmed-lcdda-harvest
description: 用關鍵字搜尋 NCBI/PubMed 上的生醫文獻，列出候選清單讓使用者挑選，再透過 lcdda-harvest 抓全文並依 lcdda 歸檔規則存進研究資料庫。當使用者說「幫我查 PubMed/NCBI 上關於 X 的文獻」、「幫我找 X 相關論文存進資料庫/lcdda」、「用 lcdda-harvest 收錄 X 主題的文獻」、或任何「搜尋生醫文獻並歸檔」的請求時，主動使用這個 skill，即使使用者沒有明確講出「PubMed」或「lcdda-harvest」這些字眼，只要主題明顯是生醫/分子生物/基因體/空間轉錄體等領域，都應觸發。注意 PubMed 只收錄生醫文獻，若主題明顯是 AI/agent/CS 類（例如 LLM、reasoning model），這個 skill 不適用，應改用 alphaXiv 相關流程。
---

# PubMed → lcdda-harvest 文獻收錄

## 這個 skill 在做什麼

使用者給一個研究主題或關鍵字，你負責：查 PubMed 找出候選文獻 → 列清單讓使用者挑要收錄哪幾篇（不要自己替使用者決定全收）→ 對選中的文章用 lcdda-harvest 抓全文並存進 lcdda 資料庫 → 視需要建立筆記把它們串起來。

跟「每日文獻雷達」排程不同：那是自動、被動、不篩選地推播新論文；這個 skill 是使用者主動喊出來、針對特定主題做一次性收錄，而且會實際把全文存進資料庫，所以篩選這一步很重要——PubMed 關鍵字搜尋雜訊不小，直接全收會讓 lcdda 資料庫裡塞進大量使用者根本不在乎的文章，之後搜尋自己的筆記反而變難用。

## 使用前提

lcdda-harvest 的工具（`mcp__remote-devices__lcdda-harvest__*`、`mcp__remote-devices__lcdda__*`）只有在使用者的電腦透過 Claude 桌面 app 連結到目前 session 時才存在。動手前，先確認這些工具在你的工具列表裡；如果不在，不要嘗試呼叫，直接告訴使用者現在沒有連線，請他們在該電腦的桌面 app 裡把這個 task 連結到那台機器，之後你才能繼續（PubMed 搜尋跟列清單這兩步不需要連線，可以先做，只有實際 harvest 那步需要）。

## 流程

### 1. 確認搜尋範圍

如果使用者給的關鍵字/主題聽起來偏 AI、agent、LLM、CS 領域而不是生醫，先跟使用者確認——PubMed 查不到這類文獻，這種情況該提醒他們這個 skill 是給生醫文獻用的，AI 類文獻建議改用 alphaXiv。

### 2. 用 PubMed 搜尋候選文獻

呼叫 `mcp__PubMed__search_articles`：
- `query`：把使用者的主題轉成 PubMed 語法。可以善用欄位標籤（`[Title]`、`[MeSH Terms]`、`[Publication Type]`）跟布林運算子讓查詢更精準，不要只丟一串自然語言關鍵字進去，除非主題本來就很單純。
- `max_results`：預設抓 15 筆。使用者要更多/更少再調整。
- `sort`：預設用 `relevance`；如果使用者的意圖明顯是「最近有什麼新的」，改用 `pub_date`。
- 需要限定年份時用 `date_from`/`date_to`（配 `datetype: pdat`）。

如果搜尋結果是 0 筆或很少，不要就這樣結束——放寬查詢（拿掉某些欄位限制、換同義詞）再試一次，並讓使用者知道你放寬了查詢條件。

### 3. 列出候選清單，讓使用者挑選

不要自動把所有搜尋結果拿去 harvest。把候選文獻列成清單給使用者看，每篇包含：標題、作者（第一作者 + et al.）、期刊/年份、PMID、一行摘要重點（用 `get_article_metadata` 補摘要，如果 search_articles 回傳的內容不夠判斷相關性再叫這個）。

請使用者用編號或標題告訴你要收錄哪幾篇（可以是「全部」「1、3、5」「跟 XX 機制有關的那幾篇」）。這一步是防雜訊的關鍵關卡，不要跳過，也不要因為使用者很趕就自作主張全收。

### 4. 對選中的文章逐篇 harvest

對使用者選中的每一篇，呼叫 lcdda-harvest 的抓取管線（優先用這個，不要自己手動抓 HTML/PDF）：

1. `harvest_submit`：`query` 用文章的完整標題（或標題+第一作者，避免抓錯論文），`mode="keyword"`，`limit` 設小（例如 3）避免混入不相關論文，`q1` 不確定時先 `false`。
2. `harvest_status(job_id)`：輪詢到完成，核對抓回來、存檔的是不是這篇——標題、作者要對得上，對不上就當作失敗處理，不要硬收。

多篇文章可以依序處理；不需要每篇都跟使用者確認進度，跑完一輪後統整回報結果（成功幾篇、失敗/擋下幾篇）即可。

### 5. 全文抓不到時的手動匯入

如果某篇被出版社擋下（bot-blocked）或 harvest 找不到全文：
1. 請使用者把該篇 PDF 下載到 `~/Downloads`、`~/Desktop` 或 `/Volumes/KINGSTON` 其中之一。
2. 用 `import_manual(src=<資料夾>, mode="manual")`，先加 `dry_run` 試跑一次，確認檔名比對邏輯抓到的是正確的檔案。
3. 確認無誤後正式匯入，用 `import_status(job_id)` 確認結果。

### 6. 確認歸檔位置

harvest/import 完成後,確認存檔位置符合 lcdda 的歸檔規則：
- 有 DOI/期刊/明確第一作者 → `20-areas/research/{YYYY}_{FirstAuthorLastName}_{ShortTitle}.md`
- 沒有明確發表資訊 → `30-resources/`，用 kebab-slug 檔名
- 發表狀態不確定時，先跟使用者確認，不要自行假設已發表

### 7.（選擇性）建立 project note 串起這批文獻

只有在使用者這次的目的明顯是要開一條新的研究討論線（而不是單純「先幫我收進資料庫，之後再看」）時才做這一步。用 `lcdda__new_note(note_type="project")` 建立筆記，帶入這批文獻共同的研究問題/初步觀察，並在內容或 tags 中關聯到剛存的文獻筆記。

建立筆記後**一定要**呼叫 `lcdda__sync_index()`——harvest/save_article 通常即時索引，但 `new_note` 不會，漏掉這步的話這個新筆記之後搜尋不到。

## 完成後跟使用者說什麼

簡短回報：這次收錄了幾篇、分別存在哪裡（路徑），失敗/手動匯入的有哪幾篇、原因是什麼。不用逐篇複述摘要內容——使用者接下來大概率會挑一兩篇要你深入討論，把空間留給那個對話。
