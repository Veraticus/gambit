"""Structural guards for behaviorally evaluated skill rules, not model evaluations."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DELETED_NON_OWNER_SKILLS = (
    "task-refinement",
    "refactoring",
    "testing-quality",
    "using-gambit",
    "writing-skills",
)


class SkillConvergenceTests(unittest.TestCase):
    def test_deleted_non_owner_skills_are_absent(self) -> None:
        for name in DELETED_NON_OWNER_SKILLS:
            with self.subTest(skill=name):
                self.assertFalse((ROOT / "skills" / name).exists())


if __name__ == "__main__":
    unittest.main()
