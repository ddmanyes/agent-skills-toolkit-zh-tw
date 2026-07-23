---
name: improve-architecture
description: 去蕪存菁：掃描程式碼庫找出深化模組的機會，用 deletion test 判斷哪些抽象在白佔位。
disable-model-invocation: true
---

# 去蕪存菁：深化程式碼架構 (Improve Architecture)

找出架構摩擦，提出**深化機會 (deepening opportunities)**——把淺模組變深的重構。目標是三件事：呼叫端的 **leverage（槓桿）**、維護者的 **locality（在地性）**、以及所有人的**可測試性**。

這個 skill 由專案的領域模型指引：先讀 `CONTEXT.md`（術語）與 `docs/adr/`（既有決策，不要重新翻案）。若這些檔不存在，可搭配 `domain-modeling` skill 邊做邊建。

## 設計詞彙 (統一用詞，不要換成 component/service/API/boundary)

- **Module（模組）**：任何有「介面 + 實作」的東西，尺度無關——函式、類別、package、跨層切片都算。
- **Interface（介面）**：呼叫端為了正確使用它「必須知道的一切」——型別簽章，加上不變式、順序約束、錯誤模式、必要設定、效能特性。比「函式簽章」更廣。
- **Depth（深度）**：介面上的槓桿——呼叫端（或測試）每學一單位介面，能操作多少行為。**深模組** = 小介面藏大量行為；**淺模組** = 介面幾乎和實作一樣複雜（要避免的）。
- **Seam（接縫）**（Michael Feathers）：能在「不編輯該處」的情況下改變行為的位置；也就是模組介面所在之處。「縫要放哪」本身是一個獨立的設計決策。
- **Leverage（槓桿）**：深度帶給呼叫端的——一份實作在 N 個呼叫點和 M 個測試上回本。
- **Locality（在地性）**：深度帶給維護者的——變更、bug、知識、驗證集中在一處，而非散落到各呼叫端。修一次，處處都修好。

## 核心判準

- **Deletion test（刪除測試）**：想像把這個模組刪掉。如果複雜度隨之消失 → 它只是個 pass-through，該砍。如果複雜度會在 N 個呼叫端重新冒出來 → 它在賺它的位子。**「消失還是搬家」是去蕪存菁的核心問句。**
- **介面就是測試面**：呼叫端和測試穿過同一道 seam。如果你想測「介面之後」的東西，代表這個模組形狀不對。
- **一個 adapter 是假想的縫，兩個 adapter 才是真的縫**：除非真的有東西跨這道縫在變，否則別開縫。
- **淺模組的訊號**：理解一個概念得在一堆小模組間彈來彈去；為了「可測試」而抽出的純函式，真正的 bug 卻藏在它「怎麼被呼叫」（沒有 locality）。

## 執行流程 (Process)

### 1. 探索 (Explore) — 先劃範圍，YAGNI

深化一個模組的回報，來自它未來更好改。所以把重量壓在「最近常動」的地方：
- 使用者若指定了方向（某模組/子系統/痛點），直接採用，跳過下面的推斷。
- 否則走一段 `git log --oneline`，找出反覆出現的 hot spot，讓那些路徑先吸引你的注意；若改動散無熱點，就把網撒大。

可用 `Explore` sub-agent 走一遍程式碼庫。別套死板 heuristic，有機地探索，記下你感到摩擦的地方：哪裡淺、哪裡耦合從縫漏出去、哪裡透過現有介面難以測試。對每個疑似淺模組套 **deletion test**：「刪掉會集中複雜度，還是只是搬家？」——答「會集中」才是你要的訊號。

### 2. 用 Markdown 報告呈現候選

把候選寫成一份 Markdown 報告（放系統暫存目錄，例如 `$TMPDIR/architecture-review-<timestamp>.md`，別落進 repo）。每個候選一段：
- **Files** — 牽涉哪些檔案/模組
- **Problem** — 現在的架構為何造成摩擦（用 淺/耦合/無 locality 描述）
- **Solution** — 白話說會怎麼改
- **Benefits** — 用 locality 與 leverage 解釋，以及測試會怎麼變好
- **Before / After** — 用簡單文字或 ASCII 圖對照「淺 → 深」
- **Recommendation strength** — `Strong` / `Worth exploring` / `Speculative`

**領域用 `CONTEXT.md` 的詞彙，架構用上面的詞彙。** 若 `CONTEXT.md` 定義了「Order」，就講「Order intake 模組」，不要講「FooBarHandler」也不要講「Order service」。
若某候選牴觸既有 ADR，只在摩擦大到值得重開該 ADR 時才提，並明確標註。

報告末尾放 **Top recommendation**：你會先動哪一個、為什麼。
先不要提出具體介面設計。寫完檔案、告訴使用者絕對路徑後，問：「這些你想先探索哪一個？」

### 3. Grilling 迴路

使用者選定候選後，用 `sp-brainstorming` skill 陪他走決策樹——約束、相依、深化後模組的形狀、縫之後藏什麼、哪些測試會存活。

決策定案時，副作用**當場**發生，用 `domain-modeling` skill 讓領域模型保持最新：
- 深化後的模組取了一個 `CONTEXT.md` 沒有的概念名 → 把該詞加進 `CONTEXT.md`（不存在就 lazily 建）。
- 過程中把模糊術語磨利 → 當場更新 `CONTEXT.md`。
- 使用者以一個「有份量的理由」否決某候選 → 提議記成 ADR（框成：「要我記成 ADR，讓未來的架構檢視不再重複建議這個嗎？」），只在該理由未來探索者確實會需要時才記。

## 輸出要求

- 全程使用「繁體中文」與使用者溝通。
