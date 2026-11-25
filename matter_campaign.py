"""Matter intake, signed delivery, and deadline follow-up."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from infrai_email import EmailResult, InfraiEmail


@dataclass(frozen=True)
class Matter:
    matter_id: str
    client_email: str
    deadline: date
    signed_document: bool = False


def follow_up_needed(matter: Matter, today: date) -> bool:
    return not matter.signed_document and today >= matter.deadline


class MatterCampaign:
    def __init__(self, email: InfraiEmail):
        self.email = email

    def send_intake(self, matter: Matter) -> EmailResult:
        return self.email.send(matter.client_email, f"Matter {matter.matter_id}: intake received",
                               "Your matter intake is recorded. We will review the details next.")

    def send_signed_document(self, matter: Matter) -> EmailResult:
        return self.email.send(matter.client_email, f"Matter {matter.matter_id}: signed document",
                               "Your signed document is ready for review in the matter record.")

    def send_deadline_follow_up(self, matter: Matter, today: date) -> EmailResult | None:
        if not follow_up_needed(matter, today):
            return None
        return self.email.send(matter.client_email, f"Matter {matter.matter_id}: deadline follow-up",
                               "Please send the outstanding signed document so this matter can proceed.")

    def delivery_snapshot(self, message_id: str) -> dict[str, Any]:
        return self.email.events(message_id)
