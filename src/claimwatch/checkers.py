from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from .models import Observation, Target

USER_AGENT = "claimwatch/0.1 (+https://github.com/DeepanshuPal/claimwatch)"


def _request(url: str, *, timeout: int = 12, headers: dict[str, str] | None = None) -> tuple[int, bytes, dict[str, str]]:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


class Checker(ABC):
    @abstractmethod
    def check(self, target: Target) -> Observation: ...


class GitHubChecker(Checker):
    def __init__(self, token: str | None = None) -> None:
        self.token = token

    def check(self, target: Target) -> Observation:
        username = target.value.lstrip("@")
        url = f"https://api.github.com/users/{urllib.parse.quote(username)}"
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            status, body, response_headers = _request(url, headers=headers)
            if status == 404:
                return Observation(target, "available", detail="GitHub returned 404", evidence_url=url)
            if status == 200:
                data = json.loads(body)
                return Observation(
                    target,
                    "taken",
                    owner=data.get("id") and str(data["id"]),
                    last_activity=data.get("updated_at"),
                    detail=f"account login={data.get('login')}",
                    evidence_url=data.get("html_url") or url,
                )
            remaining = response_headers.get("X-RateLimit-Remaining")
            return Observation(target, "unknown", detail=f"GitHub HTTP {status}; rate-limit remaining={remaining}", evidence_url=url)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return Observation(target, "error", detail=str(exc), evidence_url=url)


class DomainChecker(Checker):
    def check(self, target: Target) -> Observation:
        domain = target.value.strip().lower().rstrip(".")
        url = f"https://rdap.org/domain/{urllib.parse.quote(domain)}"
        try:
            status, body, _ = _request(url)
            if status == 200:
                data: dict[str, Any] = json.loads(body)
                events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
                owner = data.get("handle") or data.get("ldhName")
                return Observation(
                    target,
                    "taken",
                    owner=str(owner) if owner else domain,
                    last_activity=events.get("last changed") or events.get("registration"),
                    detail=f"RDAP registration found; expiration={events.get('expiration', 'unknown')}",
                    evidence_url=url,
                )
            if status == 404:
                # A missing RDAP record is useful but not enough to declare every TLD buyable.
                try:
                    socket.getaddrinfo(domain, None)
                    return Observation(target, "taken", owner=domain, detail="No RDAP record; DNS resolves", evidence_url=url)
                except socket.gaierror:
                    return Observation(target, "available", detail="No RDAP record and DNS does not resolve; confirm with registrar", evidence_url=url)
            return Observation(target, "unknown", detail=f"RDAP HTTP {status}", evidence_url=url)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return Observation(target, "error", detail=str(exc), evidence_url=url)


class BestEffortProfileChecker(Checker):
    URLS: ClassVar[dict[str, str]] = {
        "x": "https://x.com/{handle}",
        "twitter": "https://x.com/{handle}",
        "instagram": "https://www.instagram.com/{handle}/",
        "tiktok": "https://www.tiktok.com/@{handle}",
    }

    def check(self, target: Target) -> Observation:
        handle = target.value.lstrip("@").strip()
        template = self.URLS[target.platform.lower()]
        url = template.format(handle=urllib.parse.quote(handle))
        try:
            status, _, _ = _request(url, headers={"Accept": "text/html"})
            if status == 404:
                return Observation(target, "available", detail="Public profile URL returned 404; best-effort signal only", evidence_url=url)
            if status == 200:
                return Observation(target, "taken", owner=handle.lower(), detail="Public profile URL returned 200; ownership and activity are not verified", evidence_url=url)
            return Observation(target, "unknown", detail=f"Public profile HTTP {status}; platform may be throttling or challenging requests", evidence_url=url)
        except OSError as exc:
            return Observation(target, "error", detail=str(exc), evidence_url=url)


def checker_for(platform: str, *, github_token: str | None = None) -> Checker:
    normalized = platform.lower()
    if normalized == "domain":
        return DomainChecker()
    if normalized == "github":
        return GitHubChecker(github_token)
    if normalized in BestEffortProfileChecker.URLS:
        return BestEffortProfileChecker()
    raise ValueError(f"Unsupported platform: {platform}")
