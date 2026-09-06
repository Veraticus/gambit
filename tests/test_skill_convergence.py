"""Structural guards for behaviorally evaluated skill rules, not model evaluations."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillConvergenceTests(unittest.TestCase):
    def test_authoring_distinguishes_new_guidance_from_existing_regressions(self):
        for root in (ROOT / "src", ROOT, ROOT / "plugins/gambit"):
            with self.subTest(root=root):
                text = (root / "skills/writing-skills/SKILL.md").read_text()
                self.assertIn("**New skill:**", text)
                self.assertIn("**Existing skill:**", text)
                self.assertIn("also run the current skill on the same fixture", text)
                self.assertIn("NOT a stop condition", text)
                self.assertIn("restoring correct unaided behavior", text)
                self.assertIn("safeguard is genuinely necessary", text)
                self.assertIn("Do not retry until a failure appears", text)
                self.assertNotIn("**Behaves correctly → STOP. Do not write the skill.**", text)

    def test_requirements_have_a_basis_not_a_post_hoc_task_justification(self):
        for root in (ROOT / "src", ROOT, ROOT / "plugins/gambit"):
            with self.subTest(root=root):
                text = (root / "skills/brainstorming/SKILL.md").read_text()
                self.assertIn("Admit requirements by origin", text)
                self.assertIn("Never add a requirement merely to justify a task", text)
                self.assertIn("each behavior a Requirement demands", text)
                self.assertNotIn("add the requirement to the epic explicitly", text)
                template = (root / "skills/brainstorming/TEMPLATES.md").read_text()
                self.assertIn("concrete requirement — basis", template)
                self.assertIn("First deliverable:", template)

    def test_review_admits_work_separately_from_verifying_truth(self):
        for root in (ROOT / "src", ROOT, ROOT / "plugins/gambit"):
            with self.subTest(root=root):
                text = (root / "skills/review/SKILL.md").read_text()
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
        for root in (ROOT / "src", ROOT, ROOT / "plugins/gambit"):
            for reviewer in ("quality", "conformance", "security", "performance"):
                with self.subTest(root=root, reviewer=reviewer):
                    text = (root / f"skills/review/reviewers/{reviewer}.md").read_text()
                    self.assertIn("Non-blocking by default", text)
                    self.assertIn("A GAP must identify", text)
                    self.assertIn("preconditions", text)
                    self.assertNotIn("WILL be implemented", text)

    def test_execution_convergence_counts_required_delivery_not_optional_work(self):
        for root in (ROOT / "src", ROOT, ROOT / "plugins/gambit"):
            with self.subTest(root=root):
                text = (root / "skills/executing-plans/SKILL.md").read_text()
                normalized = " ".join(text.split())
                self.assertIn("Choose a runnable delivery slice", text)
                self.assertIn("A named blocker is a failing declared gate", text)
                self.assertIn("optional improvements does not reset", normalized)
                self.assertIn("Explicit user-selected mechanisms", text)
                self.assertIn("Review confirmation alone does not authorize work", normalized)


if __name__ == "__main__":
    unittest.main()
