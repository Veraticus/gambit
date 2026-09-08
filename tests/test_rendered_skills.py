from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CONTRACTS = ROOT / "contracts"
CONCRETE_PROVIDER_MODEL_IDS = re.compile(
    r"(?i)\b(?:claude-[a-z0-9.-]*\d[a-z0-9.-]*|"
    r"gpt-[a-z0-9.-]*\d[a-z0-9.-]*|o[1-9](?:-[a-z0-9.-]+)?|codex-mini)\b"
)


class RootSkillsTest(unittest.TestCase):
    def test_contract_catalog_registers_models_and_steelman(self) -> None:
        catalog = (CONTRACTS / "README.md").read_text(encoding="utf-8")
        self.assertIn("[models.md](models.md)", catalog)
        self.assertRegex(
            catalog,
            r"(?m)^\| \*\*steelman\*\* \| \[steelman\.md\]"
            r"\(steelman\.md\) \|",
        )
        self.assertNotIn("executors.md", catalog)
        self.assertTrue((CONTRACTS / "steelman.md").exists())
        self.assertFalse((CONTRACTS / "executors.md").exists())

    def test_models_contract_owns_rungs_and_roles(self) -> None:
        text = (CONTRACTS / "models.md").read_text(encoding="utf-8")
        self.assertRegex(
            text,
            r"(?m)^\| `steelman` \(design collaborator\) \|",
        )
        self.assertIn(
            "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/gambit/models.json", text
        )
        self.assertNotIn("wrapper", text)
        self.assertNotIn("most-capable", text)

    def test_validation_catalog_describes_wired_rung_routing(self) -> None:
        validation = (CONTRACTS / "VALIDATION.md").read_text(encoding="utf-8")
        normalized = " ".join(validation.split())

        self.assertNotIn(
            "Dispatch behavior is deliberately not claimed here",
            normalized,
        )
        for coverage, module in (
            (
                "`tests/test_rung_dispatch.py` pins the `models.json` config path",
                "test_rung_dispatch.py",
            ),
            (
                "`tests/test_brainstorming_steelman.py` covers Steelman rung resolution and call wiring",
                "test_brainstorming_steelman.py",
            ),
            (
                "`tests/test_executing_plans_rungs.py` covers worker and escalation routing and the binary checkpoint gate",
                "test_executing_plans_rungs.py",
            ),
            (
                "`tests/test_review_rungs.py` covers finder and verifier routing",
                "test_review_rungs.py",
            ),
            (
                "`tests/test_workflow_routing.py` covers scout and test-runner routing",
                "test_workflow_routing.py",
            ),
        ):
            with self.subTest(module=module):
                self.assertIn(coverage, normalized)
                self.assertTrue((ROOT / "tests" / module).exists())

    def test_steelman_contract_bounds_discovery_and_closure(self) -> None:
        text = " ".join(
            (CONTRACTS / "steelman.md").read_text(encoding="utf-8").split()
        )
        for field in (
            "User goal",
            "Agreed constraints and scope",
            "Chosen approach",
            "Architecture and data flow",
            "Rejected alternatives and reasons",
            "Validation strategy",
            "Delivery constraints",
            "Unresolved decisions",
        ):
            self.assertIn(field, text)

        self.assertIn(
            "Discovery status: exactly one of `READY`, `REVISE`, `NEEDS_DECISION`, or `BLOCKED`",
            text,
        )
        self.assertIn(
            "Closure status: exactly one of `READY`, `STILL_OPEN`, `CHANGE_INDUCED_CONCERN`, or `BLOCKED`",
            text,
        )
        for requirement in (
            "Strengthen the chosen design before challenging it",
            "Strongest credible alternative and when it wins",
            "Number assumptions, failure modes, ambiguities, and validation gaps",
            "concrete contract changes",
            "Actual user decisions",
            "transcript-local frozen Design Ledger",
            "`ADOPTED`, `REJECTED` with its reason, `OPEN`, or `DEFERRED` with its scope boundary",
            "Steelman cannot mutate the Design Ledger",
            "one disposition for every `ADOPTED` and `OPEN` ledger item",
            "cannot restart discovery",
            "cannot resurrect `REJECTED` or `DEFERRED` items",
            "one discovery call and one closure call",
            "No automatic third pass",
            "explicit user authorization",
            "transcript design context, never plan steps or repository state",
        ):
            self.assertIn(requirement, text)

        self.assertNotIn("Concrete contract changes", text)
        for forbidden_authority in (
            "edit files",
            "mutate task or plan state",
            "create contracts or briefs",
            "invoke workflows",
            "spawn children",
            "choose another pass",
        ):
            self.assertIn(forbidden_authority, text)

    def test_contracts_and_skills_do_not_name_concrete_provider_model_ids(self) -> None:
        for root in (CONTRACTS, SKILLS):
            for path in sorted(root.rglob("*.md")):
                self.assertIsNone(
                    CONCRETE_PROVIDER_MODEL_IDS.search(
                        path.read_text(encoding="utf-8")
                    ),
                    f"concrete provider model ID leaked into {path}",
                )

    def test_epic_contract_declares_convergence_and_validation_policy(self) -> None:
        brainstorming = (
            SKILLS / "brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        templates = (
            SKILLS / "brainstorming" / "TEMPLATES.md"
        ).read_text(encoding="utf-8")

        for required in ("Delivery Constraints", "Validation Strategy"):
            self.assertIn(required, brainstorming)
            self.assertIn(f"## {required}", templates)

        for required in (
            "two consecutive checkpoints",
            "one implementation, then at most one informed repair on the `escalation`",
            "`awaiting_user`",
            "explicit user approval",
            "Focused worker command",
            "Wave/component gate",
            "Release acceptance",
            "Acceptance budget",
        ):
            self.assertIn(required, templates)

    def test_execution_stops_negative_convergence_and_gates_acceptance(self) -> None:
        executing = (
            SKILLS / "executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        convergence = executing.split("#### Convergence Gate", 1)[1]
        convergence = convergence.split("### 4. Commit and STOP Checkpoint", 1)[0]
        for required in (
            "two consecutive checkpoints",
            "retire no success criterion or named blocker",
            "remaining work grows",
            "STOP autonomous continuation",
            "at most one informed repair on the `escalation`",
            "No judge, no second repair, no higher rung",
            "explicit user approval",
        ):
            self.assertIn(required, convergence)

        final_validation = executing.split("### 5. Epic Review", 1)[1]
        architecture = final_validation.index("architecture/scope preflight")
        acceptance = final_validation.index("release acceptance")
        self.assertLess(architecture, acceptance)
        self.assertIn("declared acceptance budget", final_validation)


if __name__ == "__main__":
    unittest.main()
