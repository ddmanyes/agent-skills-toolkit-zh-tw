"""
generate_prompt.py
將圖片傳給本地 llama-server 相容端點，回傳雙語圖片描述 prompt；模型身分與視覺能力由實際服務決定。

用法：
    python generate_prompt.py <image_path> [mode] [extra_prompt]

mode：
    manga   （預設）雙語 novel_to_manga 格式 prompt
    flux    純英文 FLUX 出圖指令
    describe 純中文場景描述
    fidelity 高保真描述（盡量貼圖、不腦補）
    f2m     先高保真觀察，再轉為雙語 manga prompt
"""

import sys
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path

LLAMA_URL = "http://localhost:8080/v1/chat/completions"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SYSTEM_MANGA = """You are a bilingual image prompt engineer for FLUX diffusion models.
Analyze the provided image and output a rich bilingual description in this EXACT format:

English (natural description):
- 8-12 sentences, 140-240 English words.
- Sentence 1 MUST start with the correct person-count token: "ddwoman" (solo female), "awei" (solo male), "ddwoman and awei" (two people), "empty scene" (no people).
- Cover all details: shot type + framing distance, body posture, facial expression, hair, clothing material/texture/color, accessories, hand/object interaction, lighting direction and color temperature, background objects, depth/layers, camera angle/lens feel, mood, and style cues.

中文（自然描写）：
- 8-12 句，完整翻譯並保留細節，不要只寫摘要。

Then on a new line output JSON metadata with these keys only:
{"shot":"...","framing":"...","angle":"...","mood":"...","lighting":"...","orientation":"portrait|landscape","has_character":true|false,"character_count":0|1|2,"appearance":"...","clothing":"...","background":"...","style_tags":["...","..."]}

Quality constraints (CRITICAL):
- Do not be vague. Avoid short generic lines like "a woman in a room".
- Describe visible details; omit uncertain specifics or mark them unclear. Do not invent facts to satisfy the format.
- Do not output markdown code fences.
- For two people, describe their spatial relationship explicitly.
- Never combine contradictory shot terms (full body + extreme close-up).
"""

SYSTEM_FLUX = """You are an expert image prompt engineer for FLUX diffusion models.
Analyze the provided image and output a clean English prompt for FLUX image generation.
- 80-120 words
- Start with person count: "ddwoman" / "awei" / "ddwoman and awei" / "empty scene"
- Include: shot type, appearance, pose, clothing, lighting, background, style tags
- End with: photorealistic, 8k, sharp focus
- NO Chinese characters, NO markdown
"""

SYSTEM_DESCRIBE = """你是一位專業的圖像分析師。
請用中文詳細描述這張圖片的內容，包含：
- 畫面中的人物（外觀、服裝、表情、動作）
- 場景與環境
- 光線與氛圍
- 構圖與鏡頭感
輸出純中文描述，約 150-200 字。
"""

SYSTEM_FIDELITY = """你是高保真圖像描述器。目標是「只描述可見事實」，避免腦補。
請用繁體中文輸出，並遵守：
- 先列 8-15 條「可直接觀察到的事實」（若看不清楚就寫看不清楚，不可猜測）。
- 再寫一段 120-220 字的整體描述。
- 禁止加入圖片中未明確可見的人物關係、情節、年代、地點推測。
- 若使用者額外提示與圖片衝突，以圖片可見事實為準。
"""

def encode_image(image_path: str) -> tuple:
    """回傳 (base64_str, mime_type)"""
    path = Path(image_path)
    if not path.is_file():
        print(f"錯誤：找不到圖片 {image_path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
        ".gif": "image/gif",
    }
    if suffix not in mime_map:
        raise ValueError(f"Unsupported image extension: {suffix}")
    mime = mime_map[suffix]

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return b64, mime


def _extract_english_word_count(content: str) -> int:
    marker = "English (natural description):"
    zh_marker = "中文（自然描写）："
    if marker not in content:
        return 0

    start = content.find(marker) + len(marker)
    end = content.find(zh_marker, start)
    english_part = content[start:end].strip() if end != -1 else content[start:].strip()
    return len([w for w in english_part.replace("\n", " ").split(" ") if w.strip()])


def _looks_truncated(content: str, mode: str) -> bool:
    text = (content or "").strip()
    if not text:
        return True

    # 常見中斷跡象：句尾未收斂、結構未完整
    if mode == "manga":
        if "English (natural description):" not in text:
            return True
        if "中文（自然描写）：" not in text:
            return True
        if "{" not in text or "}" not in text:
            return True
    last_char = text[-1]
    return last_char not in "。！？.!?}"


def _normalize_manga_output(content: str) -> str:
    """去除續寫重複，保留最後一份完整 manga 區塊。"""
    marker = "English (natural description):"
    if marker not in content:
        return content.strip()

    idx = content.rfind(marker)
    normalized = content[idx:].strip()

    # 若有多個 JSON 起始，保留最後一個完整 JSON 區塊之前的文字 + 最後 JSON
    json_start = normalized.rfind("{")
    json_end = normalized.rfind("}")
    if json_start != -1 and json_end != -1 and json_end > json_start:
        prefix = normalized[:json_start].rstrip()
        json_part = normalized[json_start:json_end + 1]
        normalized = f"{prefix}\n{json_part}".strip()

    return normalized


def _extract_json_tail(text: str) -> str:
    start = text.rfind("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end + 1].strip()


def _extract_manga_sections(content: str) -> tuple:
    marker_en = "English (natural description):"
    marker_zh = "中文（自然描写）："
    text = (content or "").strip()
    if marker_en not in text or marker_zh not in text:
        return "", "", ""

    en_start = text.find(marker_en) + len(marker_en)
    zh_start = text.find(marker_zh, en_start)
    if zh_start == -1:
        return "", "", ""

    en_text = text[en_start:zh_start].strip()
    json_start = text.rfind("{")
    json_end = text.rfind("}")
    if json_start == -1 or json_end == -1 or json_end <= json_start:
        return "", "", ""

    zh_text = text[zh_start + len(marker_zh):json_start].strip()
    json_text = text[json_start:json_end + 1].strip()
    return en_text, zh_text, json_text


def _translate_en_to_zh_tw_faithful(en_text: str) -> str:
    system = """你是專業翻譯。請將英文段落翻成繁體中文，嚴格遵守：
- 忠實翻譯，不新增、不刪減、不改寫細節。
- 保留鏡頭語意、構圖、光線、姿態、服裝與氛圍描述。
- 不輸出任何前後解釋，只輸出翻譯後段落。
"""
    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"請翻譯以下內容為繁體中文，保持語義完整：\n\n{en_text}"
        }
    ]

    translated, finish_reason = _post_chat(messages, max_tokens=1400)
    attempts = 0
    while attempts < 2:
        text = translated.strip()
        if len(text) >= 80 and text[-1] in "。！？.!?」』":
            break
        if finish_reason != "length" and len(text) >= 80:
            break

        attempts += 1
        messages.append({"role": "assistant", "content": translated})
        messages.append({"role": "user", "content": "請緊接上一句繼續翻譯到自然收尾，不要重複前文。"})
        more, finish_reason = _post_chat(messages, max_tokens=1000)
        if more:
            translated = (translated.rstrip() + more.lstrip()).strip()

    return translated.strip()


def _force_manga_bilingual_alignment(content: str) -> str:
    en_text, _, json_text = _extract_manga_sections(content)
    if not en_text or not json_text:
        return content

    try:
        parsed = json.loads(json_text)
    except Exception:
        return content

    zh_text = _translate_en_to_zh_tw_faithful(en_text)
    if not zh_text:
        return content

    if zh_text[-1] not in "。！？.!?」』" or len(zh_text) < 80:
        return content

    json_compact = json.dumps(parsed, ensure_ascii=False)
    return (
        "English (natural description):\n"
        f"{en_text}\n\n"
        "中文（自然描写）：\n"
        f"{zh_text}\n"
        f"{json_compact}"
    )


def _build_comfy_safe_block(content: str, mode: str) -> str:
    """產生可直接貼入 ComfyUI 的安全提示，避免 JSON 鍵名被當成畫面文字。"""
    negative = (
        "text, letters, words, logo, watermark, signature, subtitle, caption, typography, "
        "chinese characters, english characters"
    )

    if mode in ("manga", "f2m"):
        en_text, _, _ = _extract_manga_sections(content)
        positive = " ".join(en_text.split()) if en_text else ""
    elif mode == "flux":
        positive = " ".join((content or "").split())
    else:
        return ""

    if not positive:
        return ""

    return (
        "\n\nComfy Safe Prompt:\n"
        f"{positive}\n\n"
        "Comfy Negative Prompt:\n"
        f"{negative}"
    )


def _is_manga_complete(content: str) -> bool:
    text = (content or "").strip()
    if not text:
        return False
    if "English (natural description):" not in text:
        return False
    if "中文（自然描写）：" not in text:
        return False

    json_tail = _extract_json_tail(text)
    if not json_tail:
        return False

    try:
        parsed = json.loads(json_tail)
        if not isinstance(parsed, dict):
            return False
        required = {"shot", "framing", "angle", "mood", "lighting", "orientation", "has_character", "character_count", "appearance", "clothing", "background", "style_tags"}
        if not required.issubset(parsed):
            return False
        if parsed["orientation"] not in {"portrait", "landscape"}:
            return False
        if not isinstance(parsed["has_character"], bool) or type(parsed["character_count"]) is not int:
            return False
        if parsed["character_count"] < 0 or not isinstance(parsed["style_tags"], list):
            return False
    except Exception:
        return False

    zh_start = text.find("中文（自然描写）：") + len("中文（自然描写）：")
    zh_end = text.rfind("{")
    zh_part = text[zh_start:zh_end].strip() if zh_end > zh_start else ""
    if len(zh_part) < 80:
        return False
    if zh_part[-1] not in "。！？.!?」』":
        return False

    return True


def _post_chat(messages, max_tokens: int) -> tuple:
    payload = {
        "model": "local-model",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    last_err = None
    for _ in range(2):
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                result = json.loads(resp.read())
            break
        except (TimeoutError, urllib.error.URLError) as e:
            last_err = e
            continue
    else:
        raise last_err

    choice = result["choices"][0]
    content = choice["message"].get("content", "").strip()
    finish_reason = choice.get("finish_reason", "")
    return content, finish_reason


def _request_once(image_path: str, mode: str = "manga", retry: bool = False, extra_prompt: str = "") -> str:
    system_map = {
        "manga":    SYSTEM_MANGA,
        "flux":     SYSTEM_FLUX,
        "describe": SYSTEM_DESCRIBE,
        "fidelity": SYSTEM_FIDELITY,
        "f2m":      SYSTEM_FIDELITY,
    }
    system = system_map.get(mode, SYSTEM_MANGA)

    user_text_map = {
        "manga":    "Analyze this image and generate a detailed bilingual manga storyboard prompt with dense visual details.",
        "flux":     "Analyze this image and generate a FLUX image generation prompt.",
        "describe": "請詳細描述這張圖片的內容。",
        "fidelity": "請僅根據可見內容做高保真描述，避免推測與新增元素。",
        "f2m":      "請僅根據可見內容做高保真描述，避免推測與新增元素。",
    }
    user_text = user_text_map.get(mode, user_text_map["manga"])
    if retry and mode == "manga":
        user_text += " Ensure the English section is at least 140 words and includes concrete clothing, lighting, and background details."
    if extra_prompt.strip():
        user_text += f"\n\nAdditional user requirements:\n{extra_prompt.strip()}"

    b64, mime = encode_image(image_path)

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"}
                },
                {"type": "text", "text": user_text}
            ]
        }
    ]

    max_tokens_map = {
        "manga": 1400,
        "flux": 900,
        "describe": 1200,
        "fidelity": 1300,
        "f2m": 1300,
    }
    max_tokens = max_tokens_map.get(mode, 1200)

    try:
        content, finish_reason = _post_chat(messages, max_tokens)
    except urllib.error.URLError as e:
        print(f"連線失敗：{e}", file=sys.stderr)
        print("請檢查實際服務錯誤與視覺支援；health 成功不能確認 mmproj 已載入。", file=sys.stderr)
        sys.exit(1)

    # 如果因長度或截斷造成不完整，嘗試續寫最多 2 次。
    attempts = 0
    while attempts < 2 and (finish_reason == "length" or _looks_truncated(content, mode)):
        attempts += 1
        messages.append({"role": "assistant", "content": content})
        if mode == "describe":
            cont_text = "請緊接上一句繼續完整描述到自然收尾，不要重複前文。"
        elif mode == "manga":
            cont_text = "請從中斷處繼續，補齊完整格式（英文段落、中文段落、最後 JSON）。不要重複前文。"
        else:
            cont_text = "Continue from exactly where you stopped and finish naturally. Do not repeat previous text."
        messages.append({"role": "user", "content": cont_text})

        more, finish_reason = _post_chat(messages, max_tokens)
        if more:
            content = (content.rstrip() + "\n" + more.lstrip()).strip()

    # 移除 thinking 標籤（Gemma 有時會輸出）
    if "<think>" in content:
        end = content.find("</think>")
        if end != -1:
            content = content[end + len("</think>"):].strip()

    return content


def _rewrite_manga_from_notes(notes_zh: str) -> str:
    """當視覺直出不穩定時，改用描述筆記進行二次重寫。"""
    system = """You are a bilingual image prompt engineer.
Convert provided scene notes into this exact output format:

English (natural description):
- 8-12 sentences, 140-240 words.
- First sentence starts with one token: ddwoman / awei / ddwoman and awei / empty scene.

中文（自然描写）：
- 8-12句，完整且細節具體。

Then output one-line JSON metadata with keys only:
{"shot":"...","framing":"...","angle":"...","mood":"...","lighting":"...","orientation":"portrait|landscape","has_character":true|false,"character_count":0|1|2,"appearance":"...","clothing":"...","background":"...","style_tags":["...","..."]}

Do not output markdown code fences.
"""

    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": f"Scene notes (Chinese):\n{notes_zh}\n\nPlease generate the final bilingual manga prompt now."
            }
        ],
        "temperature": 0.3,
        "max_tokens": 1100,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())

    content = result["choices"][0]["message"].get("content", "").strip()
    return content


def call_vision(image_path: str, mode: str = "manga", extra_prompt: str = "") -> str:
    original_mode = mode

    if mode == "f2m":
        # 第一步：高保真觀察
        notes = _request_once(image_path, "fidelity", retry=False, extra_prompt=extra_prompt)
        if not notes.strip():
            notes = _request_once(image_path, "describe", retry=False, extra_prompt=extra_prompt)

        # 第二步：轉換為雙語 manga
        rewritten = _rewrite_manga_from_notes(notes)
        rewritten = _normalize_manga_output(rewritten)
        rewritten = _force_manga_bilingual_alignment(rewritten)

        if _is_manga_complete(rewritten):
            # 分層輸出：高保真觀察 → 最終 manga → ComfyUI prompt
            safe_block = _build_comfy_safe_block(rewritten, original_mode)
            output = (
                "=== 📋 高保真觀察（可見事實） ===\n"
                f"{notes}\n\n"
                "=== 🎬 轉換後的雙語 Manga Prompt ===\n"
                f"{rewritten}\n"
                f"{safe_block}"
            )
            return output.strip()
        # 若二次重寫仍不完整，回退到一般 manga 流程
        mode = "manga"

    content = _request_once(image_path, mode, retry=False, extra_prompt=extra_prompt)
    if mode == "manga" and _extract_english_word_count(content) < 110:
        content = _request_once(image_path, mode, retry=True, extra_prompt=extra_prompt)

    if mode == "manga" and (_extract_english_word_count(content) < 80 or not _is_manga_complete(_normalize_manga_output(content))):
        # Fallback: vision->describe（通常較穩）後再二次重寫成 manga 格式
        notes = _request_once(image_path, "describe", retry=False, extra_prompt=extra_prompt)
        if notes.strip():
            rewritten = _rewrite_manga_from_notes(notes)
            rewritten_norm = _normalize_manga_output(rewritten)
            if _extract_english_word_count(rewritten_norm) >= 80 and _is_manga_complete(rewritten_norm):
                content = rewritten

    if mode == "manga":
        content = _normalize_manga_output(content)
        content = _force_manga_bilingual_alignment(content)

    safe_block = _build_comfy_safe_block(content, original_mode)
    if safe_block:
        content = (content + safe_block).strip()

    return content


def check_server_vision() -> bool:
    """Legacy name: check server health only; this does not verify vision support."""
    try:
        with urllib.request.urlopen("http://localhost:8080/health", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print("Usage: python generate_prompt.py <image_path> [manga|flux|describe|fidelity|f2m] [extra_prompt]")
        return 0 if args else 2
    image_path = str(Path(args[0]).expanduser().resolve())
    mode = args[1] if len(args) > 1 else "manga"
    extra_prompt = " ".join(args[2:]).strip()
    if mode not in {"manga", "flux", "describe", "fidelity", "f2m"}:
        print(f"Unsupported mode: {mode}", file=sys.stderr)
        return 2
    path = Path(image_path)
    if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        print(f"Image is missing or has an unsupported extension: {image_path}", file=sys.stderr)
        return 2
    if not check_server_vision():
        print("llama-server health check failed at http://localhost:8080. Verify the actual service configuration; no model launcher is assumed.", file=sys.stderr)
        return 1
    try:
        result = call_vision(image_path, mode, extra_prompt=extra_prompt)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print(f"Image request failed: {exc}. Server health alone does not verify vision capability.", file=sys.stderr)
        return 1
    if not result or not result.strip():
        print("Image request returned no content; vision capability and model identity remain unverified.", file=sys.stderr)
        return 1
    print(result)
    if mode in {"manga", "f2m"} and not _is_manga_complete(result):
        print("Partial output: bilingual sections or JSON are incomplete. Do not import as a completed storyboard.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
