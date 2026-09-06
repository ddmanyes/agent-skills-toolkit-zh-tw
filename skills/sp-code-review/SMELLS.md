# Code Smell 基線 (Fowler《Refactoring》ch.3)

Standards 審查使用本基線。子代理可讀共享檔案時傳入本文件路徑；無讀檔管道時附與範圍相關的必要原文，並確保有足夠上下文判斷。

兩條約束：
- **專案規範優先**：專案成文規範一律蓋過基線；基線與之衝突時，抑制該 smell。
- **一律是判斷題**：每個 smell 都是「疑似」的啟發式標籤（"possible Feature Envy"），不是硬性違規；工具（ruff/mypy/black）已能抓的一律略過。

逐條（是什麼 → 怎麼修，比對 diff）：

- **Mysterious Name** — 函式/變數/型別名字看不出它做什麼 → 改名；改不出誠實的名字代表設計本身模糊。
- **Duplicated Code** — 同一段邏輯形狀出現在多個 hunk/檔案 → 抽出共用、兩處都呼叫。
- **Feature Envy** — 一個方法一直伸手去拿別的物件的資料，多過用自己的 → 把方法搬到它所羨慕的資料上。
- **Data Clumps** — 同幾個欄位/參數老是綁在一起旅行（一個想誕生的型別）→ 打包成一個型別。
- **Primitive Obsession** — 用 primitive/字串頂替一個該有自己型別的領域概念 → 給那概念一個小型別。
- **Repeated Switches** — 對同一個型別的 `if`/`match` 級聯在改動裡反覆出現 → 用多型或一張共用的 map 取代。
- **Shotgun Surgery** — 一個邏輯變更逼你在很多檔案零散改一堆 → 把一起變的東西收進同一模組。
- **Divergent Change** — 一個檔案/模組因多個不相干理由被改 → 拆開，讓每個模組只為一個理由而變。
- **Speculative Generality** — 為規格沒要求的需求加的抽象/參數/掛鉤 → 刪掉，inline 回去，等真需求出現再說。
- **Message Chains** — 長長的 `a.b().c().d()` 導覽 → 用第一個物件上的一個方法把這串走訪藏起來。
- **Middle Man** — 一個類別/函式大部分只是把呼叫轉手 → 砍掉，直接呼叫真正的目標。
- **Refused Bequest** — 子類/實作忽略或覆寫掉繼承來的大部分東西 → 拿掉繼承，改用組合。
