# 細胞與 IF 的比較契約

## 分割

核、全細胞、核擴張與核周環各自標示來源；ring 不代表觀察到細胞膜。先核對候選偵測 Recall、FP/FN 與 split/merge，再評估邊界。完整人工實例遮罩與固定配對規則才支持 PQ/RQ/SQ；點註記或 AI 預審不能取代實例真值。記錄模型權重與資料重疊；同圖調參不能稱獨立驗收。

## 逐細胞資料

使用 image/dataset、series/z/t/ROI、segmentation version、object type 與 label ID 建立唯一身份。保留 mask hash、單位與座標 transform。重分割的同名 label 不代表同一細胞；合併拆分另存一對多／多對一關聯。

量測表保留 channel、marker、compartment、metric、value、unit 與 raw/corrected 狀態。未知值與原因分開保存，不默認為0；bin數不當UMI數，RNA expression不當蛋白強度。模型判定、人工、AI、QA各存來源與revision。

## IF

先固定 image+mask，比較兩個實作的像素數、area、mean/median/integrated intensity與縮放，隔離量測差異和分割差異。核對位深、軸序、曝光、飽和、flat/dark、背景與串色對照。沒有校準證據的分數不標機率或絕對蛋白量。

陽性規則與門檻在看驗收答案前凍結；保留UNKNOWN與原因、全體候選及可判讀者分母。雙陽性不等於分子共定位。跨組推論另外確認animal/section/field結構，不把細胞數當生物複本數；先前暫緩的統計工作不因引用本skill而自動恢復。

CellProfiler、QuPath、SpatialData與OME-NGFF可作量測／介面／資料交換候選；查核指定版本官方文件，不把固定版本API寫成永久約定。
