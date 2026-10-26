import re


EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50]",
    flags=re.UNICODE,
)


def sanitize_no_emoji(text: str) -> str:
    if not text:
        return ""
    return EMOJI_REGEX.sub("", text).strip()


def get_commit_subjects(commit_logs: str):
    subjects = []
    for line in commit_logs.splitlines():
        parts = line.split("|", 2)
        if len(parts) > 1 and parts[1].strip():
            subjects.append(sanitize_no_emoji(parts[1]))
    return subjects


def format_full_changelog(commit_logs: str, repo_url: str) -> str:
    if not commit_logs:
        return "_No commit history found._"

    formatted = []
    for line in commit_logs.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 2)
        commit_hash = parts[0].strip() if parts else ""
        subject = sanitize_no_emoji(parts[1]) if len(parts) > 1 else ""
        author = parts[2].strip() if len(parts) > 2 else ""
        formatted.append(
            f"- [`{commit_hash}`]({repo_url}/commit/{commit_hash}) - "
            f"{subject} (@{author})"
        )

    return "\n".join(formatted) or "_No commit history found._"
