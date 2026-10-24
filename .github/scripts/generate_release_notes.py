#!/usr/bin/env python3
# coding: utf-8
"""
==============================================================================
generate_release_notes.py
==============================================================================
Automated release notes generator for aacert.
Uses Google Gemini API with fallback to synthesize human-readable release notes.
Appends an exhaustive, hyperlinked ## Full Changelog section at the bottom.
Enforces zero-native-emojis policy across all generated notes.
Requires Python 3.8+ (zero external dependencies, uses standard library only).
==============================================================================
"""

import os
import sys
import re
import json
import time
import subprocess
import urllib.request
import urllib.error

# Regex to strip Unicode emoji glyphs
EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50]",
    flags=re.UNICODE
)


def sanitize_no_emoji(text: str) -> str:
    if not text:
        return ""
    return EMOJI_REGEX.sub("", text).strip()


def run_git(cmd: str) -> str:
    try:
        res = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return res.stdout.strip()
    except Exception:
        return ""


def get_repo_url() -> str:
    remote_url = run_git("git remote get-url origin")
    if not remote_url:
        remote_url = "https://github.com/dyzulk/aacert.git"
    url = re.sub(r"^git@github\.com:", "https://github.com/", remote_url)
    url = re.sub(r"\.git$", "", url)
    return url


def get_previous_formal_tag(current_tag: str):
    tags_output = run_git("git tag --sort=-creatordate")
    if not tags_output:
        return None

    tags = [t.strip() for t in tags_output.split("\n") if t.strip()]
    formal_tags = []
    for tag in tags:
        if tag == current_tag:
            continue
        if re.search(r"(-staged|-rc|-alpha|-beta|-dev)", tag, re.IGNORECASE):
            continue
        if re.match(r"^v?\d+\.\d+\.\d+$", tag):
            formal_tags.append(tag)

    return formal_tags[0] if formal_tags else None


def get_commit_range(target_version: str):
    previous_formal_tag = get_previous_formal_tag(target_version)
    has_ref = run_git(f'git rev-parse --verify "{target_version}^{{commit}}" 2>/dev/null')
    target_ref = target_version if has_ref else "HEAD"

    if previous_formal_tag:
        commit_logs = run_git(f'git log "{previous_formal_tag}..{target_ref}" --pretty=format:"%h|%s|%an"')
    else:
        commit_logs = run_git(f'git log "{target_ref}" --pretty=format:"%h|%s|%an"')

    return previous_formal_tag, commit_logs


def format_full_changelog(commit_logs: str, repo_url: str) -> str:
    if not commit_logs:
        return "_No commit history found._"

    lines = [l for l in commit_logs.split("\n") if l.strip()]
    formatted = []
    for line in lines:
        parts = line.split("|")
        h = parts[0].strip() if len(parts) > 0 else ""
        s = parts[1].strip() if len(parts) > 1 else ""
        a = parts[2].strip() if len(parts) > 2 else ""
        clean_s = sanitize_no_emoji(s)
        formatted.append(f"- [`{h}`]({repo_url}/commit/{h}) - {clean_s} (@{a})")

    return "\n".join(formatted)


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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }).encode("utf-8")

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[release-notes] Querying Gemini model {model} (attempt {attempt}/{max_retries})...")
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            content = parts[0]["text"]
                            print(f"[release-notes] Successfully generated release notes with {model}.")
                            return sanitize_no_emoji(content)

            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                print(f"[release-notes] {model} returned HTTP {e.code}: {err_body[:160]}")
                last_error = e
                if e.code in [400, 404]:
                    # Model not supported or unavailable, immediately break to try next model
                    break
                if attempt < max_retries:
                    time.sleep(attempt)
            except Exception as e:
                print(f"[release-notes] {model} attempt {attempt} error: {str(e)}")
                last_error = e
                if attempt < max_retries:
                    time.sleep(attempt)

    raise last_error or RuntimeError("Failed to generate response from all candidate Gemini models")


def generate_local_fallback_notes(version: str, previous_tag: str) -> str:
    return f"""## Release {version}

This release introduces core updates, stability improvements, and enhancements for **aacert** (Multi-CA ACME Manager for aaPanel).

### Highlights
- Seamless multi-provider ACME support (ZeroSSL, Google Public CA, SSL.com, Let's Encrypt).
- Safe runtime micro-patching of aaPanel's `acme_v2.py` with clean uninstaller rollback.
- Complete CLI tool suite with active CA status, configuration setup, and connectivity testing."""


def main():
    version = os.environ.get("VERSION") or (sys.argv[1] if len(sys.argv) > 1 else "HEAD")
    output_path = os.environ.get("OUTPUT_PATH") or (sys.argv[2] if len(sys.argv) > 2 else "release-notes.md")
    prompt_template_path = os.environ.get("PROMPT_TEMPLATE") or ".github/prompts/release-notes-prompt.md"
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    repo_url = get_repo_url()
    print(f"[release-notes] Target Version: {version}")
    print(f"[release-notes] Repository Base URL: {repo_url}")

    previous_tag, commit_logs = get_commit_range(version)
    baseline_desc = f"previous formal release: {previous_tag}" if previous_tag else "initial repository commit (full history)"
    print(f"[release-notes] Calculated baseline: {baseline_desc}")

    commit_messages_for_ai = []
    for l in commit_logs.split("\n"):
        parts = l.split("|")
        if len(parts) > 1 and parts[1].strip():
            clean_s = sanitize_no_emoji(parts[1])
            commit_messages_for_ai.append(f"- {clean_s}")
    commit_messages_str = "\n".join(commit_messages_for_ai) or "Initial release commit"

    formatted_full_changelog = format_full_changelog(commit_logs, repo_url)
    human_summary = ""

    if api_key:
        print("[release-notes] GEMINI_API_KEY detected. Synthesizing release notes via Gemini AI...")
        try:
            template_full_path = os.path.abspath(prompt_template_path)
            with open(template_full_path, "r", encoding="utf-8") as f:
                template = f.read()

            populated_prompt = template.replace("{{COMMIT_LOG}}", commit_messages_str).replace("{{VERSION}}", version)
            human_summary = call_gemini_api(populated_prompt, api_key)
            print("[release-notes] AI release note generation succeeded.")
        except Exception as e:
            print(f"[release-notes] AI generation failed ({str(e)}). Using local fallback.")
            human_summary = generate_local_fallback_notes(version, previous_tag)
    else:
        print("[release-notes] No GEMINI_API_KEY configured. Using local fallback.")
        human_summary = generate_local_fallback_notes(version, previous_tag)

    human_summary = sanitize_no_emoji(human_summary)
    final_release_notes = f"{human_summary}\n\n## Full Changelog\n\n{formatted_full_changelog}\n"

    out_full_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(out_full_path), exist_ok=True)
    with open(out_full_path, "w", encoding="utf-8") as f:
        f.write(final_release_notes)

    print(f"[release-notes] Release notes written to: {out_full_path}")


if __name__ == "__main__":
    main()
