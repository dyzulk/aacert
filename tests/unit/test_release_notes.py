import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPTS_PATH = Path(__file__).resolve().parents[2] / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from generate_release_notes.formatting import get_commit_subjects
from generate_release_notes.generator import generate_local_fallback_notes, generate_summary
from generate_release_notes.providers import call_groq_api


class TestReleaseNotes(unittest.TestCase):
    def test_local_fallback_uses_actual_commit_subjects(self):
        notes = generate_local_fallback_notes(
            "v1.2.3",
            "v1.2.2",
            "abc123|Fix DNS challenge retry|Ada\n"
            "def456|Update release workflow|Lin",
        )

        self.assertIn("### Changes since v1.2.2", notes)
        self.assertIn("- Fix DNS challenge retry", notes)
        self.assertIn("- Update release workflow", notes)
        self.assertNotIn("Seamless multi-provider ACME support", notes)

    def test_commit_subject_extraction_removes_emoji(self):
        subjects = get_commit_subjects("abc123|Fix renewal flow 🚀|Ada")

        self.assertEqual(subjects, ["Fix renewal flow"])

    @patch("generate_release_notes.providers.urllib.request.urlopen")
    def test_groq_api_sends_expected_request(self, urlopen):
        response = Mock()
        response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Release summary"}}]
        }).encode("utf-8")
        urlopen.return_value.__enter__.return_value = response

        result = call_groq_api("prompt text", "groq-secret")

        request = urlopen.call_args.args[0]
        self.assertEqual(result, "Release summary")
        self.assertEqual(request.full_url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer groq-secret")
        self.assertEqual(json.loads(request.data)["model"], "openai/gpt-oss-20b")

    @patch("generate_release_notes.generator.build_prompt", return_value="release prompt")
    @patch("generate_release_notes.generator.call_groq_api", return_value="Groq summary")
    @patch(
        "generate_release_notes.generator.call_gemini_api",
        side_effect=RuntimeError("Gemini unavailable"),
    )
    def test_uses_groq_when_gemini_fails(self, gemini, groq, build_prompt):
        summary = generate_summary(
            "v1.2.3",
            "v1.2.2",
            "abc123|Fix DNS challenge retry|Ada",
            "unused-template.md",
            "gemini-key",
            "groq-key",
        )

        self.assertEqual(summary, "Groq summary")
        gemini.assert_called_once_with("release prompt", "gemini-key")
        groq.assert_called_once_with("release prompt", "groq-key")
        build_prompt.assert_called_once()


if __name__ == "__main__":
    unittest.main()
