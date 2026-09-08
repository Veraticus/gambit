from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def numbered_items_between(
    text: str,
    start: str,
    end: str,
) -> tuple[tuple[int, str], ...]:
    body = text.split(start, 1)[1].split(end, 1)[0]
    return tuple(
        (int(number), item)
        for number, item in re.findall(r"(?m)^(\d+)\. (\S.*)$", body)
    )


class BrainstormingSteelmanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "skills" / "brainstorming" / "SKILL.md").read_text(
            encoding="utf-8"
        )

    def test_discovery_precedes_epic_drafting_with_complete_packet(self) -> None:
        expected_fields = tuple(
            enumerate(
                (
                    "**User goal**",
                    "**Agreed constraints and scope**",
                    "**Chosen approach**",
                    "**Architecture and data flow**",
                    "**Rejected alternatives and reasons**",
                    "**Validation strategy**",
                    "**Delivery constraints**",
                    "**Unresolved decisions**",
                ),
                start=1,
            )
        )
        steelman_at = self.text.index("### 3a. Steelman the Agreed Design")
        epic_at = self.text.index("### 4. Create the Epic Task")
        self.assertLess(steelman_at, epic_at)
        steelman = self.text[steelman_at:epic_at]
        prose = " ".join(steelman.split())
        self.assertIn(
            "After the user and root agree on one coherent candidate design",
            prose,
        )
        self.assertIn("mandatory discovery pass", prose)
        self.assertIn("self-contained **Design Packet**", prose)
        actual_fields = numbered_items_between(
            steelman,
            "containing exactly these contracted fields:\n\n",
            "\n\nDo not omit an empty field",
        )
        self.assertEqual(expected_fields, actual_fields)

    def test_steelman_resolves_its_rung_and_stays_read_only(self) -> None:
        steelman = self.text.split("### 3a. Steelman the Agreed Design", 1)[1]
        steelman = steelman.split("### 4. Create the Epic Task", 1)[0]
        prose = " ".join(steelman.split())
        for required in (
            "Resolve the `steelman` role through `contracts/models.md` to its rung",
            "an agent rung dispatches the rung's `readonly_agent` with no `model:` at all",
            'model: "<steelman rung alias — contracts/models.md>"',
            "omit entirely on an agent rung",
            "contracts/steelman.md",
            "Mode: Discovery",
        ):
            self.assertIn(required, prose)

        for retired in (
            "executors.json",
            "contracts/executors.md",
            "codex-reply",
            "configured fully qualified MCP tool",
            "developer-instructions",
            "steelman tier",
        ):
            self.assertNotIn(retired, prose)

    def test_steelman_dispatch_is_fresh_and_carries_only_contract_and_mode(
        self,
    ) -> None:
        steelman = self.text.split("### 3a. Steelman the Agreed Design", 1)[1]
        steelman = steelman.split("### 4. Create the Epic Task", 1)[0]
        prose = " ".join(steelman.split())
        for required in (
            "Discovery receives the Design Packet and no previous Steelman output",
            "revised Design Packet, the frozen Design Ledger, and a concise design delta",
            "Never inherit prior turns into a Steelman dispatch",
            "never dispatch a Steelman without its contract path",
        ):
            self.assertIn(required, prose)

    def test_visible_frozen_ledger_yield_and_bounded_closure_dialogue(self) -> None:
        expected_choices = (
            (1, "revise without another Steelman pass;"),
            (2, "lock the contract with the residual risk recorded; or"),
            (3, "explicitly authorize another discovery cycle."),
        )
        steelman = self.text.split("### 3a. Steelman the Agreed Design", 1)[1]
        steelman = steelman.split("### 4.", 1)[0]
        prose = " ".join(steelman.split())
        for required in (
            "`READY`, `REVISE`, `NEEDS_DECISION`, or `BLOCKED`",
            "Strongest case for the chosen design",
            "Strongest credible alternative and when it wins",
            "Numbered findings",
            "Actual user decisions",
            "Evidence and coverage",
            "transcript-local frozen **Design Ledger**",
            "`ADOPTED`",
            "`REJECTED` with a reason",
            "`OPEN`",
            "`DEFERRED` with a scope boundary",
            "every discovery finding",
            "yield to the user",
            "cannot silently revise the packet and dispatch closure",
            "exactly one closure pass",
            "if an `ADOPTED` or `OPEN` finding materially changes the design",
            "Skip closure only when discovery returned `READY` and no material design change occurred",
            "`READY`, `STILL_OPEN`, `CHANGE_INDUCED_CONCERN`, or `BLOCKED`",
            "cannot restart discovery",
            "cannot reopen `REJECTED` or `DEFERRED` items",
            "No automatic third call",
            "fundamental architecture reset",
            "explicit user authorization",
        ):
            self.assertIn(required, prose)

        actual_choices = numbered_items_between(
            steelman,
            "stop and offer exactly these user\nchoices in prose:\n\n",
            "\n\nThe third choice is the only choice",
        )
        self.assertEqual(expected_choices, actual_choices)
        self.assertIn(
            "third choice is the only choice that resets the budget",
            prose,
        )

    def test_every_discovery_outcome_has_fail_closed_routing(self) -> None:
        routing = self.text.split(
            "Discovery receives the Design Packet and no previous Steelman output.",
            1,
        )[1].split("#### Freeze the ledger and yield", 1)[0]
        prose = " ".join(routing.split())
        for required in (
            "selected discovery dispatch or tool call fails",
            "output is malformed or missing any contracted section",
            "stop and report the failure",
            "Do not create a Design Ledger",
            "draft an epic contract",
            "fall back to another dispatch path",
            "automatically redispatch",
            "`BLOCKED`: stop and show the exact missing material",
            "`NEEDS_DECISION`: follow the ledger/yield path",
            "yield on every named user decision",
            "cannot advance while any named decision remains unresolved",
            "`REVISE`: follow the ledger/yield path but do not advance directly",
            "requires finding dispositions and a material Design Packet revision",
            "If no material revision is adopted, stop",
            "`READY`: follow the ledger/yield path",
            "may skip closure only when no material design change follows",
            "No non-`READY` discovery result can fall through to epic drafting",
            "No discovery branch automatically spends a second discovery call",
        ):
            self.assertIn(required, prose)

    def test_finalized_design_packet_is_the_immutable_contract_source(self) -> None:
        steelman = self.text.split("### 3a. Steelman the Agreed Design", 1)[1]
        steelman = steelman.split("### 4. Create the Epic Task", 1)[0]
        prose = " ".join(steelman.split())
        for required in (
            "Before epic drafting, the root must produce a finalized Design Packet",
            "every `ADOPTED` conclusion",
            "Requirements (IMMUTABLE)",
            "Anti-Patterns (FORBIDDEN)",
            "Approach",
            "Validation Strategy",
            "Delivery Constraints",
            "A `READY` status permits drafting but is not the contract source",
            "Draft the epic contract from that finalized Design Packet",
            "Do not copy the Design Ledger itself into the epic",
            "do not convert ledger IDs into task or plan state",
            "ledger remains transcript-local",
        ):
            self.assertIn(required, prose)


if __name__ == "__main__":
    unittest.main()
