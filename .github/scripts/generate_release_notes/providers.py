import time

from .formatting import sanitize_no_emoji


GEMINI_CANDIDATE_MODELS = (
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
)
GEMINI_MAX_ATTEMPTS_PER_MODEL = 2


def get_gemini_client(api_key: str):
    try:
        from google import genai
    except ImportError as error:
        raise RuntimeError(
            "Google GenAI SDK is not installed; install "
            ".github/scripts/requirements-release-notes.txt"
        ) from error

    return genai.Client(
        api_key=api_key,
        http_options={
            "timeout": 30000,
            "retry_options": {"attempts": 1},
        },
    )


def redact_api_key(message: str, api_key: str) -> str:
    return message.replace(api_key, "[REDACTED]") if api_key else message


def call_gemini_api(prompt: str, api_key: str) -> str:
    last_error = None
    client = get_gemini_client(api_key)

    try:
        for model in GEMINI_CANDIDATE_MODELS:
            for attempt in range(1, GEMINI_MAX_ATTEMPTS_PER_MODEL + 1):
                try:
                    print(
                        f"[release-notes] Querying Gemini model {model} "
                        f"(attempt {attempt}/{GEMINI_MAX_ATTEMPTS_PER_MODEL})..."
                    )
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config={
                            "temperature": 0.2,
                            "max_output_tokens": 2048,
                        },
                    )
                    content = response.text
                    if content and content.strip():
                        print(
                            f"[release-notes] Successfully generated release "
                            f"notes with {model}."
                        )
                        return sanitize_no_emoji(content)
                    raise RuntimeError(f"{model} returned no text")

                except Exception as error:
                    print(
                        f"[release-notes] Gemini {model} attempt {attempt} "
                        f"error: {redact_api_key(str(error), api_key)}"
                    )
                    last_error = error

                    status_code = getattr(error, "code", None)
                    message = str(error).lower()
                    if status_code == 429 or "resource_exhausted" in message:
                        print(
                            "[release-notes] Gemini quota/rate limit reached; "
                            "skipping remaining Gemini models."
                        )
                        raise

                    model_unavailable = status_code == 404 or any(
                        marker in message
                        for marker in (
                            "model not found",
                            "model is not found",
                            "model is no longer available",
                            "model is not supported",
                        )
                    )
                    if model_unavailable:
                        print(
                            f"[release-notes] Skipping unavailable Gemini "
                            f"model {model}."
                        )
                        break

                    if status_code == 400:
                        print(
                            "[release-notes] Gemini rejected the request; "
                            "skipping remaining Gemini models."
                        )
                        raise

                    if status_code in (408, 500, 502, 503, 504) or any(
                        marker in type(error).__name__.lower()
                        for marker in ("timeout", "connection")
                    ):
                        if attempt < GEMINI_MAX_ATTEMPTS_PER_MODEL:
                            print(
                                f"[release-notes] Retrying transient Gemini "
                                f"error for {model} once."
                            )
                            time.sleep(attempt)
                            continue
                        print(
                            f"[release-notes] Skipping {model} after "
                            f"{GEMINI_MAX_ATTEMPTS_PER_MODEL} attempts."
                        )
                        break

                    if status_code in (401, 403):
                        print(
                            "[release-notes] Gemini authentication or access "
                            "was rejected; skipping remaining Gemini models."
                        )
                        raise

                    print(
                        f"[release-notes] Non-retryable Gemini error for "
                        f"{model}; moving to the next provider model."
                    )
                    break
    finally:
        client.close()

    raise last_error or RuntimeError(
        "Failed to generate response from all candidate Gemini models"
    )


def get_groq_client(api_key: str):
    try:
        from groq import Groq
    except ImportError as error:
        raise RuntimeError(
            "Groq Python SDK is not installed; install "
            ".github/scripts/requirements-release-notes.txt"
        ) from error

    return Groq(api_key=api_key, timeout=30, max_retries=2)


def call_groq_api(prompt: str, api_key: str) -> str:
    print("[release-notes] Querying Groq with the official Python SDK...")
    client = get_groq_client(api_key)
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_completion_tokens=2048,
    )
    content = completion.choices[0].message.content if completion.choices else None
    if not content or not content.strip():
        raise RuntimeError("Groq returned no text")

    print("[release-notes] Successfully generated release notes with Groq.")
    return sanitize_no_emoji(content)
