from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from .core import run
from .models import Target
from .transports import SMTPTransport, WebhookTransport


def load_config(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        if path.suffix.lower() == ".json":
            return json.load(handle)
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(prog="claimwatch", description="Watch handles and domains for identity changes.")
    parser.add_argument("--config", "-c", type=Path, default=Path("claimwatch.yml"))
    parser.add_argument("--state", type=Path, default=Path(".claimwatch/state.json"))
    parser.add_argument("--no-alerts", action="store_true", help="Check and persist state without sending alerts")
    args = parser.parse_args()
    config = load_config(args.config)
    targets = [Target(item["platform"], item.get("handle") or item.get("domain") or item["value"], item.get("label")) for item in config.get("targets", [])]
    if not targets:
        parser.error("config must contain at least one target")
    observations, events = run(targets, args.state, github_token=os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"observations": [item.to_dict() for item in observations], "events": [item.to_dict() for item in events]}, indent=2))
    if events and not args.no_alerts:
        alert_config = config.get("alerts", {})
        if webhook := alert_config.get("webhook"):
            WebhookTransport(os.path.expandvars(webhook["url"]), webhook.get("headers")).send(events)
        if smtp := alert_config.get("smtp"):
            SMTPTransport({key: os.path.expandvars(str(value)) for key, value in smtp.items()}).send(events)
    if any(item.status == "error" for item in observations):
        sys.exit(2)


if __name__ == "__main__":
    main()
