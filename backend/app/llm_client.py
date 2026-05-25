import json
import os
import re
import requests


def _get_token() -> str:
    auth_path = os.path.expanduser("~/.hermes/auth.json")
    if os.path.exists(auth_path):
        with open(auth_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            pool = data.get("credential_pool", {})
            oc = pool.get("opencode-go", [])
            if isinstance(oc, list) and len(oc) > 0:
                token = oc[0].get("access_token")
                if token:
                    return token
            elif isinstance(oc, dict):
                token = oc.get("access_token")
                if token:
                    return token
    raise RuntimeError("OpenCode Go token not found in ~/.hermes/auth.json")


def _get_endpoint() -> str:
    return "https://opencode.ai/zen/go/v1/chat/completions"


def chat_completion(prompt: str, model: str = "kimi-k2.6", max_tokens: int = 4000) -> str:
    token = _get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Origin": "https://opencode.ai",
        "Referer": "https://opencode.ai/",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    resp = requests.post(_get_endpoint(), headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return content


def extract_json(text: str) -> list:
    """Extract JSON array from markdown-fenced or raw LLM output."""
    text = text.strip()

    # 1. Try last fenced code block
    matches = list(re.finditer(r"```(?:json)?\n(.*?)\n```", text, re.DOTALL))
    if matches:
        for m in reversed(matches):
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                continue

    # 2. Find last balanced [...] by scanning backwards from the end
    # Start from the last ']' and walk back to find its matching '['
    last_bracket = text.rfind("]")
    if last_bracket == -1:
        return []

    depth = 0
    start = None
    for i in range(last_bracket, -1, -1):
        ch = text[i]
        if ch == "]" and i == last_bracket:
            depth = 1
        elif ch == "]":
            depth += 1
        elif ch == "[" and depth > 0:
            depth -= 1
            if depth == 0:
                start = i
                break

    if start is not None:
        try:
            return json.loads(text[start:last_bracket + 1])
        except json.JSONDecodeError:
            pass

    return []
