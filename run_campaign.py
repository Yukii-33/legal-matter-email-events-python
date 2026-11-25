"""Run one campaign path and print the message id plus event data."""

import argparse
import os
from datetime import date, timedelta

from infrai_email import InfraiEmail
from matter_campaign import Matter, MatterCampaign


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recipient",
        default=os.environ.get("INFRAI_RECIPIENT"),
        help="recipient email address (or set INFRAI_RECIPIENT)",
    )
    args = parser.parse_args()
    if not args.recipient:
        parser.error("--recipient or INFRAI_RECIPIENT is required")

    matter = Matter("MAT-104", args.recipient, date.today() + timedelta(days=7))
    campaign = MatterCampaign(InfraiEmail())
    sent = campaign.send_intake(matter)
    print("intake message_id:", sent.message_id)
    print("delivery events:", campaign.delivery_snapshot(sent.message_id))


if __name__ == "__main__":
    main()
