import re
import subprocess


def run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except OSError as error:
        print(f"[release-notes] Could not run git {args[0]}: {error}")
        return ""


def get_repo_url() -> str:
    remote_url = run_git("remote", "get-url", "origin")
    if not remote_url:
        remote_url = "https://github.com/dyzulk/aacert.git"
    url = re.sub(r"^git@github\.com:", "https://github.com/", remote_url)
    return re.sub(r"\.git$", "", url)


def get_previous_formal_tag(current_tag: str):
    tags_output = run_git("tag", "--sort=-creatordate")
    if not tags_output:
        return None

    for tag in tags_output.splitlines():
        tag = tag.strip()
        if tag == current_tag:
            continue
        if re.search(r"(-staged|-rc|-alpha|-beta|-dev)", tag, re.IGNORECASE):
            continue
        if re.match(r"^v?\d+\.\d+\.\d+$", tag):
            return tag
    return None


def get_commit_range(target_version: str):
    previous_formal_tag = get_previous_formal_tag(target_version)
    target_ref = target_version
    if not run_git("rev-parse", "--verify", f"{target_version}^{{commit}}"):
        target_ref = "HEAD"

    if previous_formal_tag:
        revision_range = f"{previous_formal_tag}..{target_ref}"
        commit_logs = run_git(
            "log", revision_range, '--pretty=format:%h|%s|%an'
        )
    else:
        commit_logs = run_git(
            "log", target_ref, '--pretty=format:%h|%s|%an'
        )

    return previous_formal_tag, commit_logs
