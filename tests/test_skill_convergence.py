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

    def test_review_admits_work_separately_from_verifying_truth(self):
        text = (ROOT / "skills/review/SKILL.md").read_text()
        normalized = " ".join(text.split())
        self.assertIn("Only confirmed, admitted findings", text)
        self.assertIn("admission_basis:", text)
        self.assertIn("zero admitted ledger entries", text)
        self.assertIn("improvements do not block approval", normalized)
        self.assertIn("without pretending they were refuted", normalized)
        self.assertIn("required safety or compatibility", text)
        self.assertNotIn("implement every confirmed improvement", text)
        self.assertNotIn("Confirmed findings become the complete", text)

    def test_all_finders_keep_optional_improvements_nonblocking(self):
        for reviewer in ("quality", "conformance", "security", "performance"):
            with self.subTest(reviewer=reviewer):
                text = (
                    ROOT / f"skills/review/reviewers/{reviewer}.md"
                ).read_text()
                self.assertIn("Non-blocking by default", text)
                self.assertIn("A GAP must identify", text)
                self.assertIn("preconditions", text)
                self.assertNotIn("WILL be implemented", text)

if __name__ == "__main__":
    unittest.main()
