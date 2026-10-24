
#!/usr/bin/env python3

import json
import os
import sys
import time
import urllib.error
import urllib.request


MAX_ATTEMPTS = 3
TIMEOUT = 30


def main() -> int:
    tag = os.environ.get("TAG", "").strip()
    repository = os.environ.get("REPOSITORY", "").strip()

    if not tag or not repository:
        print("::error::TAG and REPOSITORY are required.")
        return 1

    if not tag.startswith("v"):
        print(f"::error::Invalid release tag: {tag}")
        return 1

    file_path = f"/gh/{repository}@{tag}/setup.sh"
    purge_url = f"https://purge.jsdelivr.net{file_path}"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Purge attempt {attempt}/{MAX_ATTEMPTS}: {purge_url}")

        request = urllib.request.Request(
            purge_url,
            headers={"User-Agent": "aacert-release-workflow"},
        )

        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                body = response.read().decode("utf-8")
                status_code = response.status

        except urllib.error.HTTPError as error:
            status_code = error.code
            body = error.read().decode("utf-8", errors="replace")

        except (urllib.error.URLError, TimeoutError) as error:
            print(f"::warning::jsDelivr request failed: {error}")

            if attempt < MAX_ATTEMPTS:
                time.sleep(10)
                continue

            return 1

        print(f"HTTP status: {status_code}")
        print(body)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            print("::warning::jsDelivr returned a non-JSON response.")
            return 1

        if not isinstance(payload, dict):
            print("::warning::Unexpected jsDelivr response format.")
            return 1

        if payload.get("throttled") is True:
            reset = payload.get("throttlingReset", 60)

            try:
                wait_seconds = max(1, int(reset)) + 5
            except (TypeError, ValueError):
                wait_seconds = 65

            if attempt == MAX_ATTEMPTS:
                print("::warning::jsDelivr purge remained throttled.")
                return 1

            print(f"Rate limited. Retrying in {wait_seconds} seconds.")
            time.sleep(wait_seconds)
            continue

        if not 200 <= status_code < 300:
            print("::warning::jsDelivr purge request failed.")
            return 1

        if payload.get("status") in {"error", "failed"}:
            print("::warning::jsDelivr reported a purge failure.")
            return 1

        if payload.get("error"):
            print(f"::warning::jsDelivr error: {payload['error']}")
            return 1

        print("jsDelivr purge request completed successfully.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
