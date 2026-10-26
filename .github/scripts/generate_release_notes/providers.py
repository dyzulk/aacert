import json
import time
import urllib.error
import urllib.request

from .formatting import sanitize_no_emoji


def call_gemini_api(prompt: str, api_key: str) -> str:
    candidate_models = [
        "gemini-flash-latest",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]
    max_retries = 3
    last_error = None

    for model in candidate_models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
        }).encode("utf-8")

        for attempt in range(1, max_retries + 1):
            try:
                print(
                    f"[release-notes] Querying Gemini model {model} "
                    f"(attempt {attempt}/{max_retries})..."
                )
                request = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(request, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and parts[0].get("text"):
                        print(
                            f"[release-notes] Successfully generated release "
                            f"notes with {model}."
                        )
                        return sanitize_no_emoji(parts[0]["text"])
                raise RuntimeError(f"{model} returned no text")

            except urllib.error.HTTPError as error:
                body = error.read().decode("utf-8", errors="ignore")
                print(
                    f"[release-notes] Gemini {model} returned HTTP "
                    f"{error.code}: {body[:160]}"
                )
                last_error = error
                if error.code in (400, 404):
                    break
                if attempt < max_retries:
                    time.sleep(attempt)
            except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError) as error:
                print(f"[release-notes] Gemini {model} attempt {attempt} error: {error}")
                last_error = error
                if attempt < max_retries:
                    time.sleep(attempt)

    raise last_error or RuntimeError(
        "Failed to generate response from all candidate Gemini models"
    )


def call_groq_api(prompt: str, api_key: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 2048,
    }).encode("utf-8")
    for attempt in range(1, 4):
        try:
            print(f"[release-notes] Querying Groq (attempt {attempt}/3)...")
            request = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content")
                if content and content.strip():
                    print("[release-notes] Successfully generated release notes with Groq.")
                    return sanitize_no_emoji(content)
            raise RuntimeError("Groq returned no text")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="ignore")
            print(f"[release-notes] Groq returned HTTP {error.code}: {body[:160]}")
            if error.code not in (408, 429, 500, 502, 503, 504) or attempt == 3:
                raise
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError):
            if attempt == 3:
                raise
        time.sleep(attempt)

    raise RuntimeError("Failed to generate response from Groq")
