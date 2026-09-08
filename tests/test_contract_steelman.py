from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SteelmanContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "contracts" / "steelman.md").read_text(encoding="utf-8")

    def test_required_sections_are_present_in_order(self) -> None:
        headings = re.findall(r"(?m)^## (.+)$", self.text)
        self.assertEqual(
            [
                "Authority",
                "The Design Packet",
                "Discovery",
                "The Design Ledger",
                "Closure",
                "Budget and decisions",
            ],
            headings,
        )

    def test_required_statuses_are_present(self) -> None:
        for status in (
            "READY",
            "REVISE",
            "NEEDS_DECISION",
            "BLOCKED",
            "STILL_OPEN",
            "CHANGE_INDUCED_CONCERN",
        ):
            with self.subTest(status=status):
                self.assertIn(status, self.text)

    def test_design_packet_fields_are_present(self) -> None:
        for field in (
            "Intent",
            "Premises",
            "Requirements",
            "Must Not Ship",
            "Approach and Rejected Approaches",
            "Done",
            "Release",
            "Unresolved decisions",
        ):
            with self.subTest(field=field):
                self.assertRegex(self.text, rf"(?m)^\d+\. \*\*{re.escape(field)}\*\*")

    def test_contract_is_within_word_budget(self) -> None:
        self.assertLessEqual(len(self.text.split()), 900)

    def test_forbidden_content_is_absent_case_insensitively(self) -> None:
        for token in (
            "Validation strategy",
            "Delivery constraints",
            "Success Criteri",
            "Anti-Pattern",
            "reset boundary",
            "explicit user authorization",
            "return control to the user",
            "third pass",
            "subagent_type",
            "legacy",
            "previously",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token.casefold(), self.text.casefold())


if __name__ == "__main__":
    unittest.main()
