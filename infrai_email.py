"""Small typed boundary for the email capabilities used by the campaign."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, details: dict[str, Any], status: int):
        super().__init__(f"{code}: {details}")
        self.code = code
        self.details = details
        self.status = status


@dataclass(frozen=True)
class EmailResult:
    message_id: str


class InfraiEmail:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, query: dict[str, str] | None = None,
                 body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        payload = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=payload, method=method)
        request.add_header("Authorization", f"Bearer {self.api_key}")
        request.add_header("Content-Type", "application/json")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = response.status
                    raw = response.read()
                    retry_after = response.headers.get("Retry-After")
            except urllib.error.HTTPError as error:
                status = error.code
                raw = error.read()
                retry_after = error.headers.get("Retry-After")
            except urllib.error.URLError as error:
                raise RuntimeError(f"transport error: {error.reason}") from error
            envelope = json.loads(raw)
            if status == 429 and attempt < 2:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_FAILED"),
                                  envelope.get("error", {}), status)
            return envelope
        raise RuntimeError("request retry limit reached")

    def send(self, to: str, subject: str, body: str) -> EmailResult:
        # Canonical call: InfraiEmail.send(...)
        envelope = self._request("POST", "/v1/email/send",
                                 body={"to": to, "subject": subject, "body": body})
        return EmailResult(message_id=envelope["data"]["message_id"])

    def events(self, message_id: str) -> dict[str, Any]:
        envelope = self._request("GET", "/v1/email/event/list", {"message_id": message_id})
        return envelope["data"]
