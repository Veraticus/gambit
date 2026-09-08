from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".sh", ".py"}


class WorkflowRoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.router_text = (
            ROOT / "skills" / "using-gambit" / "SKILL.md"
        ).read_text(encoding="utf-8")

    def test_router_has_no_automatic_session_start_activation(self) -> None:
        forbidden = (
            r"(?i)session[- ]start",
            r"(?i)start of (?:every|a|the) session",
            r"(?i)before (?:any|every) (?:response|action)",
            r"(?i)before (?:any|every) response or action",
            r"(?i)\b1\s*%",
        )
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, self.router_text), pattern)

    def test_router_is_explicit_concrete_and_under_200_body_words(self) -> None:
        frontmatter, body = self.router_text.split("\n---\n", 1)
        description = re.search(
            r"(?m)^description:\s*(.+)$", frontmatter
        ).group(1)
        self.assertRegex(description, r"(?i)\bexplicit")
        self.assertRegex(description, r"(?i)\bconcrete")
        self.assertIn("Choose exactly one owner", body)
        self.assertIn("first match wins", body)
        self.assertLess(len(re.findall(r"\b[\w-]+\b", body)), 200)

    def test_scout_sites_resolve_the_scout_rung(self) -> None:
        for skill in ("brainstorming", "executing-plans"):
            text = (
                ROOT / "skills" / skill / "SKILL.md"
            ).read_text(encoding="utf-8")
            prose = " ".join(text.split())
            with self.subTest(skill=skill):
                self.assertIn(
                    "Resolve the `scout` role through `contracts/models.md`",
                    prose,
                )
                self.assertIn(
                    "an agent rung uses the rung's `readonly_agent`",
                    prose,
                )
                self.assertIn("no `model:` at all", prose)
                self.assertNotIn("executors.json", prose)
                self.assertNotIn("scout tier", prose)

    def test_test_runner_site_resolves_the_test_runner_rung(self) -> None:
        text = (
            ROOT / "skills" / "refactoring" / "SKILL.md"
        ).read_text(encoding="utf-8")
        prose = " ".join(text.split())
        self.assertIn(
            "Resolve the `test-runner` role through `contracts/models.md`",
            prose,
        )
        self.assertIn("an agent rung uses the rung's `agent`", prose)
        self.assertIn("no `model:` at all", prose)
        self.assertNotIn("executors.json", prose)
        self.assertNotIn("test-runner tier", prose)

    def test_retired_parallel_workflow_is_absent_from_active_surfaces(self) -> None:
        retired_identifiers = ("parallel-agents", "parallel_agents")
        skill_root = ROOT / "skills"
        for identifier in retired_identifiers:
            with self.subTest(directory=identifier):
                self.assertFalse(skill_root.joinpath(identifier).exists())
        for artifact in sorted(skill_root.rglob("*")):
            if not artifact.is_file() or artifact.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = artifact.read_text(encoding="utf-8").casefold()
            for identifier in retired_identifiers:
                with self.subTest(artifact=artifact, identifier=identifier):
                    self.assertNotIn(identifier, text)

        catalog = (ROOT / "contracts" / "README.md").read_text(
            encoding="utf-8"
        ).casefold()
        for identifier in retired_identifiers:
            with self.subTest(catalog=identifier):
                self.assertNotIn(identifier, catalog)


if __name__ == "__main__":
    unittest.main()
