import time

from .formatting import sanitize_no_emoji


def get_gemini_client(api_key: str):
    try:
        from google import genai
    except ImportError as error:
        raise RuntimeError(
            "Google GenAI SDK is not installed; install "
            ".github/scripts/requirements-release-notes.txt"
        ) from error

    return genai.Client(api_key=api_key, http_options={"timeout": 30000})


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
    client = get_gemini_client(api_key)

    try:
        for model in candidate_models:
            for attempt in range(1, max_retries + 1):
                try:
                    print(
                        f"[release-notes] Querying Gemini model {model} "
                        f"(attempt {attempt}/{max_retries})..."
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
                        f"error: {error}"
                    )
                    last_error = error
                    status_code = getattr(error, "code", None)
                    if status_code in (400, 404):
                        break
                    if attempt < max_retries:
                        time.sleep(attempt)
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
