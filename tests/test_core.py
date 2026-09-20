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
