"""Structural guards for behaviorally evaluated skill rules, not model evaluations."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillConvergenceTests(unittest.TestCase):
    def test_authoring_distinguishes_new_guidance_from_existing_regressions(self):
        text = (ROOT / "skills/writing-skills/SKILL.md").read_text()
        self.assertIn("**New skill:**", text)
        self.assertIn("**Existing skill:**", text)
        self.assertIn("also run the current skill on the same fixture", text)
        self.assertIn("NOT a stop condition", text)
        self.assertIn("restoring correct unaided behavior", text)
        self.assertIn("safeguard is genuinely necessary", text)
        self.assertIn("Do not retry until a failure appears", text)
        self.assertNotIn("**Behaves correctly → STOP. Do not write the skill.**", text)

if __name__ == "__main__":
    unittest.main()
