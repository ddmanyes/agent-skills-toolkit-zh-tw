# NotebookLM 操作與復原

本文件維護呼叫方式，執行仍依既有安裝的 scripts/run.py。`SKILL_DIR` 必須解析為包含本 Skill 的絕對路徑；使用参数陣列或正確引號傳遞使用者文字，不拼接可執行的 shell 字串。

| 分支 | 傳給 wrapper 的指令 |
| --- | --- |
| 狀態 | auth_manager.py status |
| 互動登入 | auth_manager.py setup |
| 驗證登入 | auth_manager.py validate |
| 清單／搜尋 | notebook_manager.py list / search --query TEXT |
| 新增本機記錄 | notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS |
| 指定 notebook 查詢 | ask_question.py --question TEXT --notebook-id ID |
| 指定 URL 查詢 | ask_question.py --question TEXT --notebook-url URL |
| 除錯顯示瀏覽器 | ask_question.py --question TEXT --notebook-id ID --show-browser |
| cleanup 預覽 | cleanup_manager.py |

只有使用者要求移除某筆本機記錄，才對該 ID 使用 notebook_manager.py remove。只有使用者要求重設登入，才使用 auth_manager.py clear／reauth；後者會清除舊登入。不要把帳戶切換當作繞過服務配額的方法。

cleanup_manager.py --confirm 會實際刪除資料；先預覽確切範圍，備份會失去的 library／必要設定，再確認該範圍已獲授權。--preserve-library 僅保留 library，不能當成保留登入狀態的承諾。瀏覽器崩潰先保留錯誤，不能直接清除整套資料。

wrapper 可能在首次執行建立 `.venv` 並安裝既有 requirements；這是寫入操作，先確認此安装維護在授權範圍。若自動環境建立失敗，讀實際 setup_environment.py 與 requirements，定位 Python、套件或瀏覽器缺件；不要用固定的 Chromium/Chrome 假設取代目前實作。

資料位置由 config.py 定義：data/library.json、data/auth_info.json、data/browser_state/。不讀出 cookies/token 到回覆、log 或提交；保留既有 .gitignore。舊文件中的固定每日次數、固定延遲和環境變數須以實際服務／程式為準，未驗證不作保證。

失敗後最多一次針對已定位原因的安全重試；同樣错误重現則回報並停止依賴查詢。來源不足不是工具故障，不以反覆重問補出不存在的答案。
