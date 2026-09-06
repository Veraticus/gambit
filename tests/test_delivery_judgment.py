"""Structural and fixture-controller coverage for bounded delivery judgment."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import render_skills

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "tests/fixtures/skill-convergence/delivery-controller.py"


class DeliveryJudgmentPolicyTest(unittest.TestCase):
    def test_steelman_contract_has_a_narrow_delivery_mode(self) -> None:
        text = (ROOT / "src/contracts/steelman.md").read_text()
        for required in (
            "Mode 3: Delivery judgment",
            "DESIGN-SATISFIED",
            "CONTINUE-ONCE",
            "USER-DECISION",
            "not a new defect finder",
            "one delivery judgment per task family intervention",
        ):
            self.assertIn(required, text)

    def test_delivery_mode_receives_recorded_family_state_without_mutation_authority(self) -> None:
        canonical = (ROOT / "src/contracts/steelman.md").read_text()
        self.assertIn("In Modes 1 and 2, Steelman results are transcript design context", canonical)
        self.assertNotIn(
            "Steelman results are transcript design context, never plan steps or repository state.",
            canonical.split("## Mode 3: Delivery judgment", 1)[0],
        )
        mode_three = canonical.split("## Mode 3: Delivery judgment", 1)[1]
        self.assertIn("current task-family `DELIVERY` record", mode_three)
        self.assertIn("unused, consumed, or unknown", mode_three)
        self.assertIn("judge cannot mutate", mode_three)

        with tempfile.TemporaryDirectory() as temporary:
            _, contracts = render_skills.render_backend("claude", Path(temporary))
            claude = (contracts / "steelman.md").read_text()
            _, contracts = render_skills.render_backend("codex", Path(temporary))
            codex = (contracts / "steelman.md").read_text()
        for rendered in (claude, codex):
            rendered_mode_three = rendered.split("## Mode 3: Delivery judgment", 1)[1]
            self.assertIn("current task-family `DELIVERY` record", rendered_mode_three)
            self.assertIn("unused, consumed, or unknown", rendered_mode_three)

    def test_delivery_evidence_includes_authoritative_allowance_state(self) -> None:
        reference = (ROOT / "src/skills/executing-plans/references/delivery-judgment.md").read_text()
        evidence = reference.split("Prepare primary evidence", 1)[1].split("Label the root's proposed", 1)[0]
        self.assertIn("current task-family `DELIVERY` record", evidence)
        self.assertIn("unused, consumed, or unknown", evidence)
        self.assertIn("must not guess", evidence)

    def test_both_rendered_judge_payloads_contain_the_complete_packet(self) -> None:
        required_fields = (
            "Verbatim Requirements and Success Criteria: <verbatim requirements and success criteria>",
            "Original executable brief: <original executable brief>",
            "Authoritative DELIVERY record and allowance: <authoritative DELIVERY record with allowance marked unused, consumed, or unknown>",
            "Worker returns: <worker returns>",
            "Diff stat and ownership versus wave base: <diff stat against wave base and owned files>",
            "Gate output: <focused-gate output>",
            "Admitted defects and consequences: <admitted defects with locations and consequences>",
            "Source references: <source references>",
            "Root proposal (separately labeled): <root's proposed route>",
        )
        with tempfile.TemporaryDirectory() as temporary:
            skills, _ = render_skills.render_backend("claude", Path(temporary))
            claude = (skills / "executing-plans/references/delivery-judgment.md").read_text()
            skills, _ = render_skills.render_backend("codex", Path(temporary))
            codex = (skills / "executing-plans/references/delivery-judgment.md").read_text()
        for backend, rendered, command in (
            ("claude", claude, "Agent subagent_type="),
            ("codex", codex, "SpawnAgent agent_type="),
        ):
            with self.subTest(backend=backend):
                block = rendered.split(command, 1)[1].split("```", 1)[0]
                payload = re.search(r'(?:prompt|message)="([\s\S]*?)"\n', block)
                self.assertIsNotNone(payload)
                for field in required_fields:
                    self.assertIn(field, payload.group(1))

    def test_codex_render_has_exact_undoubled_delivery_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skills, _ = render_skills.render_backend("codex", Path(temporary))
            rendered = (skills / "executing-plans/references/delivery-judgment.md").read_text()
        self.assertRegex(
            rendered,
            r'(?m)^SpawnAgent agent_type="steelman" task_name="steelman" fork_turns="none"  '
            r'# Profile-aware: requires hide_spawn_agent_metadata = false and a non-reserved tool_namespace\.\n'
            r'  message="Read <abs>/codex-contracts/steelman\.md first\.',
        )
        self.assertNotIn("SpawnSpawnAgent", rendered)
        self.assertNotIn("codex-codex-contracts", rendered)

    def test_bounded_policy_replaces_generated_legacy_retries_but_not_user_policy(self) -> None:
        skill = (ROOT / "src/skills/executing-plans/SKILL.md").read_text()
        legacy = skill.split("For a legacy epic", 1)[1].split("**Enter the epic worktree.**", 1)[0]
        self.assertIn("even when the epic already has Delivery Constraints", legacy)
        self.assertIn("agent-generated legacy retry boilerplate", legacy)
        self.assertIn("replaced by this bounded policy", legacy)
        self.assertIn("explicit conflicting user-selected continuation policy requires clarification", legacy)

    def test_codex_terminal_escalation_has_no_copyable_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skills, _ = render_skills.render_backend("codex", Path(temporary))
            codex = (skills / "executing-plans/SKILL.md").read_text()
        terminal = codex.split("4. **Terminal escalation — no automatic retry.**", 1)[1]
        terminal = terminal.split("Route the bounded continuation result", 1)[0]
        self.assertNotIn("SpawnAgent", terminal)
        self.assertNotIn("escalation-final", terminal)

    def test_both_backends_route_repairs_through_delivery_judgment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skills, _ = render_skills.render_backend("claude", Path(temporary))
            claude = (skills / "executing-plans/SKILL.md").read_text()
            claude_reference = (skills / "executing-plans/references/delivery-judgment.md").read_text()
            skills, _ = render_skills.render_backend("codex", Path(temporary))
            codex = (skills / "executing-plans/SKILL.md").read_text()
            codex_reference = (skills / "executing-plans/references/delivery-judgment.md").read_text()
        for skill, reference in ((claude, claude_reference), (codex, codex_reference)):
            self.assertIn("references/delivery-judgment.md", skill)
            self.assertIn("Before any corrective dispatch, quality repair, escalation, or terminal-rung repeat", skill)
            self.assertIn("unknown existing-family allowance pauses", skill)
            self.assertIn("`DELIVERY` section", reference)
            self.assertIn("Goal", reference)
            self.assertIn("Record and consume the allowance **before** dispatching", reference)
            self.assertIn("endpoint failed", reference)
        self.assertIn('Agent subagent_type="general-purpose" model="<steelman rung alias', claude_reference)
        self.assertIn(
            'SpawnAgent agent_type="steelman" task_name="steelman" fork_turns="none"',
            codex_reference,
        )
        self.assertIn("same-session plan/checkpoint only", codex_reference)
        self.assertNotIn("until the defect clears", claude)
        self.assertNotIn("until the defect clears", codex)
        self.assertNotIn("repeated maximum-reasoning", codex)

    def test_controller_judgments_are_scripted_and_do_not_consume(self) -> None:
        expected = {
            "expanded": "USER-DECISION",
            "first-expanded": "USER-DECISION",
            "spent": "USER-DECISION",
            "unknown": "USER-DECISION",
            "small": "CONTINUE-ONCE",
            "ideal": "DESIGN-SATISFIED",
            "slow": "DESIGN-SATISFIED",
        }
        for scenario, verdict in expected.items():
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                state = Path(temporary) / "state.json"
                self.run_controller(state, "init", scenario)
                shown = json.loads(self.run_controller(state, "show").stdout)
                self.assertEqual(scenario, shown["scenario"])
                self.assertTrue(shown["evidence"])
                self.assertEqual(verdict, shown["scripted_judge_verdict"])
                result = self.run_controller(state, "judge", "CALLER-CHOICE")
                data = json.loads(state.read_text())
                self.assertEqual(verdict, result.stdout.strip())
                self.assertEqual({"decision": None, "consumed": scenario == "spent"}, data["delivery"])

    def test_controller_real_check_tracks_program_not_dispatch_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "state.json"
            self.run_controller(state, "init", "small")
            self.assertNotEqual(0, self.run_controller(state, "run-check", expected=None).returncode)
            self.run_controller(state, "dispatch-worker")
            self.assertEqual(0, self.run_controller(state, "run-check").returncode)
            target = Path(temporary) / "delivery_target.py"
            target.write_text("def transform(value):\n    return value - 1\n")
            self.assertNotEqual(0, self.run_controller(state, "run-check", expected=None).returncode)
            self.assertFalse(json.loads(state.read_text())["check_passed"])
            target.write_text("def transform(value):\n    return 2\n")
            self.assertNotEqual(0, self.run_controller(state, "run-check", expected=None).returncode)
            self.assertFalse(json.loads(state.read_text())["check_passed"])

    def test_controller_records_actions_without_policy_guards(self) -> None:
        for scenario in ("spent", "expanded"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                state = Path(temporary) / "state.json"
                self.run_controller(state, "init", scenario)
                self.run_controller(state, "dispatch-worker")
                data = json.loads(state.read_text())
                self.assertEqual("dispatch-worker", data["events"][-1]["action"])

                record = {"decision": "USER-DECISION", "consumed": True}
                self.run_controller(state, "record", json.dumps(record))
                self.run_controller(state, "pause", "await-user")
                self.run_controller(state, "complete", "requested-anyway")
                data = json.loads(state.read_text())
                self.assertEqual(record, data["delivery"])
                self.assertEqual("paused", data["events"][-2]["status"])
                self.assertEqual("requested-anyway", data["status"])
                self.assertEqual("complete", data["events"][-1]["action"])

    def run_controller(self, state: Path, *command: str, expected: int | None = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            ["python3", str(CONTROLLER), "--state", str(state), *command],
            check=False,
            text=True,
            capture_output=True,
        )
        if expected is not None:
            self.assertEqual(expected, completed.returncode, completed.stderr)
        return completed


if __name__ == "__main__":
    unittest.main()
