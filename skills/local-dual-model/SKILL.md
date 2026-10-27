---
name: local-dual-model
description: 調用實驗室本地/Tailscale 雙模型伺服器 (100.109.10.60:8080)，支援 System 1 決策大腦 (Clef-flash 9B) 與 System 2 生成大腦 (Gemma 4 26B-A4B)。
---

# Local Dual Model (100.109.10.60:8080)

本 Skill 提供與本機／Tailscale 私網雙模型伺服器（M4 Mac mini，`100.109.10.60:8080`）的標準交互介面與腳本。
專為敏感資料處理、離線生醫分析、高頻機率決策與程式碼演化設計。

---

## 一、Second Brain 脈絡與參考文件

本 Skill 之架構設計、參數配置與金鑰規範嚴格對齊 Second Brain 核心決策紀錄。以下為 vault 相對路徑，用 `mcp__second-brain__read_note` 讀取（各電腦的 vault 掛載位置不同，不要寫成本機絕對路徑）：

1. **核心架構決策**：`decisions/clef-與-gemma4-雙核心個人-ai-架構決策.md`
   *(定義了 System 1 + System 2 雙核心架構、M4 Mac mini 24GB 顯存互斥管理、基準測試與落地場景)*
2. **連線與憑證管理**：`20-areas/coding/2026-09-05-huihui-qwen38-funnel-api-handoff.md`
   *(記錄了 Tailscale 連線、API 金鑰來源與 Windows 客戶端接入)*
3. **共享與演進歷史**：`30-resources/gemma-4-26b-遠端-windows-tailscale-使用指南-2026-10-02.md`

---

## 二、安全性與金鑰管理 (Zero-Leakage Guarantee)

- **防 Push 外流機制**：本 Skill 的任何文件與腳本**完全不包含明文金鑰**。
- **儲存位置**：金鑰儲存於本機 Windows 使用者登錄表環境變數：
  `HKCU\Environment\LOCAL_LLM_KEY`
- **動態解析**：腳本執行時自動經由 `os.environ.get("LOCAL_LLM_KEY")` 或直接向 Windows Registry 查詢，即使提交與推播（Push）程式庫至公開 GitHub 也絕無外洩風險。

---

## 三、雙大腦伺服器架構與特性

伺服器運行 `llama-server (b11913)` 之 Router 模式，配置 `--models-preset models.ini` 與 **`--models-max 1`** 進行嚴格顯存互斥排程：

| 角色定位 | 核心模型 | Model ID / Alias | 端點 (Endpoint) | 特性與效能數據 |
|---|---|---|---|---|
| **System 1：決策大腦**<br>*(分類、打分、路由、查核)* | **Cloudflare `Clef-flash` (9B)**<br>*(IQ4_XS + mmproj, ~5.0GB)* | `clef`<br>`clef-flash` | `POST /v1/systemone` | • **預設常駐**顯存，極低延遲。<br>• 單次 Forward pass 輸出 Brier Loss 校準機率（耗時約 1.3~1.9s）。<br>• **0 output tokens**（純機率計算，零多餘廢話）。 |
| **System 2：生成大腦**<br>*(推理、寫作、寫 Code)* | **Google `Gemma 4 26B-A4B`**<br>*(Q4_K_M + 430M 原生 MTP, ~16GB)* | `gemma4-26b-a4b`<br>`gemma4`<br>`huihui-qwen3.8-27b` | `POST /v1/chat/completions`<br>*(OpenAI 相容)* | • **按需換入顯存**：若前一請求為 Clef，自動淘汰 Clef 並從 SSD 載入 Gemma 4（冷載入約需 15 秒）。<br>• 生成吞吐約 **~34 tokens/s**（MTP 接受率約 70%）。<br>• 熱載入狀態下單次回應僅約 1~2 秒。 |

---

## 四、呼叫方式與內建腳本

Skill 內建標準調用腳本：[`scripts/call_model.py`](scripts/call_model.py)

以下範例中的 `<SKILL_DIR>` 是**本 SKILL.md 所在的目錄**（依客戶端不同，可能是 `~/.claude/skills/local-dual-model`、`~/.agents/skills/local-dual-model`、`~/.codex/skills/local-dual-model` 或 `~/.gemini/config/skills/local-dual-model`）。執行時換成實際載入本 Skill 的那個目錄，不要改用其他客戶端的副本。腳本只用標準函式庫，需 Python 3.10+。

### 1. CLI 呼叫範例

```bash
# 檢查模型掛載與常駐狀態
python "<SKILL_DIR>/scripts/call_model.py" --status

# 呼叫 System 2 (Gemma 4) 對話生成
python "<SKILL_DIR>/scripts/call_model.py" --chat "請用繁體中文總結本專案特點"

# 呼叫 System 1 (Clef) 是非判定 (noul)
python "<SKILL_DIR>/scripts/call_model.py" \
  --decide-noul "這份病理切片報告是否提及淋巴結轉移？" \
  --context "病理診斷：浸潤性導管癌，切片檢查顯示 3 顆哨兵淋巴結中未見癌細胞轉移..."

# 呼叫 System 1 (Clef) 5 級量表評分 (score)
python "<SKILL_DIR>/scripts/call_model.py" \
  --decide-score "評估此篇文獻之創新程度" \
  --context "本篇提出利用雙核心架構動態置換模型..."

# 呼叫 System 1 (Clef) 多分類選擇 (choice)
python "<SKILL_DIR>/scripts/call_model.py" \
  --decide-choice "這兩篇筆記的關聯屬性為何？" \
  --options 支持 矛盾 延伸 無關 \
  --context "筆記 A 主張 MTP 可提升 40% 速度；筆記 B 記錄在中文長篇測試中速度提升 18%..."
```

### 2. Python 模組直接匯入

```python
import sys
sys.path.append("<SKILL_DIR>/scripts")
from call_model import chat, decide_noul, decide_score, decide_choice

# 1. 呼叫 Gemma 4
reply = chat("請分析這段錯誤日誌", system_prompt="你是資深生醫工程師")

# 2. 呼叫 Clef 是非判定
is_ok = decide_noul("快取是否依然有效？", state="快取生成時間: 2小時前，資料來源無更新")

# 3. 呼叫 Clef 分類
relation = decide_choice("判斷關聯性", options=["支持", "矛盾", "無關"], state="內容對比...")
```

---

## 五、關鍵避坑指南 (Gotchas)

1. **System 1 `/v1/systemone` 的 Schema 規範**：
   - `type: "noul"`（是非）：僅需 `instructions`，回傳 `0.0 ~ 1.0` 的校準機率值。
   - `type: "score"`（評分）：**必須提供 `criteria: list[str]`**（2 到 10 級量表，由低至高），如 `["極差", "不良", "尚可", "良好", "極佳"]`。
     **回傳的 `score` 與 `probabilities` 鍵都是 0 起算的等級索引**（5 級量表為 `0`～`4`，`score` 是機率加權平均），不是 1～5。要對回標籤請用 `criteria[round(score)]`；`decide_score()` 已附上 `label` 與 `label_probabilities`。
   - `type: "choice"`（分類）：**必須提供 `criteria: dict[str, str]`**（非空物件，如 `{"A": "說明A", "B": "說明B"}` 或各標籤映射），缺漏會直接報 HTTP 400。
2. **互斥切換等待（避免逾時誤判）**：
   - 當常駐為 Clef 時，首次呼叫 `/v1/chat/completions` (Gemma 4) 需等待約 15 秒冷載入。
   - **客戶端 Timeout 請一律保持在 60 秒以上**，切勿在 15 秒內重送或判定斷線。
3. **中文編碼問題**：
   - Windows 終端機若直接以命令列組合非 ASCII JSON，易受終端 code page 截斷。請優先使用 `call_model.py` 或由 Python 透過 UTF-8 傳遞請求。

