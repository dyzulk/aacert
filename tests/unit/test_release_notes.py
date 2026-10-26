import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPTS_PATH = Path(__file__).resolve().parents[2] / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from generate_release_notes.formatting import get_commit_subjects
from generate_release_notes.generator import generate_local_fallback_notes, generate_summary
from generate_release_notes.providers import call_gemini_api, call_groq_api
from test_release_notes import parse_env_file


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

    def test_env_file_parser_reads_quoted_values(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / "secrets.env"
            env_file.write_text(
                "# local API keys\nGEMINI_API_KEY='gemini-value'\n"
                "export GROQ_API_KEY=\"groq-value\"\n",
                encoding="utf-8",
            )

            values = parse_env_file(env_file)

        self.assertEqual(values, {
            "GEMINI_API_KEY": "gemini-value",
            "GROQ_API_KEY": "groq-value",
        })

    @patch("generate_release_notes.providers.get_gemini_client")
    def test_gemini_api_uses_official_sdk(self, get_gemini_client):
        response = Mock(text="Gemini release summary")
        client = Mock()
        client.models.generate_content.return_value = response
        get_gemini_client.return_value = client

        result = call_gemini_api("prompt text", "gemini-secret")

        self.assertEqual(result, "Gemini release summary")
        get_gemini_client.assert_called_once_with("gemini-secret")
        client.models.generate_content.assert_called_once_with(
            model="gemini-flash-latest",
            contents="prompt text",
            config={"temperature": 0.2, "max_output_tokens": 2048},
        )
        client.close.assert_called_once_with()

    @patch("generate_release_notes.providers.get_groq_client")
    def test_groq_api_uses_official_sdk(self, get_groq_client):
        completion = Mock()
        completion.choices = [Mock(message=Mock(content="Release summary"))]
        client = Mock()
        client.chat.completions.create.return_value = completion
        get_groq_client.return_value = client

        result = call_groq_api("prompt text", "groq-secret")

        self.assertEqual(result, "Release summary")
        get_groq_client.assert_called_once_with("groq-secret")
        client.chat.completions.create.assert_called_once_with(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": "prompt text"}],
            temperature=0.2,
            max_completion_tokens=2048,
        )

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
