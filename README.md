# Antigravity Skills ZHT (繁體中文優化版) 🚀

歡迎使用！本專案收錄了超過 25 個經由開發者社群優化的 **Claude Code (Antigravity)** 高階技能。

我們已經將這些技能翻譯為繁體中文，並針對「資訊分析」、「UI/UX 設計」與「自動化開發」進行了邏輯強化。

---

## ⚡️ 一鍵快速安裝 (推薦新手使用)

請將以下這段內容**完整複製**，並直接貼給你的 **Claude / Antigravity** 助手：

> ```text
> 我是新手，我想安裝「Antigravity Skills ZHT」技能包。
>
> 請幫我執行以下自動化部署任務：
>
> 1. **路徑偵測**：自動辨識我的作業系統路徑：
>    - Mac/Linux: ~/.gemini/antigravity/
>    - Windows: %USERPROFILE%/.gemini/antigravity/
>
> 2. **建立目錄**：在上述路徑內建立「skills」與「disabled_skills」資料夾（如果尚未存在）。
>
> 3. **連線與部署**：
>    - 存取 GitHub 倉庫：https://github.com/你的用戶名/你的倉庫名
>    - 讀取「skills/」與「disabled_skills/」目錄下的所有技能。
>
> 4. **衝突與更新策略**：
>    - 如果發現我的電腦裡已經有同名的技能資料夾，請逐一詢問我：「檢測到舊版 [技能名稱]，是否要以繁體中文優化版覆蓋更新？」
>    - 如果是新的技能，請直接建立資料夾並寫入 SKILL.md。
>
> 5. **權限要求**：請自動幫我完成所有目錄建立與檔案寫入，結束後顯示完整的技能佈署地圖。
> ```

---

## 🗺️ 新專案怎麼串起來用

不知道從哪個 skill 開始？看 **[新專案工作流.md](./新專案工作流.md)**——一張流程圖 + 對照表，說明開新專案時各階段該呼叫哪個 skill。

---

## 📂 技能包內容清單

### 核心開發 (Active)

- **SP 系列**：腦力激盪（已升級為 grilling 決策樹拷問）、極細計畫、自動執行、子代理調度、測試除錯等。
- **架構工具**：專案建築師 v3.0、循環開發 (Ralph)、檔案計畫管理 (Manus 風格)。
- **代碼品質**：資深代碼審查（雙軸 Standards/Spec 並行 + Fowler code smell 基線）、代碼簡化專家。
- **Skill QA Gate**：建立、修改或發布 Skill 時，檢查結構、安全邊界、指令歧義與語義保留；一般 Skill 執行不會觸發。

### 設計方法論 (Active，源自 mattpocock/skills)

- **domain-modeling**：建立與磨利專案的領域模型——`CONTEXT.md` 術語表 + ADR 決策紀錄（三條件才寫）。
- **improve-architecture（去蕪存菁）**：掃描程式碼庫找出深化模組的機會，用 deletion test 判斷哪些抽象在白佔位。
- **writing-great-skills**：寫 skill 的品質判準——leading word、progressive disclosure、no-op、failure modes（含 GLOSSARY）。

### 數據與檔案 (Active)

- **Office 專家**：Word (XML 級別編輯)、Excel (數據分析)、PPT (專業設計師版)、PDF (高精準提取)。

### 圖表與知識視覺化 (Active)

- **diagram-design**：將文字、Mermaid 或 draw.io 重繪為專業、可存取的 SVG／單檔 HTML；支援架構圖、流程圖、資料流、時間軸與 Dots／signal-flow，並可把產物索引寫回 Second Brain。

### 視覺與藝術 (Disabled by default)

- **設計專家**：UI-UX Pro Max、玻璃擬態、前端設計、自動化測試。
- **創意工具**：生成式藝術、Slack GIF 製作。

---

## 📜 聲明與致謝

本專案為開源社群作品，核心邏輯之版權歸屬原創作者。詳細致謝清單請參閱 [ACKNOWLEDGEMENTS.md](./ACKNOWLEDGEMENTS.md)。
