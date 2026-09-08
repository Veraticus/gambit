from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools import render_skills


def bounded_section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


class ExecutingPlansRungRoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="gambit-rungs-exec-")
        temporary_root = Path(cls.temporary.name)
        claude_skills, _ = render_skills.render_backend("claude", temporary_root)
        codex_skills, _ = render_skills.render_backend("codex", temporary_root)
        cls.claude = (claude_skills / "executing-plans" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        cls.codex = (codex_skills / "executing-plans" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        cls.worker_dispatch = bounded_section(
            cls.claude,
            "**Dispatch the wave to workers:**",
            "3. **Route on the worker's returned status**",
        )
        cls.claude_status_routing = bounded_section(
            cls.claude,
            "3. **Route on the worker's returned status**",
            "**One of the four statuses is the ONLY signal",
        )
        cls.codex_status_routing = bounded_section(
            cls.codex,
            "3. **Route on the worker's returned status**",
            "**One of the four statuses is the ONLY signal",
        )
        cls.claude_gate = bounded_section(
            cls.claude,
            "#### Checkpoint gate",
            "#### When Hitting Obstacles",
        )
        cls.codex_gate = bounded_section(
            cls.codex,
            "#### Checkpoint gate",
            "#### When Hitting Obstacles",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

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

    def test_claude_render_has_no_configured_executor_route(self) -> None:
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
                self.assertNotIn(retired, self.claude)

    def test_repairs_are_limited_to_one_informed_repair_then_the_user(self) -> None:
        self.assertContainsAll(
            self.claude_status_routing,
            (
                "one implementation, then at most one informed repair on the `escalation` rung, then the user",
                "read the task's `repairs_used`; if it is already `1`, or the task is `awaiting_user`, there is no dispatch to make",
                "Resolve the `escalation` role through `contracts/models.md`",
                "Record `repairs_used: 1` on the task with `TaskUpdate` BEFORE dispatching",
                "There is no second repair, no climb beyond this rung, and no renamed or split descendant that starts fresh",
                'Agent subagent_type="general-purpose" model="<escalation rung alias — contracts/models.md>"',
                'set `subagent_type="<escalation rung agent>"` instead',
                "routes as the one informed repair, never to a reviewer",
                "A second NEEDS_CONTEXT on the same task",
            ),
        )
        self.assertContainsAll(
            self.codex_status_routing,
            (
                "one implementation, then at most one informed repair, then the user",
                "Record `repairs_used: 1` in the checkpoint first",
                'SpawnAgent agent_type="escalation"',
                "3. **No second repair.**",
                "Do not dispatch another worker, a higher rung, a judge, or a renamed descendant",
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
                self.assertNotIn(retired, self.claude)
                self.assertNotIn(retired, self.codex)

    def test_checkpoint_gate_is_binary_against_the_baseline_with_no_reviewer(self) -> None:
        for gate in (self.claude_gate, self.codex_gate):
            self.assertContainsAll(
                gate,
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
                    self.assertNotIn(retired, gate)
        self.assertNotIn(
            "Resolve the `finder` role through `contracts/models.md` for this one advisory dispatch",
            self.claude,
        )

    def test_claude_summaries_describe_rung_resolved_workers(self) -> None:
        self.assertContainsAll(
            self.claude,
            (
                "a fresh worker on the resolved `worker` rung does the mechanical work",
                "Each worker runs on the rung the `worker` role resolves to in"
                " `contracts/models.md`, and a NOT DONE gets exactly one informed"
                " repair on the `escalation` rung before the user decides.",
            ),
        )

    def test_native_codex_output_is_isolated_from_claude_rung_routing(self) -> None:
        self.assertContainsAll(
            self.codex,
            (
                'SpawnAgent agent_type="worker"',
                'SpawnAgent agent_type="escalation"',
                "Resolve the worker role",
                "codex-contracts/worker.md",
            ),
        )
        for claude_only in (
            "rung alias",
            "readonly_agent",
            "Resolve the `worker` role",
            "Resolve the `escalation` role",
        ):
            with self.subTest(claude_only=claude_only):
                self.assertNotIn(claude_only, self.codex)

    def test_generated_outputs_are_current(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        self.assertEqual(
            self.claude,
            (repository / "skills" / "executing-plans" / "SKILL.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(
            self.codex,
            (
                repository
                / "plugins"
                / "gambit"
                / "skills"
                / "executing-plans"
                / "SKILL.md"
            ).read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
