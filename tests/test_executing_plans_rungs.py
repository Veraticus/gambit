from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def bounded_section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


class ExecutingPlansRungRoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "skills" / "executing-plans" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        cls.worker_dispatch = bounded_section(
            cls.text,
            "**Dispatch the wave to workers:**",
            "3. **Route on the worker's returned status**",
        )
        cls.status_routing = bounded_section(
            cls.text,
            "3. **Route on the worker's returned status**",
            "**One of the four statuses is the ONLY signal",
        )
        cls.gate = bounded_section(
            cls.text,
            "#### Checkpoint gate",
            "#### When Hitting Obstacles",
        )

    def assertContainsAll(self, text: str, expected: tuple[str, ...]) -> None:
        for item in expected:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_worker_rung_is_resolved_by_the_orchestrator_before_dispatch(self) -> None:
        self.assertContainsAll(
            self.worker_dispatch,
            (
                "Resolve the `worker` role through `contracts/models.md` before the initial dispatch",
                "never a rung below the entry, and never a rung the worker picks for itself",
                "always set `model:` explicitly to the rung's alias",
                "never omit it, never pass `inherit`",
                'Agent subagent_type="general-purpose" model="<worker rung alias — contracts/models.md>"',
                'Agent subagent_type="<worker rung agent>"',
            ),
        )

    def test_agent_rung_dispatch_never_carries_a_model_parameter(self) -> None:
        self.assertIn(
            "pass **no `model:` at all** — a foreign model id in `model:` is silently"
            " substituted rather than rejected",
            self.worker_dispatch,
        )
        self.assertIn("the `model=` field removed entirely", self.worker_dispatch)

    def test_skill_has_no_configured_executor_route(self) -> None:
        for retired in (
            "executors.json",
            "contracts/executors.md",
            "async-dispatch",
            "gambit-wrapper",
            "codex-reply",
            "worker.tool",
            "worker.reply_tool",
            "escalation-final",
            "TaskOutput",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.text)

    def test_repairs_are_limited_to_one_informed_repair_then_the_user(self) -> None:
        self.assertContainsAll(
            self.status_routing,
            (
                "one implementation, then at most one informed repair on the `escalation` rung, then the user",
                "read the task's `repairs_used`; if it is already `1`, or the task is `awaiting_user`, there is no dispatch to make",
                "Resolve the `escalation` role through `contracts/models.md`",
                "Record `repairs_used: 1` on the task's metadata with `TaskUpdate` BEFORE dispatching",
                "There is no second repair, no climb beyond this rung, and no renamed or split descendant that starts fresh",
                'Agent subagent_type="general-purpose" model="<escalation rung alias — contracts/models.md>"',
                'set `subagent_type="<escalation rung agent>"` instead',
                "routes as the one informed repair, never to a reviewer",
                "A second NEEDS_CONTEXT on the same task",
            ),
        )
        for retired in (
            "delivery-judgment",
            "CONTINUE-ONCE",
            "USER-DECISION",
            "allowance",
            "followup_task",
            "Terminal escalation",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.text)

    def test_checkpoint_gate_is_binary_against_the_baseline_with_no_reviewer(self) -> None:
        self.assertContainsAll(
            self.gate,
            (
                "there is no per-task reviewer dispatch",
                "against the epic's baseline and nothing else",
                "The verdict is binary and itemized",
                "Verdict:       DONE | NOT DONE",
                "Each NOT DONE names its baseline clause, the changed-code cause, and the evidence",
                "is an observation: write it under the checkpoint's Notes and move on",
                "There is no per-task reviewer.",
                "Do NOT dispatch a finder, verifier, or judge from this gate",
                "**Never edit the diff yourself — you judge and route; workers implement.**",
            ),
        )
        for retired in (
            "Quality review:",
            "reviewers/quality.md",
            "Escalate to an independent quality reviewer",
            "escalation trigger",
            "six sources",
            "maximal standard",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.gate)
        self.assertNotIn(
            "Resolve the `finder` role through `contracts/models.md` for this one advisory dispatch",
            self.text,
        )

    def test_summaries_describe_rung_resolved_workers(self) -> None:
        self.assertContainsAll(
            self.text,
            (
                "a fresh worker on the resolved `worker` rung does the mechanical work",
                "Each worker runs on the rung the `worker` role resolves to in"
                " `contracts/models.md`, and a NOT DONE gets exactly one informed"
                " repair on the `escalation` rung before the user decides.",
            ),
        )


if __name__ == "__main__":
    unittest.main()
