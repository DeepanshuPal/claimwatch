from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .checkers import checker_for
from .models import Event, Observation, Target

TRACKED_FIELDS = {
    "status": "availability_changed",
    "owner": "owner_changed",
    "last_activity": "last_activity_changed",
}


def load_state(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_state(path: Path, observations: list[Observation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {item.target.key: item.to_dict() for item in observations}
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def diff(previous: dict[str, dict[str, Any]], current: Observation) -> list[Event]:
    old = previous.get(current.target.key)
    if old is None:
        return [Event("first_seen", current.target, None, current.status, current.checked_at)]
    events: list[Event] = []
    now = current.to_dict()
    for field, kind in TRACKED_FIELDS.items():
        before, after = old.get(field), now.get(field)
        if before != after and (before is not None or after is not None):
            events.append(Event(kind, current.target, before, after, current.checked_at))
    return events


def run(targets: list[Target], state_path: Path, *, github_token: str | None = None) -> tuple[list[Observation], list[Event]]:
    previous = load_state(state_path)
    observations: list[Observation] = []
    events: list[Event] = []
    for target in targets:
        observation = checker_for(target.platform, github_token=github_token).check(target)
        observations.append(observation)
        events.extend(diff(previous, observation))
    save_state(state_path, observations)
    return observations, events
