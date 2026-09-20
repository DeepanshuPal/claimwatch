from pathlib import Path

from claimwatch.core import diff, load_state, save_state
from claimwatch.models import Observation, Target


def test_first_seen_event():
    current = Observation(Target("github", "octocat"), "taken", owner="583231")
    assert [event.kind for event in diff({}, current)] == ["first_seen"]


def test_changes_are_specific():
    target = Target("domain", "example.com")
    current = Observation(target, "available", owner=None, last_activity="2026-01-01")
    previous = {target.key: {"status": "taken", "owner": "EXAMPLE", "last_activity": "2025-01-01"}}
    assert [event.kind for event in diff(previous, current)] == [
        "availability_changed", "owner_changed", "last_activity_changed"
    ]


def test_state_round_trip(tmp_path: Path):
    path = tmp_path / "state.json"
    item = Observation(Target("github", "octocat"), "taken", owner="583231")
    save_state(path, [item])
    assert load_state(path)[item.target.key]["owner"] == "583231"


def test_run_preserves_target_order_when_checks_finish_out_of_order(tmp_path, monkeypatch):
    import time

    from claimwatch import core

    def fake_check(target, github_token):
        if target.value == "slow":
            time.sleep(0.03)
        return Observation(target, "taken")

    monkeypatch.setattr(core, "_check", fake_check)
    targets = [Target("github", "slow"), Target("github", "fast")]
    observations, _ = core.run(targets, tmp_path / "state.json", workers=2)
    assert [item.target.value for item in observations] == ["slow", "fast"]
