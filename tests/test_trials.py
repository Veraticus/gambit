from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "tests" / "trials" / "run.py"
SPEC = importlib.util.spec_from_file_location("gambit_trial_runner", RUN_PATH)
assert SPEC is not None and SPEC.loader is not None
trials = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trials)


class FakeTransport:
    def __init__(self, *outcomes: object) -> None:
        self.outcomes = list(outcomes)
        self.calls: list[tuple[str, str, str]] = []

    def __call__(self, model: str, effort: str, prompt: str) -> str:
        self.calls.append((model, effort, prompt))
        if not self.outcomes:
            raise AssertionError("unexpected transport call")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, str)
        return outcome


def judge_json(checklist: list[str], passes: list[bool] | None = None) -> str:
    if passes is None:
        passes = [True] * len(checklist)
    return json.dumps(
        {
            "items": [
                {"item": item, "pass": passed, "evidence": f"evidence {index}"}
                for index, (item, passed) in enumerate(zip(checklist, passes))
            ]
        }
    )


class TrialRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="gambit-trials-")
        self.root = Path(self.temporary.name)
        (self.root / "tests" / "fixtures" / "trials" / "demo").mkdir(
            parents=True
        )
        (self.root / "skills" / "demo").mkdir(parents=True)
        (self.root / "contracts").mkdir()
        (self.root / "skills" / "demo" / "SKILL.md").write_text(
            "Do the demonstrated thing.\n", encoding="utf-8"
        )
        (self.root / "contracts" / "models.md").write_text(
            "Use the configured role.\n", encoding="utf-8"
        )
        self.checklist = ["states the result", "does not invent facts"]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_fixture(
        self,
        *,
        name: str = "basic",
        skill: str = "demo",
        text: str = "skills/demo/SKILL.md",
        neighbors: list[str] | None = None,
        exercise: str = "Answer the exercise.",
        checklist: list[str] | None = None,
        payload_override: dict[str, object] | None = None,
    ) -> Path:
        if neighbors is None:
            neighbors = ["contracts/models.md"]
        if checklist is None:
            checklist = self.checklist
        payload: dict[str, object] = {
            "skill": skill,
            "text": text,
            "neighbors": neighbors,
            "exercise": exercise,
            "checklist": checklist,
        }
        if payload_override is not None:
            payload = payload_override
        path = (
            self.root
            / "tests"
            / "fixtures"
            / "trials"
            / skill
            / f"{name}.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def load_one(self) -> object:
        self.write_fixture()
        loaded = trials.load_fixtures(self.root, "demo")
        self.assertEqual(1, len(loaded))
        return loaded[0]

    def test_fixture_loading_and_validation(self) -> None:
        fixture = self.load_one()
        self.assertEqual("demo", fixture.skill)
        self.assertEqual("basic", fixture.name)
        self.assertEqual("skills/demo/SKILL.md", fixture.text)
        self.assertEqual(("contracts/models.md",), fixture.neighbors)
        self.assertEqual(tuple(self.checklist), fixture.checklist)

        bad = self.write_fixture(
            name="bad",
            payload_override={
                "skill": "demo",
                "text": "skills/demo/SKILL.md",
                "neighbors": [],
                "exercise": "exercise",
            },
        )
        with self.assertRaisesRegex(trials.FixtureError, "checklist"):
            trials.load_fixture(self.root, bad)

        bad.write_text(
            json.dumps(
                {
                    "skill": "demo",
                    "text": "/absolute/SKILL.md",
                    "neighbors": [],
                    "exercise": "exercise",
                    "checklist": ["binary item"],
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(trials.FixtureError, "repo-relative"):
            trials.load_fixture(self.root, bad)

    def test_cell_id_and_hashes_cover_exact_file_bytes(self) -> None:
        fixture = self.load_one()
        self.assertEqual("demo/basic@sol-low", trials.cell_id(fixture, "sol-low"))
        hashes = trials.fixture_hashes(self.root, fixture)
        fixture_path = self.root / "tests/fixtures/trials/demo/basic.json"
        text_path = self.root / "skills/demo/SKILL.md"
        neighbor_path = self.root / "contracts/models.md"
        self.assertEqual(
            hashlib.sha256(fixture_path.read_bytes()).hexdigest(), hashes["fixture"]
        )
        self.assertEqual(
            hashlib.sha256(text_path.read_bytes()).hexdigest(), hashes["text"]
        )
        self.assertEqual(
            {
                "contracts/models.md": hashlib.sha256(
                    neighbor_path.read_bytes()
                ).hexdigest()
            },
            hashes["neighbors"],
        )

    def test_subject_prompt_contains_skill_neighbors_and_exercise_markers(self) -> None:
        fixture = self.load_one()
        prompt = trials.subject_prompt(self.root, fixture)
        self.assertIn(
            "The text between the BEGIN/END SKILL markers is your complete workflow instructions; follow it exactly.",
            prompt,
        )
        self.assertIn("BEGIN SKILL\nDo the demonstrated thing.\nEND SKILL", prompt)
        self.assertIn(
            "BEGIN REFERENCE contracts/models.md\nUse the configured role.\nEND REFERENCE contracts/models.md",
            prompt,
        )
        self.assertIn("BEGIN EXERCISE\nAnswer the exercise.\nEND EXERCISE", prompt)

    def test_subject_transport_failure_retries_once(self) -> None:
        fixture = self.load_one()
        fake = FakeTransport(
            OSError("disconnected"),
            "subject answer",
            judge_json(self.checklist),
        )
        record = trials.run_cell(self.root, fixture, "sol-low", fake)
        self.assertEqual("ok", record["status"])
        self.assertTrue(record["pass"])
        self.assertEqual(3, len(fake.calls))
        self.assertEqual("low", fake.calls[0][1])
        self.assertEqual("low", fake.calls[1][1])
        self.assertEqual("xhigh", fake.calls[2][1])

    def test_second_subject_transport_failure_is_recorded(self) -> None:
        fixture = self.load_one()
        fake = FakeTransport(OSError("first"), OSError("second"))
        record = trials.run_cell(self.root, fixture, "astra-high", fake)
        self.assertEqual("transport_failure", record["status"])
        self.assertFalse(record["pass"])
        self.assertEqual("", record["response"])
        self.assertEqual([], record["items"])
        self.assertEqual(2, len(fake.calls))

    def test_judge_output_matches_numbered_items_by_position(self) -> None:
        checklist = ("first item", "second item", "third item")
        response = json.dumps(
            {
                "items": [
                    {"item": "1. first item", "pass": True, "evidence": "one"},
                    {"item": "2) second item", "pass": True, "evidence": "two"},
                    {
                        "item": "  third   item  ",
                        "pass": True,
                        "evidence": "three",
                    },
                ]
            }
        )

        parsed = trials.parse_judge_output(response, checklist)

        self.assertEqual(3, len(parsed))
        self.assertTrue(all(item["pass"] is True for item in parsed))

    def test_judge_output_extracts_fenced_or_surrounded_object(self) -> None:
        payload = json.loads(judge_json(self.checklist))
        payload["summary"] = "extra top-level keys are ignored"
        raw = json.dumps(payload)
        responses = [
            f"```json\n{raw}\n```",
            f"```\n{raw}\n```",
            f"The verdict follows.\n{raw}",
            f"{raw}\nThat is the verdict.",
            f"The verdict follows.\n{raw}\nThat is the verdict.",
        ]

        for response in responses:
            with self.subTest(response=response):
                parsed = trials.parse_judge_output(response, tuple(self.checklist))
                self.assertEqual(2, len(parsed))

    def test_judge_output_rejects_invalid_item_data(self) -> None:
        invalid_payloads = {
            "missing items": {"summary": "no verdict"},
            "wrong item count": {
                "items": [
                    {
                        "item": self.checklist[0],
                        "pass": True,
                        "evidence": "only one item",
                    }
                ]
            },
            "non-boolean pass": {
                "items": [
                    {
                        "item": self.checklist[0],
                        "pass": "true",
                        "evidence": "first",
                    },
                    {
                        "item": self.checklist[1],
                        "pass": True,
                        "evidence": "second",
                    },
                ]
            },
            "mismatched normalized text": {
                "items": [
                    {
                        "item": "1. states the wrong result",
                        "pass": True,
                        "evidence": "first",
                    },
                    {
                        "item": self.checklist[1],
                        "pass": True,
                        "evidence": "second",
                    },
                ]
            },
            "non-string evidence": {
                "items": [
                    {
                        "item": self.checklist[0],
                        "pass": True,
                        "evidence": ["first"],
                    },
                    {
                        "item": self.checklist[1],
                        "pass": True,
                        "evidence": "second",
                    },
                ]
            },
        }

        for name, payload in invalid_payloads.items():
            with self.subTest(name=name):
                with self.assertRaises(trials.JudgeParseError):
                    trials.parse_judge_output(
                        json.dumps(payload), tuple(self.checklist)
                    )

    def test_judge_scores_every_item(self) -> None:
        fixture = self.load_one()
        fake = FakeTransport(
            "subject answer", judge_json(self.checklist, [True, False])
        )
        record = trials.run_cell(self.root, fixture, "sol-low", fake)
        self.assertEqual("ok", record["status"])
        self.assertFalse(record["pass"])
        self.assertEqual(self.checklist, [item["item"] for item in record["items"]])

    def test_judge_prompt_allows_numbered_or_unnumbered_item_text(self) -> None:
        prompt = trials.judge_prompt(tuple(self.checklist), "subject answer")
        self.assertIn("with or without its number", prompt)

    def test_judge_parse_failure_retries_once_then_records_failure(self) -> None:
        fixture = self.load_one()
        recovered = FakeTransport(
            "subject answer", "not json", judge_json(self.checklist)
        )
        record = trials.run_cell(self.root, fixture, "sol-low", recovered)
        self.assertEqual("ok", record["status"])
        self.assertTrue(record["pass"])
        self.assertEqual(3, len(recovered.calls))

        failed = FakeTransport(
            "subject answer", "first invalid verdict", "last invalid verdict"
        )
        record = trials.run_cell(self.root, fixture, "sol-low", failed)
        self.assertEqual("judge_failure", record["status"])
        self.assertFalse(record["pass"])
        self.assertEqual("subject answer", record["response"])
        self.assertEqual([], record["items"])
        self.assertEqual("last invalid verdict", record["judge_raw"])
        self.assertEqual(3, len(failed.calls))

    def test_check_fresh_reports_missing_stale_and_failed_cells(self) -> None:
        fixture = self.load_one()
        current_hashes = trials.fixture_hashes(self.root, fixture)
        identifiers = [trials.cell_id(fixture, name) for name in trials.SUBJECTS]

        problems = trials.check_fresh(self.root, [fixture], {})
        self.assertEqual([f"missing {identifier}" for identifier in identifiers], problems)

        results = {
            identifier: {"status": "ok", "pass": True, "hashes": current_hashes}
            for identifier in identifiers
        }
        results[identifiers[0]] = {
            "status": "ok",
            "pass": True,
            "hashes": {**current_hashes, "text": "0" * 64},
        }
        self.assertEqual(
            [f"stale {identifiers[0]}"],
            trials.check_fresh(self.root, [fixture], results),
        )

        results[identifiers[0]] = {
            "status": "ok",
            "pass": False,
            "hashes": current_hashes,
        }
        self.assertEqual(
            [f"failing {identifiers[0]}"],
            trials.check_fresh(self.root, [fixture], results),
        )

        results[identifiers[0]] = {
            "status": "judge_failure",
            "pass": False,
            "hashes": current_hashes,
        }
        self.assertEqual(
            [f"failing {identifiers[0]}"],
            trials.check_fresh(self.root, [fixture], results),
        )

        results[identifiers[0]] = {
            "status": "ok",
            "pass": True,
            "hashes": current_hashes,
        }
        self.assertEqual([], trials.check_fresh(self.root, [fixture], results))

    def test_result_file_update_is_atomic_and_preserves_other_cells(self) -> None:
        results_path = self.root / "tests/fixtures/trials/results.json"
        results_path.write_text(
            json.dumps({"other/cell@sol-low": {"pass": True}}), encoding="utf-8"
        )
        new_record = {"status": "ok", "pass": True}
        real_replace = os.replace
        replacements: list[tuple[Path, Path]] = []

        def recording_replace(
            source: str | os.PathLike[str], destination: str | os.PathLike[str]
        ) -> None:
            replacements.append((Path(source), Path(destination)))
            real_replace(source, destination)

        with mock.patch.object(trials.os, "replace", side_effect=recording_replace):
            trials.store_result(self.root, "demo/basic@sol-low", new_record)

        stored = json.loads(results_path.read_text(encoding="utf-8"))
        self.assertEqual({"pass": True}, stored["other/cell@sol-low"])
        self.assertEqual(new_record, stored["demo/basic@sol-low"])
        self.assertEqual(1, len(replacements))
        self.assertNotEqual(results_path, replacements[0][0])
        self.assertEqual(results_path, replacements[0][1])
        self.assertFalse(replacements[0][0].exists())

    def test_cli_exit_codes_writes_results_and_never_networks_for_checks(self) -> None:
        self.write_fixture()
        passing = FakeTransport(
            "answer one",
            judge_json(self.checklist),
            "answer two",
            judge_json(self.checklist),
        )
        output = io.StringIO()
        self.assertEqual(
            0,
            trials.main(
                ["--skill", "demo"],
                root=self.root,
                transport=passing,
                output=output,
            ),
        )
        results = json.loads(
            (self.root / "tests/fixtures/trials/results.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(2, len(results))

        never = FakeTransport()
        self.assertEqual(
            0,
            trials.main(
                ["--check-fresh"], root=self.root, transport=never, output=io.StringIO()
            ),
        )
        self.assertEqual([], never.calls)

        first_id = sorted(results)[0]
        results[first_id]["pass"] = False
        (self.root / "tests/fixtures/trials/results.json").write_text(
            json.dumps(results), encoding="utf-8"
        )
        failed_output = io.StringIO()
        self.assertEqual(
            1,
            trials.main(
                ["--check-fresh"], root=self.root, transport=never, output=failed_output
            ),
        )
        self.assertIn(f"failing {first_id}", failed_output.getvalue())

        failing_root = Path(tempfile.mkdtemp(dir=self.temporary.name))
        (failing_root / "tests/fixtures/trials/demo").mkdir(parents=True)
        (failing_root / "skills/demo").mkdir(parents=True)
        (failing_root / "skills/demo/SKILL.md").write_text("text", encoding="utf-8")
        payload = {
            "skill": "demo",
            "text": "skills/demo/SKILL.md",
            "neighbors": [],
            "exercise": "exercise",
            "checklist": ["passes"],
        }
        (failing_root / "tests/fixtures/trials/demo/basic.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
        failing = FakeTransport(
            "one",
            judge_json(["passes"], [False]),
            "two",
            judge_json(["passes"], [True]),
        )
        self.assertEqual(
            1,
            trials.main(
                ["--skill", "demo"],
                root=failing_root,
                transport=failing,
                output=io.StringIO(),
            ),
        )

    def test_cli_check_fresh_passes_with_no_fixtures(self) -> None:
        empty_root = Path(tempfile.mkdtemp(dir=self.temporary.name))
        (empty_root / "tests/fixtures/trials").mkdir(parents=True)
        self.assertEqual(
            0,
            trials.main(
                ["--check-fresh"],
                root=empty_root,
                transport=FakeTransport(),
                output=io.StringIO(),
            ),
        )

    def test_cli_all_runs_fixtures_from_every_skill(self) -> None:
        self.write_fixture()
        (self.root / "skills/other").mkdir()
        (self.root / "skills/other/SKILL.md").write_text(
            "Other instructions.\n", encoding="utf-8"
        )
        other_checklist = ["other item"]
        self.write_fixture(
            name="second",
            skill="other",
            text="skills/other/SKILL.md",
            neighbors=[],
            checklist=other_checklist,
        )
        fake = FakeTransport(
            "demo sol",
            judge_json(self.checklist),
            "demo astra",
            judge_json(self.checklist),
            "other sol",
            judge_json(other_checklist),
            "other astra",
            judge_json(other_checklist),
        )
        self.assertEqual(
            0,
            trials.main(
                ["--all"], root=self.root, transport=fake, output=io.StringIO()
            ),
        )
        results = trials.load_results(self.root)
        self.assertEqual(
            {
                "demo/basic@sol-low",
                "demo/basic@astra-high",
                "other/second@sol-low",
                "other/second@astra-high",
            },
            set(results),
        )

    def test_http_transport_sends_confirmed_messages_api_fields(self) -> None:
        key_path = self.root / "patchbay-key"
        key_path.write_text("secret-key\n", encoding="utf-8")
        captured: dict[str, object] = {}

        class Response:
            status = 200

            def __enter__(self) -> "Response":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(
                    {
                        "content": [
                            {"type": "text", "text": "transport reply"}
                        ]
                    }
                ).encode("utf-8")

        def urlopen(request: object, timeout: int) -> Response:
            captured["request"] = request
            captured["timeout"] = timeout
            return Response()

        with (
            mock.patch.object(trials, "PATCHBAY_KEY_FILE", key_path),
            mock.patch.object(trials.urllib.request, "urlopen", side_effect=urlopen),
        ):
            reply = trials.patchbay_transport("chatgpt/sol", "low", "prompt")

        self.assertEqual("transport reply", reply)
        request = captured["request"]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(
            {
                "model": "chatgpt/sol",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": "prompt"}],
                "output_config": {"effort": "low"},
            },
            body,
        )
        self.assertEqual(300, captured["timeout"])
        self.assertEqual("2023-06-01", request.get_header("Anthropic-version"))
        self.assertEqual("secret-key", request.get_header("X-patchbay-key"))

    def test_cli_dry_run_prints_both_prompts_without_transport(self) -> None:
        self.write_fixture()
        fake = FakeTransport()
        output = io.StringIO()
        self.assertEqual(
            0,
            trials.main(
                ["--dry-run", "--skill", "demo"],
                root=self.root,
                transport=fake,
                output=output,
            ),
        )
        rendered = output.getvalue()
        self.assertIn("BEGIN SKILL", rendered)
        self.assertIn("BEGIN REFERENCE contracts/models.md", rendered)
        self.assertIn("BEGIN EXERCISE", rendered)
        self.assertIn("<SUBJECT RESPONSE>", rendered)
        self.assertEqual([], fake.calls)

    def test_cli_probe_calls_each_subject_and_judge(self) -> None:
        fake = FakeTransport("sol reply", "astra reply", "judge reply")
        output = io.StringIO()
        self.assertEqual(
            0,
            trials.main(
                ["--probe"], root=self.root, transport=fake, output=output
            ),
        )
        self.assertEqual(
            [
                ("chatgpt/sol", "low"),
                ("chatgpt/astra", "high"),
                ("chatgpt/sol", "xhigh"),
            ],
            [(model, effort) for model, effort, _ in fake.calls],
        )
        self.assertIn("sol-low: 200 sol reply", output.getvalue())
        self.assertIn("astra-high: 200 astra reply", output.getvalue())
        self.assertIn("judge: 200 judge reply", output.getvalue())


if __name__ == "__main__":
    unittest.main()
