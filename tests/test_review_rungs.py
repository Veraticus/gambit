from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReviewExecutorRoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "skills" / "review" / "SKILL.md").read_text(
            encoding="utf-8"
        )

    @staticmethod
    def section(text: str, start: str, end: str) -> str:
        return text.split(start, 1)[1].split(end, 1)[0]

    def test_resolves_the_finder_rung_exactly_once_before_dispatch(self) -> None:
        step = self.section(
            self.text,
            "### Step 4: Dispatch Four Reviewers",
            "### Step 5: Scope-Filter and Dedupe Candidate Findings",
        )
        resolution = (
            "Resolve the `finder` role through `contracts/models.md` exactly once"
        )
        self.assertEqual(1, step.count(resolution))
        self.assertLess(step.index(resolution), step.index("#### Finder dispatch"))
        self.assertIn("All four dimensions run on that one resolved rung", step)
        self.assertIn("never resolve per dimension and never mix rungs", step)
        self.assertIn("an agent rung uses the rung's `readonly_agent`", step)

    def test_finder_dispatch_is_four_parallel_calls_on_the_resolved_rung(self) -> None:
        step = self.section(
            self.text,
            "#### Finder dispatch",
            "### Step 5: Scope-Filter and Dedupe Candidate Findings",
        )
        self.assertIn("In ONE message, emit exactly four finder calls", step)
        self.assertEqual(4, step.count('Agent subagent_type="general-purpose"'))
        self.assertEqual(
            4, step.count('model="<finder rung alias — contracts/models.md>"')
        )
        self.assertIn("with no `model:` at all", step)
        self.assertNotIn("finder tier", step)
        self.assertEqual(
            4,
            step.count(
                "your FIRST action must be to Read it, then follow it exactly."
            ),
        )
        for dimension in ("conformance", "security", "quality", "performance"):
            self.assertEqual(1, step.count(f"reviewers/{dimension}.md"))

    def test_frozen_brief_requires_actual_hunks_before_any_finder_dispatch(self) -> None:
        step = self.section(
            self.text,
            "### Step 3: Freeze Boundary and Prepare Brief",
            "### Step 5: Scope-Filter and Dedupe Candidate Findings",
        )
        for required in (
            "actual frozen diff hunks",
            "empty or missing hunk set is a composition failure",
            "before any finder dispatch",
            "never dispatch a finder with nothing to review",
        ):
            self.assertIn(required, step)

    def test_verifier_rung_resolves_once_and_independently_of_the_finder(self) -> None:
        step = self.section(
            self.text,
            "### Step 6: Dispatch Verifier Sub-Agent",
            "### Step 7: Assemble Findings From Verifier Output",
        )
        prose = " ".join(step.split())
        resolution = (
            "Resolve the `verifier` role through `contracts/models.md` exactly once"
        )
        self.assertEqual(1, prose.count(resolution))
        self.assertIn(
            "The verifier rung is resolved independently of the finder rung", prose
        )
        self.assertIn("retain that rung for closure", prose)
        self.assertIn("never a rung below the role's entry", prose)
        self.assertIn("an agent rung uses the rung's `readonly_agent`", prose)
        self.assertIn('model="<verifier rung alias — contracts/models.md>"', step)
        self.assertNotIn("verifier tier", step)
        self.assertIn(
            "your FIRST action must be to Read it, then follow it exactly.",
            step,
        )

    def test_closure_never_reruns_finders_and_preserves_the_ledger(self) -> None:
        closure = self.text.split("### Step 8: Remediate and Close the Ledger", 1)[1]
        prose = " ".join(closure.split())
        self.assertIn("Do not dispatch the four finders again", closure)
        self.assertIn("only open ledger entries", closure)
        self.assertIn("reuse the verifier rung resolved in Step 6", prose)
        self.assertIn("do not re-resolve the role or change rungs mid-ledger", prose)
        self.assertIn("The ledger is immutable", self.text)
        self.assertNotIn("#### Finder dispatch", closure)

    def test_summary_rules_follow_the_once_resolved_finder_rung(self) -> None:
        rules = self.text.split("**Parallelism is structural", 1)[1].split(
            "\n##", 1
        )[0]
        self.assertIn("four calls on the once-resolved finder rung", rules)
        self.assertNotIn("four Agent calls", rules)

        integration = self.text.split("## Integration", 1)[1]
        self.assertIn(
            "on the once-resolved `finder` rung (`contracts/models.md`)",
            integration,
        )
        self.assertIn(
            "Dispatches one verifier on the once-resolved `verifier` rung",
            integration,
        )


if __name__ == "__main__":
    unittest.main()
