---
name: sp-learn-codebase
description: 為跨模組修改或架構問題探索陌生程式庫；局部修改只讀足以定位與驗證的相關內容。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---
# 程式庫探索
以當前問題劃定範圍，先遵守 AGENTS.md 與環境實際採用的專案指示。

1. 從相關設定（例如 pyproject.toml、requirements.txt、package.json）、入口與測試定位技術棧。
2. 追蹤會影響當前問題的關鍵模組、資料流、介面及相依；必要時用近期 commits 解釋變更背景。
3. 當修改位置、受影響介面、必要限制與驗證指令均可確定時結束探索。遇到無法查明的事項標示未知，不以讀完整庫作完成條件。
4. 使用者要求導覽或需要跨會話保存時才產生專案攻略：核心结构、常用指令及不明顯陷阱；沿用現有文件以免重複。

用繁體中文交代發現與其對任務的影響。
