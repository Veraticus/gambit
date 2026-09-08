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
    def test_contract_catalog_names_roles_and_contract_paths(self) -> None:
        catalog = (CONTRACTS / "README.md").read_text(encoding="utf-8")
        for role in (
            "worker",
            "escalation",
            "scout",
            "steelman",
            "finder",
            "verifier",
            "test-runner",
        ):
            self.assertIn(f"`{role}`", catalog)
        for contract_path in (
            "contracts/worker.md",
            "contracts/scout.md",
            "contracts/steelman.md",
            "skills/review/reviewers/",
        ):
            self.assertIn(contract_path, catalog)

    def test_validation_catalog_describes_wired_rung_routing(self) -> None:
        validation = (
            ROOT / "tests" / "fixtures" / "skill-convergence" / "VALIDATION.md"
        ).read_text(encoding="utf-8")
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

    def test_contracts_and_skills_do_not_name_concrete_provider_model_ids(self) -> None:
        for root in (CONTRACTS, SKILLS):
            for path in sorted(root.rglob("*.md")):
                self.assertIsNone(
                    CONCRETE_PROVIDER_MODEL_IDS.search(
                        path.read_text(encoding="utf-8")
                    ),
                    f"concrete provider model ID leaked into {path}",
                )

if __name__ == "__main__":
    unittest.main()
