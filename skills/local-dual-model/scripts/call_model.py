#!/usr/bin/env python3
"""
CLI & Helper script for interacting with the local dual-model server on Tailscale (100.109.10.60:8080).
Supports System 1 (Clef-flash decision engine) and System 2 (Gemma 4 26B-A4B generation engine).
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_HOST = "http://100.109.10.60:8080"


def get_api_key() -> str:
    """Safely retrieves the API key from environment or Windows registry."""
    # 1. Environment variable
    key = os.environ.get("LOCAL_LLM_KEY")
    if key and key.strip():
        return key.strip()

    # 2. Windows registry (User HKCU\Environment)
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as reg_key:
                val, _ = winreg.QueryValueEx(reg_key, "LOCAL_LLM_KEY")
                if val and val.strip():
                    return val.strip()
        except Exception:
            pass

    raise RuntimeError(
        "無法取得 API Key！請確認已設定環境變數 LOCAL_LLM_KEY 或在 Windows 登錄表中註冊。"
    )


def make_request(endpoint: str, data: dict | None = None, timeout: float = 60.0) -> dict:
    """Performs HTTP request with Authorization header."""
    url = f"{DEFAULT_HOST}{endpoint}"
    key = get_api_key()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json; charset=utf-8",
    }

    if data is not None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} Error: {err_msg}") from e
    except Exception as e:
        raise RuntimeError(f"連線至 {url} 失敗: {e}") from e


def get_status() -> dict:
    """Returns current server model status."""
    return make_request("/v1/models", timeout=10.0)


def chat(prompt: str, system_prompt: str | None = None, model: str = "gemma4-26b-a4b", max_tokens: int = 1024, temperature: float = 0.7) -> str:
    """Generates text using System 2 (Gemma 4)."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # Mutual exclusion switch can take up to ~20s if cold loading
    res = make_request("/v1/chat/completions", data=payload, timeout=90.0)
    return res["choices"][0]["message"]["content"]


def decide_noul(instruction: str, state: str, model: str = "clef") -> dict:
    """Performs boolean/yes-no probability judgment using System 1 (Clef)."""
    payload = {
        "model": model,
        "state": state,
        "questions": {
            "result": {
                "type": "noul",
                "instructions": instruction,
            }
        },
    }
    res = make_request("/v1/systemone", data=payload, timeout=30.0)
    answer = res.get("answers", {}).get("result", {})
    return {
        "probability_yes": answer.get("noul"),
        "raw_answer": answer,
        "usage": res.get("usage"),
    }


def decide_score(instruction: str, state: str, criteria: list[str] | None = None, model: str = "clef") -> dict:
    """Performs calibrated rating score judgment using System 1 (Clef)."""
    if criteria is None:
        criteria = ["極差", "不良", "尚可", "良好", "極佳"]

    payload = {
        "model": model,
        "state": state,
        "questions": {
            "result": {
                "type": "score",
                "instructions": instruction,
                "criteria": criteria,
            }
        },
    }
    res = make_request("/v1/systemone", data=payload, timeout=30.0)
    answer = res.get("answers", {}).get("result", {})
    # The server returns 0-based level indices: score is the probability-weighted
    # mean of 0..len(criteria)-1, and probabilities is keyed "0", "1", ...
    score = answer.get("score")
    probabilities = answer.get("probabilities")
    label = None
    if isinstance(score, (int, float)):
        label = criteria[min(max(round(score), 0), len(criteria) - 1)]
    label_probabilities = None
    if isinstance(probabilities, dict):
        label_probabilities = {
            criteria[int(k)]: v for k, v in probabilities.items() if str(k).isdigit() and int(k) < len(criteria)
        }
    return {
        "score": score,
        "label": label,
        "label_probabilities": label_probabilities,
        "probabilities": probabilities,
        "raw_answer": answer,
        "usage": res.get("usage"),
    }


def decide_choice(instruction: str, options: list[str] | dict[str, str], state: str, model: str = "clef") -> dict:
    """Performs categorical multi-choice classification using System 1 (Clef)."""
    if isinstance(options, list):
        criteria = {opt: opt for opt in options}
    else:
        criteria = options

    payload = {
        "model": model,
        "state": state,
        "questions": {
            "result": {
                "type": "choice",
                "instructions": instruction,
                "criteria": criteria,
            }
        },
    }
    res = make_request("/v1/systemone", data=payload, timeout=30.0)
    answer = res.get("answers", {}).get("result", {})
    return {
        "choice": answer.get("choice"),
        "probabilities": answer.get("probabilities"),
        "confidence": answer.get("confidence"),
        "raw_answer": answer,
        "usage": res.get("usage"),
    }



def main():
    parser = argparse.ArgumentParser(description="Local Dual Model Client (100.109.10.60:8080)")
    parser.add_argument("--status", action="store_true", help="檢查伺服器模型與掛載狀態")
    parser.add_argument("--chat", type=str, help="呼叫 System 2 (Gemma 4) 生成文字")
    parser.add_argument("--system", type=str, default=None, help="System Prompt")
    parser.add_argument("--decide-noul", type=str, help="呼叫 System 1 (Clef) 進行是非判定 (輸入問題)")
    parser.add_argument("--decide-score", type=str, help="呼叫 System 1 (Clef) 進行量表評分 (輸入評估指標)")
    parser.add_argument("--decide-choice", type=str, help="呼叫 System 1 (Clef) 進行類別分類 (輸入分類問題)")
    parser.add_argument("--options", type=str, nargs="+", default=[], help="類別分類選項 (搭配 --decide-choice 使用)")
    parser.add_argument("--context", type=str, default="", help="判定時的參考上下文 (state)")

    args = parser.parse_args()

    if args.status:
        st = get_status()
        print("=== 伺服器模型狀態 ===")
        for m in st.get("data", []):
            print(f"- 模型: {m.get('id')} | 狀態: {m.get('status', {}).get('value')} | 別名: {m.get('aliases')}")
        return

    if args.chat:
        print(f"[呼叫 Gemma 4] Prompt: {args.chat}")
        t0 = time.time()
        reply = chat(args.chat, system_prompt=args.system)
        print(f"\n[模型回覆] (耗時: {time.time() - t0:.2f}s):\n{reply}")
        return

    if args.decide_noul:
        t0 = time.time()
        res = decide_noul(args.decide_noul, state=args.context)
        print(f"=== System 1 是非判定 (耗時: {time.time() - t0:.2f}s) ===")
        prob = res.get("probability_yes")
        print(f"問題: {args.decide_noul}")
        if not isinstance(prob, (int, float)):
            print(f"錯誤：伺服器未回傳 noul 機率，原始回應: {res.get('raw_answer')}")
            sys.exit(1)
        print(f"肯定機率 (Probability YES): {prob * 100:.2f}%")
        print(f"判定建議: {'【是 (YES)】' if prob >= 0.5 else '【否 (NO)】'}")
        return

    if args.decide_score:
        t0 = time.time()
        res = decide_score(args.decide_score, state=args.context)
        print(f"=== System 1 量表評分 (耗時: {time.time() - t0:.2f}s) ===")
        print(f"指標: {args.decide_score}")
        score = res.get("score")
        if not isinstance(score, (int, float)):
            print(f"錯誤：伺服器未回傳 score，原始回應: {res.get('raw_answer')}")
            sys.exit(1)
        print(f"評分 (0~4，0 起算): {score:.2f} → {res.get('label')}")
        print("機率分佈:", res.get("label_probabilities") or res.get("probabilities"))
        return

    if args.decide_choice:
        if not args.options:
            print("錯誤：使用 --decide-choice 時必須提供 --options 選項，例如: --options 支持 矛盾 延伸 無關")
            sys.exit(1)
        t0 = time.time()
        res = decide_choice(args.decide_choice, options=args.options, state=args.context)
        print(f"=== System 1 類別分類 (耗時: {time.time() - t0:.2f}s) ===")
        print(f"問題: {args.decide_choice}")
        print(f"分類結果: {res.get('choice')}")
        print("各選項機率分佈:", res.get("probabilities"))
        return


    parser.print_help()


if __name__ == "__main__":
    main()
