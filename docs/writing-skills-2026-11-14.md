# 寫作技能安裝與使用

本輪新增兩個繁中適配技能。先用 writing-clearly-and-concisely 整理內容，再用 humanizer 檢查模板痕跡。研究文件最後核對數字、分析單位、分母與證據強度。保留原版請建立新檔。

```bash
./scripts/sync-local-skills.sh --agents --skill writing-clearly-and-concisely --skill humanizer
```

若Claude共用agents symlink，不必重複同步。其他客戶端依安裝指南選擇。來源、版本與授權在各技能目錄；未安裝Academic-Writing-Humanizer，避免增加重疊入口與不需要的detector流程。

驗證範圍：frontmatter、參考檔、語義與授權人工核對；本機實際任務會另記錄。靜態通過不代表跨模型效能或自然文風已獲實驗驗證。
