#!/usr/bin/env python3
"""Run release-note generation with Gemini, Groq, or no AI.

Examples:
    python3 .github/scripts/test_release_notes.py --provider all
    python3 .github/scripts/test_release_notes.py --provider groq --env-file tmp/secret.env
"""

import argparse
import contextlib
import io
import os
from pathlib import Path

from generate_release_notes.generator import generate_release_notes


REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDERS = ("gemini", "groq", "none")
OUTPUT_NAMES = {
    "gemini": "output-gemini.md",
    "groq": "output-groq.md",
    "none": "output-no-ai.md",
}
SUCCESS_MESSAGES = {
    "gemini": "Successfully generated release notes with ",
    "groq": "Successfully generated release notes with Groq.",
}


def parse_env_file(env_file: Path) -> dict:
    values = {}
    if not env_file.is_file():
        raise FileNotFoundError(f"Environment file does not exist: {env_file}")

    for line_number, raw_line in enumerate(
        env_file.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            raise ValueError(
                f"Invalid environment assignment at {env_file}:{line_number}"
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(value[0]):
            value = value[1:-1]
        values[key] = value

    return values


def run_scenario(
    provider: str,
    version: str,
    output_dir: Path,
    prompt_template: str,
    gemini_api_key: str,
    groq_api_key: str,
) -> bool:
    output_path = output_dir / OUTPUT_NAMES[provider]
    selected_gemini_key = gemini_api_key if provider == "gemini" else ""
    selected_groq_key = groq_api_key if provider == "groq" else ""
    captured_output = io.StringIO()

    with contextlib.redirect_stdout(captured_output):
        generate_release_notes(
            version,
            str(output_path),
            prompt_template,
            selected_gemini_key,
            selected_groq_key,
        )

    log = captured_output.getvalue()
    for secret in (gemini_api_key, groq_api_key):
        if secret:
            log = log.replace(secret, "[REDACTED]")
    print(f"=== {provider} ===")
    print(log, end="" if log.endswith("\n") else "\n")

    if not output_path.is_file() or not output_path.read_text(
        encoding="utf-8"
    ).strip():
        print(f"[release-notes-test] No output was written to {output_path}")
        return False

    if provider in SUCCESS_MESSAGES and SUCCESS_MESSAGES[provider] not in log:
        print(
            f"[release-notes-test] {provider} did not generate the notes; "
            "the generator may have used its local fallback."
        )
        return False

    print(f"[release-notes-test] Output verified: {output_path}")
    return True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate release notes using selected AI providers for testing."
    )
    parser.add_argument(
        "--provider",
        choices=(*PROVIDERS, "all"),
        default="all",
        help="Provider to test; 'all' runs Gemini, Groq, then local fallback.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path("tmp/secret.env"),
        help="Local KEY=VALUE file (default: tmp/secret.env). Values are never printed.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp"),
        help="Directory for generated output files (default: tmp).",
    )
    parser.add_argument(
        "--version",
        default="HEAD",
        help="Version or Git ref to describe (default: HEAD).",
    )
    parser.add_argument(
        "--prompt-template",
        default=".github/prompts/release-notes-prompt.md",
        help="Prompt template path relative to the repository root.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    file_values = {}
    if args.env_file.is_file():
        try:
            file_values = parse_env_file(args.env_file)
        except (OSError, ValueError) as error:
            raise SystemExit(f"[release-notes-test] {error}") from error

    gemini_api_key = os.environ.get(
        "GEMINI_API_KEY", file_values.get("GEMINI_API_KEY", "")
    ).strip()
    groq_api_key = os.environ.get(
        "GROQ_API_KEY", file_values.get("GROQ_API_KEY", "")
    ).strip()

    selected = PROVIDERS if args.provider == "all" else (args.provider,)
    missing_keys = []
    if "gemini" in selected and not gemini_api_key:
        missing_keys.append("GEMINI_API_KEY")
    if "groq" in selected and not groq_api_key:
        missing_keys.append("GROQ_API_KEY")
    if missing_keys:
        raise SystemExit(
            "[release-notes-test] Missing non-empty key(s): "
            + ", ".join(missing_keys)
        )

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    failures = []
    for provider in selected:
        try:
            succeeded = run_scenario(
                provider,
                args.version,
                output_dir,
                str(REPO_ROOT / args.prompt_template),
                gemini_api_key,
                groq_api_key,
            )
        except Exception as error:
            message = str(error)
            for secret in (gemini_api_key, groq_api_key):
                if secret:
                    message = message.replace(secret, "[REDACTED]")
            print(f"[release-notes-test] {provider} test errored: {message}")
            succeeded = False
        if not succeeded:
            failures.append(provider)

    if failures:
        raise SystemExit(
            "[release-notes-test] Failed provider test(s): "
            + ", ".join(failures)
        )

    print("[release-notes-test] All selected scenarios passed.")


if __name__ == "__main__":
    main()
