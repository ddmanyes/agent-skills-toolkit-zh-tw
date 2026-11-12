# dsh-purge 的機制與移植範圍

研究來源：[HunYiSage/dsh-purge](https://github.com/HunYiSage/dsh-purge)，固定 revision `4c3369a945701598275dcabbe958b7b815570ed5`，package 版本 1.1.90。以下為靜態來源觀察，並非插件或模型執行結果。本技能是依機制研究撰寫的原創通用實驗工具，未複製上游提示詞或宿主補丁。

## 三個不同層級

1. **模型請求**：由使用者可控制的 API client 組裝 system/user messages。這是本技能的 A/B 實驗範圍；只能影響送入該次請求的文字，不代表外層代理的 system/developer 指令被更改。
2. **宿主提示詞組裝**：上游 `lib/index.js` 註冊 prompt sections 並攔截 assembly；`lib/identity.js` 重新排列、移除或改寫若干 sections。這依賴 DSH 插件介面和版本。`lib/rules.js:243-256` 的正文來源是進程已提交文字、磁碟注入檔、bundled 預設；`266-283` 的規則啟用另寫入 AGENTS.md/CLAUDE.md，不應把這兩條路徑混為一談。
3. **宿主執行權限**：`lib/core.js` 包含更動審批、沙箱和工具執行邏輯的補丁。文字提示詞不會自行更改 OS 權限、工具 schema 或代理審批政策；本技能不提供這些補丁。

引用：[提示詞入口](https://github.com/HunYiSage/dsh-purge/blob/4c3369a945701598275dcabbe958b7b815570ed5/lib/index.js)、[組裝重寫](https://github.com/HunYiSage/dsh-purge/blob/4c3369a945701598275dcabbe958b7b815570ed5/lib/identity.js)、[規則來源](https://github.com/HunYiSage/dsh-purge/blob/4c3369a945701598275dcabbe958b7b815570ed5/lib/rules.js)。

## 生命周期與可靠性

- `injectOnce` 在已檢查的來源中只有預設值與正規化使用點；不能據此聲稱「只注入一次」。assembly 路徑會重做提示詞處理。
- 版本宣告列出 DSH `0.2.1-rc.2` 與 `0.2.1-rc.5`；部分 README 段落仍寫較舊支援範圍。版本比對僅是宣告，不是實機相容證據。
- `core.js:7553-7556` 將 `drifted` 列為 soft OK，因此零 failed 不等於每個補丁有效。
- `core.js:2007-2050` 的備份與套用不是整體交易；備份報告錯誤不必然阻止後續套用。備份存在也不證明可完整恢復。
- 舊備份遇上官方升級可能恢復成混合版本；上游有基線刷新邏輯，但不能取代實際恢復驗證。

引用：[版本宣告](https://github.com/HunYiSage/dsh-purge/blob/4c3369a945701598275dcabbe958b7b815570ed5/package.json)、[補丁與恢復實作](https://github.com/HunYiSage/dsh-purge/blob/4c3369a945701598275dcabbe958b7b815570ed5/lib/core.js)。

## REA 的有限觀察

在研究機器上的已安裝 DSH `0.1.5-rc.3` 中，對 `dsh-persona` 的 `package.json` 與 `lib/index.js` 做 REA 靜態分析。parent Evidence 為 `ev_f3f5f0fdac94065fd59cf9df31855b272408dfaa745d8018b4685e6d918e75b9`，產物目錄 SHA-256 為 `4ff572a44f3e0f6fcb9a2d003fb5ef38600e01af0fd2f9c1abb0d22426d9652b`。該模組具有原生的 per-agent persona prefix/suffix 註冊介面；它要求 agent scope，不能推論為全域任意注入能力。

REA 未執行插件。分析只選取兩個檔案，還有一個 inventory 檔案與動態關係未分析；graph coverage 是 partial。此證據不代表目前版本 dsh-purge 可在該舊宿主運作。

## 本技能採用的設計

保留來源摘要、明確提示詞配置、合成案例、固定參數、逐筆結果與未解問題。輸出位於新實驗目錄，不修改宿主，因此原設定無須回滾。原生設定變更屬另一個具體操作，不能從「研究或測試」推導出授權。

證據分類可參考上游 [evidence-ledger.mjs](https://github.com/HunYiSage/dsh-purge/blob/4c3369a945701598275dcabbe958b7b815570ed5/lib/redteam/evidence-ledger.mjs)，但雜湊只能辨識內容；分類標籤與雜湊都不能自行證明結果真實。需要獨立工具輸出支持完成宣告。
