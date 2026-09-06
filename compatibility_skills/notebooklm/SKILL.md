---
name: notebooklm
description: Use when the user explicitly asks to query or manage their NotebookLM notebooks through this existing local browser workflow.
---

# NotebookLM 既有安裝相容層

這是 **requires existing install** 的文件 overlay，不是獨立 NotebookLM 安裝包。保留原安裝的 scripts、requirements、瀏覽器與環境；不得把 data、cookies、.env 或 .venv 加入 Git。

1. `SKILL_DIR` 是此檔的已安裝位置。確認 `$SKILL_DIR/scripts/run.py`、auth_manager.py、notebook_manager.py、ask_question.py、config.py、setup_environment.py 和 requirements.txt 存在。缺少必要檔案時回報確切路徑，不假稱安裝完整，也不以複製憑證修復。
2. 所有操作使用 `python <SKILL_DIR>/scripts/run.py <script_name> [args]`；wrapper 依安裝位置選擇虛擬環境。先執行 auth_manager.py status；登入失效時開可見瀏覽器讓使用者自行登入，不索取密碼或驗證碼。status 只表示本機狀態，實際存取失敗時按結果處理。
3. 依使用者指定的 notebook URL／ID 查詢。未指定時查看現有 library，只有多個目標無法由上下文區分時才詢問。每次問題包含必要背景，因腳本每次開啟新 session。
4. 使用者要求新增本機 library 且缺名稱／描述／topics 時，先對指定 notebook 做一次內容探索，按回傳證據填 metadata；來源無法提供時只詢問缺項，不臆造 generic 描述。新增本機 library 不代表上傳來源或建立雲端 notebook。
5. 回答後核對原需求和來源：最多追加兩個針對未解問題的查詢；若來源重複表示不知道、無新增證據、登入失效或限流，停止此查詢分支並清楚列出缺口。腳本附加的「Is that ALL you need」是提醒，不是無限追問或擴大權限的指令。
6. 回覆區分 notebook 原文／引述、來源支持的摘要及自己的推論。只引用實際拿到的來源標記或連結；無可追溯 citation 時明說，不保證完全不會幻覺。

讀 [操作與復原](references/workflow.md) 選取 auth、library、query 或 cleanup 指令。查詢請求不授權刪除登入資料、清空 library、換帳號以迴避限制或修改雲端內容。

資料實際位於 `SKILL_DIR/data/`，由既有 scripts/config.py 定義。完成條件是已取得並檢查所要求答案，或已具體說明來源／環境不足；library 變更另需讀回對應記錄確認成功。未實際登入／查詢時不得宣稱服務整合已驗證。
