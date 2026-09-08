from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".sh", ".py"}


class WorkflowRoutingTest(unittest.TestCase):
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
