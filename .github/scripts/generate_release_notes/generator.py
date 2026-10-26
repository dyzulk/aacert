import os
import sys
from typing import Callable, Optional

from .formatting import (
    format_full_changelog,
    get_commit_subjects,
    sanitize_no_emoji,
)
from .git_data import get_commit_range, get_repo_url
from .providers import call_gemini_api, call_groq_api


def generate_local_fallback_notes(
    version: str, previous_tag: str, commit_logs: str
) -> str:
    subjects = get_commit_subjects(commit_logs)
    if not subjects:
        changes = "- No commit subjects were available for this release."
    else:
        changes = "\n".join(f"- {subject}" for subject in subjects)

    baseline = f" since {previous_tag}" if previous_tag else ""
    return f"""## Release {version}

### Changes{baseline}
{changes}"""


def build_prompt(template_path: str, version: str, commit_logs: str) -> str:
    with open(os.path.abspath(template_path), "r", encoding="utf-8") as template_file:
        template = template_file.read()

    commit_messages = get_commit_subjects(commit_logs)
    commit_log = "\n".join(f"- {subject}" for subject in commit_messages)
    return template.replace(
        "{{COMMIT_LOG}}", commit_log or "Initial release commit"
    ).replace("{{VERSION}}", version)


def generate_summary(
    version: str,
    previous_tag: str,
    commit_logs: str,
    prompt_template_path: str,
    gemini_api_key: str,
    groq_api_key: str,
    on_provider_success: Optional[Callable[[str], None]] = None,
) -> str:
    providers = []
    if gemini_api_key:
        providers.append(("Gemini", call_gemini_api, gemini_api_key))
    if groq_api_key:
        providers.append(("Groq", call_groq_api, groq_api_key))

    if providers:
        try:
            prompt = build_prompt(prompt_template_path, version, commit_logs)
        except OSError as error:
            print(f"[release-notes] Could not read prompt template: {error}")
            prompt = None

        if prompt is not None:
            for provider_name, generate, api_key in providers:
                try:
                    print(f"[release-notes] Generating release notes with {provider_name}...")
                    summary = generate(prompt, api_key)
                    if on_provider_success is not None:
                        on_provider_success(provider_name.lower())
                    return summary
                except Exception as error:
                    message = str(error).replace(api_key, "[REDACTED]")
                    print(
                        f"[release-notes] {provider_name} generation failed: "
                        f"{message}"
                    )

    print("[release-notes] Using local commit-based fallback.")
    return generate_local_fallback_notes(version, previous_tag, commit_logs)


def generate_release_notes(
    version: str,
    output_path: str,
    prompt_template_path: str,
    gemini_api_key: str,
    groq_api_key: str,
    on_provider_success: Optional[Callable[[str], None]] = None,
) -> str:
    repo_url = get_repo_url()
    print(f"[release-notes] Target Version: {version}")
    print(f"[release-notes] Repository Base URL: {repo_url}")

    previous_tag, commit_logs = get_commit_range(version)
    baseline = (
        f"previous formal release: {previous_tag}"
        if previous_tag
        else "initial repository commit (full history)"
    )
    print(f"[release-notes] Calculated baseline: {baseline}")

    summary = generate_summary(
        version,
        previous_tag,
        commit_logs,
        prompt_template_path,
        gemini_api_key,
        groq_api_key,
        on_provider_success,
    )
    final_notes = (
        f"{sanitize_no_emoji(summary)}\n\n## Full Changelog\n\n"
        f"{format_full_changelog(commit_logs, repo_url)}\n"
    )

    output_full_path = os.path.abspath(output_path)
    output_directory = os.path.dirname(output_full_path)
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)
    with open(output_full_path, "w", encoding="utf-8") as output_file:
        output_file.write(final_notes)
    print(f"[release-notes] Release notes written to: {output_full_path}")
    return final_notes


def main():
    version = os.environ.get("VERSION") or (
        sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    )
    output_path = os.environ.get("OUTPUT_PATH") or (
        sys.argv[2] if len(sys.argv) > 2 else "release-notes.md"
    )
    prompt_template_path = os.environ.get(
        "PROMPT_TEMPLATE", ".github/prompts/release-notes-prompt.md"
    )

    generate_release_notes(
        version,
        output_path,
        prompt_template_path,
        os.environ.get("GEMINI_API_KEY", "").strip(),
        os.environ.get("GROQ_API_KEY", "").strip(),
    )
