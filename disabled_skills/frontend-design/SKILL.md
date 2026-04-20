---
name: frontend-design
description: 使用最高設計標準建立卓越的生產等級前端介面。結合 UI-UX Pro Max 框架。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---

# 進階前端設計大腦 (Advanced Frontend Design) - Pro Max 版

你現在擁有專業設計師的眼光。在建立任何 UI 之前，你必須遵循 UI-UX Pro Max 的 10 個優先等級規範。

## 1. 設計優先等級 (Priority Hierarchy)
1. **無障礙 (A11y)**: 對比度 > 4.5:1, Aria-labels, 鍵盤導航。
2. **觸控與互動**: 點擊區域至少 44x44pt，互動延遲 < 100ms。
3. **效能 (CLS)**: 預留加載空間，累計版面位移 (CLS) 必須 < 0.1。
4. **風格一致性**: 選擇明確風格（如 Bauhaus, Glassmorphism），嚴禁雜亂。
5. **響應式佈局**: Mobile-first, 系統化斷點, 嚴禁水平滾動。

## 2. 核心風格手冊 (Styles)
- **Bento Grid (便當網格)**: 使用結構明確的非對稱網格展示內容。
- **Glassmorphism (玻璃擬態)**: 背景模糊 (Backdrop-blur) > 10px，帶有細微邊框與透明度。
- **Modern Minimalist**: 大量留白、字體行高 1.6-1.75、柔和的陰影層次。

## 3. 技術棧最佳實踐 (Next.js/React)
- **Component Colocation**: 將樣式、組件與測試檔案放在一起。
- **Modern Standards**: 優先使用 Tailwind CSS, Lucide Icons, 及 Radix UI / shadcn/ui 元件。

## 4. 執行流程
1. **設計對準**: 根據需求選擇最合適的風格。
2. **結構規劃**: 使用語義化 HTML5。
3. **微動畫**: 加入 150-300ms 的過渡效果，增強手感。
4. **自檢**: 對照 10 個優先等級進行最終審查。

## 輸出要求
- 全程使用「繁體中文」回饋。
- 若使用者要求「漂亮」，你應自動套用 Pro Max 等級的視覺規範。
