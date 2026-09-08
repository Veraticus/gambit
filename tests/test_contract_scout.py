import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOUT_CONTRACT = ROOT / "contracts" / "scout.md"
EXPECTED_SECTIONS = [
    "Read-only",
    "Answer the question asked",
    "Evidence, not verdicts",
    "The bug path",
    "Report",
]
FORBIDDEN_TOKENS = [
    "subagent_type",
    "Explore",
    "EnterWorktree",
    "Skill tool",
    "Common excuses",
    "STOP and",
    "return control",
    "ask the user",
    "legacy",
    "previously",
    "gambit:debugging",
]


class ScoutContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCOUT_CONTRACT.read_text()

    def test_has_required_sections_in_order(self):
        sections = re.findall(r"^## (.+)$", self.text, flags=re.MULTILINE)
        self.assertEqual(sections, EXPECTED_SECTIONS)

    def test_stays_within_word_limit(self):
        words = re.findall(r"\b[\w'-]+\b", self.text)
        self.assertLessEqual(len(words), 700)

    def test_names_absence_and_writable_reproduction_handoff(self):
        self.assertIn("NOT FOUND", self.text)
        self.assertIn("test-runner", self.text)

    def test_omits_harness_specific_and_historical_vocabulary(self):
        folded = self.text.casefold()
        for token in FORBIDDEN_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(token.casefold(), folded)


if __name__ == "__main__":
    unittest.main()
