from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".sh", ".py"}
RETIRED_EXECUTOR_MACHINERY = (
    "executors.json",
    "mcp__codex__codex",
    "async-dispatch",
    "gambit-wrapper",
    "codex-reply",
)
ROLES = (
    "scout",
    "worker",
    "escalation",
    "steelman",
    "finder",
    "verifier",
    "test-runner",
)


class RootTreeIsFreeOfExecutorMachineryTest(unittest.TestCase):
    def text_files(self) -> list[Path]:
        return sorted(
            path
            for root in (ROOT / "skills", ROOT / "contracts")
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
        )

    def test_root_tree_drops_every_executor_surface(self) -> None:
        for path in self.text_files():
            text = path.read_text(encoding="utf-8")
            for token in RETIRED_EXECUTOR_MACHINERY:
                with self.subTest(path=path.name, token=token):
                    self.assertNotIn(token, text)

    def test_retired_contract_files_are_absent(self) -> None:
        for relative in ("executors.md", "async-dispatch.md"):
            self.assertFalse((ROOT / "contracts" / relative).exists(), relative)
        self.assertFalse(
            (
                ROOT
                / "skills"
                / "executing-plans"
                / "references"
                / "configured-workers.md"
            ).exists()
        )


class ModelsContractDefinesRungsAndRolesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "contracts" / "models.md").read_text(encoding="utf-8")
        cls.prose = " ".join(cls.text.split())

    def test_config_path_uses_the_exact_claude_config_dir_fallback(self) -> None:
        self.assertIn(
            "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/gambit/models.json", self.text
        )
        self.assertNotIn("~/.claude/gambit/models.json", self.text)

    def test_pinned_schema_is_documented_verbatim(self) -> None:
        self.assertIn(
            '"<name>": {"agent": "<subagent_type>", '
            '"readonly_agent": "<subagent_type>"}',
            self.text,
        )
        self.assertIn(
            '"<name>": {"model": "<sonnet|opus|haiku|fable>"}', self.text
        )
        self.assertIn(
            '"<role>": {"entry": "<rung>", "ladder": ["<rung>", ...], '
            '"readonly": true|absent}',
            self.text,
        )
        self.assertIn('"rungs": {', self.text)
        self.assertIn('"roles": {', self.text)

    def test_dispatch_semantics_separate_agent_rungs_from_model_rungs(self) -> None:
        self.assertIn('subagent_type: "<agent>"', self.text)
        self.assertIn('subagent_type: "<readonly_agent>"', self.text)
        self.assertIn('subagent_type: "general-purpose"', self.text)
        self.assertIn('subagent_type: "Explore"', self.text)
        self.assertRegex(
            self.prose, r"agent rung[^.]*no `model:`|no `model:`[^.]*agent rung"
        )
        self.assertIn("readonly_agent", self.prose)

    def test_foreign_model_ids_are_forbidden_in_model_parameters(self) -> None:
        self.assertIn("silently substitute", self.prose.lower())
        self.assertRegex(
            self.prose,
            r"(?i)never (?:put |pass |use )?[^.]*foreign model id[^.]*`model:`",
        )
        self.assertIn("`sonnet`, `opus`, `haiku`, and `fable`", self.text)

    def test_built_in_defaults_use_only_harness_guaranteed_enum_rungs(self) -> None:
        expected = {
            "worker": ("opus", ["opus", "fable"]),
            "escalation": ("fable", ["fable"]),
            "scout": ("sonnet", ["sonnet"]),
            "steelman": ("fable", ["fable"]),
            "finder": ("fable", ["fable"]),
            "verifier": ("fable", ["fable"]),
            "test-runner": ("sonnet", ["sonnet"]),
        }
        defaults = self.text.split("## Built-in defaults", 1)[1].split("\n## ", 1)[0]
        for role, (entry, ladder) in expected.items():
            with self.subTest(role=role):
                row = re.search(
                    rf"(?m)^\| `{re.escape(role)}` \|(?P<rest>.*)$", defaults
                )
                self.assertIsNotNone(row, f"no built-in row for {role}")
                assert row is not None
                cells = [cell.strip() for cell in row.group("rest").split("|")]
                self.assertEqual(f"`{entry}`", cells[0])
                self.assertEqual(
                    " → ".join(f"`{rung}`" for rung in ladder), cells[1]
                )

        for readonly_role in ("scout", "steelman", "finder", "verifier"):
            row = re.search(
                rf"(?m)^\| `{re.escape(readonly_role)}` \|(?P<rest>.*)$", defaults
            )
            self.assertIsNotNone(row, f"no built-in row for {readonly_role}")
            assert row is not None
            cells = [cell.strip() for cell in row.group("rest").split("|")]
            self.assertEqual("yes", cells[2], readonly_role)

        self.assertNotRegex(defaults, r'"agent":')

        clause = re.search(
            r"An \*\*invalid\*\* file[^.]*\.", " ".join(defaults.split())
        )
        self.assertIsNotNone(clause, "no invalid-config clause in the defaults")
        assert clause is not None
        invalid = clause.group(0)
        self.assertIn("falls back to these same defaults", invalid)
        self.assertIn("in the transcript", invalid)
        self.assertIn("one-line warning", invalid)
        self.assertIn(
            "naming the file and the exact parse or validation error", invalid
        )

    def test_resolution_requires_a_fresh_config_read_before_the_table(self) -> None:
        self.assertIn(
            "Every resolution starts with a fresh Read of the config file",
            self.text,
        )
        self.assertIn("`rung source: config`", self.text)
        self.assertIn(
            "`rung source: built-in defaults (models.json absent)`", self.text
        )
        defaults = " ".join(self.text.split("## Built-in defaults", 1)[1].split())
        self.assertIn(
            "reached only through step 1 of the dispatch procedure", defaults
        )

    def test_a_concern_about_the_configured_rung_is_flagged_not_rerouted(
        self,
    ) -> None:
        invariants = " ".join(
            self.text.split("## Rung and ladder invariants", 1)[1].split()
        )
        self.assertIn("flagged, never routed around", invariants)
        self.assertIn("not an in-flight override", invariants)

    def test_rung_and_ladder_invariants_are_stated(self) -> None:
        invariants = self.text.split("## Rung and ladder invariants", 1)[1]
        prose = " ".join(invariants.split())
        for required in (
            "orchestrator selects the entry rung",
            "never below the role's entry",
            "never selects or changes its own rung",
            "Never re-dispatch the same rung on unchanged evidence",
            "moves UP the ladder",
            "Escalation is one step",
            "at most one informed repair on the `escalation` rung",
            "There is no third dispatch",
            "reachable only through that answer",
        ):
            with self.subTest(required=required):
                self.assertIn(required, prose)

    def test_every_role_keeps_its_name(self) -> None:
        for role in ROLES:
            with self.subTest(role=role):
                self.assertIn(f"`{role}`", self.text)


class SkillDispatchSitesResolveThroughModelsTest(unittest.TestCase):
    @staticmethod
    def skill(name: str) -> str:
        return " ".join(
            (ROOT / "skills" / name / "SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )

    def test_scout_sites_resolve_the_scout_role(self) -> None:
        for name in ("brainstorming", "executing-plans"):
            with self.subTest(skill=name):
                self.assertIn(
                    "Resolve the `scout` role through `contracts/models.md`",
                    self.skill(name),
                )

    def test_test_runner_site_resolves_the_test_runner_role(self) -> None:
        self.assertIn(
            "Resolve the `test-runner` role through `contracts/models.md`",
            self.skill("refactoring"),
        )

    def test_worker_and_escalation_sites_resolve_their_roles(self) -> None:
        executing = self.skill("executing-plans")
        self.assertIn(
            "Resolve the `worker` role through `contracts/models.md`", executing
        )
        self.assertIn(
            "Resolve the `escalation` role through `contracts/models.md`",
            executing,
        )
        self.assertNotIn(
            "Resolve the `finder` role through `contracts/models.md` for this one advisory dispatch",
            executing,
        )

    def test_review_resolves_finder_and_verifier_roles(self) -> None:
        review = self.skill("review")
        self.assertIn(
            "Resolve the `finder` role through `contracts/models.md`", review
        )
        self.assertIn(
            "Resolve the `verifier` role through `contracts/models.md`", review
        )

    def test_brainstorming_resolves_the_steelman_role(self) -> None:
        self.assertIn(
            "Resolve the `steelman` role through `contracts/models.md`",
            self.skill("brainstorming"),
        )

    def test_no_skill_keeps_the_retired_tier_vocabulary(self) -> None:
        for path in sorted((ROOT / "skills").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotRegex(
                    text,
                    r"(?:scout|worker|finder|verifier|test-runner|steelman|"
                    r"wrapper|escalation) tier",
                )

    def test_no_skill_points_at_a_name_models_md_no_longer_defines(self) -> None:
        for path in sorted((ROOT / "skills").rglob("*.md")):
            text = " ".join(path.read_text(encoding="utf-8").split())
            with self.subTest(path=path.name):
                self.assertNotRegex(
                    text,
                    r"(?:cheap|standard|most-capable) tier|tier alias"
                    r"|configured (?:worker|executor|Codex)",
                )


if __name__ == "__main__":
    unittest.main()
