---
name: ask-matt
description: Use when the user explicitly invokes ask-matt or asks which Skill to use; 依目前環境實際可用的技能，挑選最小可行的 Skill 或執行順序。
disable-model-invocation: true
---

# Ask Matt：本機技能路由

你的工作是選路，不是直接執行。

1. 從目前工作階段的可用技能清單確認候選。不要推薦未安裝或目前不可呼叫的技能。
2. 先判斷使用者需要的是解釋、研究、設計、實作、除錯、審查、文件產物、長期任務，或 Skill 維護。
3. 優先推薦能單獨完成工作的最小 Skill。只有在階段有明確交接條件時才排成序列。
4. 對每個建議說明「現在為何使用」與「完成條件」。若兩個技能重疊，說明選擇其中一個的理由。
5. 標出需要使用者決定、授權或提供資料的節點。不要把建議當成執行授權。
6. 輸出一個主要路徑；最多提供一個替代路徑。等待使用者選擇或要求開始執行。

## 常用分流

- 上一段沒聽懂：`wait-what`。
- 單一主題的一頁視覺解說：`eli5`。
- 跨多次對話的學習計畫：`teach`；把既有投影片或 PDF 轉成自學材料：`lecture-converter`。
- 一手來源研究並留下可引用報告：`research`；GitHub Stars 增量整理：`github-stars-radar`。
- Threads saved posts：`threads-bookmarks-radar`；X 書籤：`x-bookmarks-radar`；從 Second Brain 彙整三個來源的週報：`content-radar`。
- 需求仍模糊：`sp-brainstorming`；需求已定、需要計畫：`sp-writing-plans`；依既定計畫實作：`sp-executing-plans`。
- 新功能的測試先行：`tdd`；失敗測試或 bug：`sp-fix-test`；完成後審查：`sp-code-review`。
- 領域詞彙或 ADR：`domain-modeling`；深模組與架構摩擦：`improve-architecture`。
- 長任務需要檔案化進度：`planning-with-files`；依 PRD 自主循環：`ralph-loop`；使用者明確授權全自動執行：`autonomous-pilot`。
- 建立或修改 Skill：`skill-creator`，並以 `skill-qa-gate` 驗證；Agent 會讀的文件同時使用 `writing-for-agents`。
- Word、Excel、PowerPoint、PDF、圖表或網站等產物：依目前清單挑選對應的專用 Skill，不要用通用開發 Skill 代替。

這些分流是偏好，不是封閉清單。實際路由以目前工作階段提供的技能及使用者目標為準。
