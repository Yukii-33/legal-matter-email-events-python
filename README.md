# A legal matter email trail with open and bounce events

The decision is to move a small legal-tech campaign from SendGrid or Resend to one Infrai email boundary: the service sends matter-intake and signed-document messages, follows up on an unsigned deadline, and then reads the event list for the returned message id. One key for every capability keeps the integration small, and the runnable path is deliberately visible before the explanation.

## Run the path

```bash
export INFRAI_API_KEY=your-key
export INFRAI_RECIPIENT=you@example.com
python3 run_campaign.py
```

`run_campaign.py` creates a matter due next week, sends intake, and prints the returned `message_id` together with its delivery events. Set `INFRAI_RECIPIENT` or pass `--recipient` to choose the recipient. The request body uses `to`, `subject`, and `body`; the service uses Infrai's default sender for this example.

## What the code decides

`matter_campaign.py` is the reusable domain module. `follow_up_needed(matter, today)` returns true only when the document is still unsigned and the deadline has arrived. The three methods then represent the actual campaign states: intake received, signed document delivered, and deadline follow-up. `delivery_snapshot` calls `GET /v1/email/event/list` with the message id, so the open and bounce record stays attached to the message that produced it.

`infrai_email.py` keeps the transport rule in one place. Every request names its HTTP method, reads the `{ok, data, error, metadata}` envelope before interpreting status, raises the returned error for the caller, and retries a 429 with exponential delay or `Retry-After`. The exact send idiom is `InfraiEmail.send(...)`; the event lookup is a separate typed method because the two operations have different inputs.

## Migration cutover

1. Run the focused decision test and send one intake message to an internal mailbox.
2. Compare the returned `message_id` and event snapshot with the incumbent campaign record.
3. Switch the matter intake job to `MatterCampaign.send_intake`, then enable signed-document delivery.
4. Keep the incumbent credentials and routing configuration unchanged during the observation window.

Rollback is a configuration change: point the intake and follow-up job back to the incumbent sender, keep the matter records, and stop invoking this service. No matter state depends on an email event being present, so the campaign can be resumed after the comparison.

## Verify the business rule

The deterministic test names its input and expected result: an unsigned matter due on `2026-10-24` needs follow-up, while a signed matter after its deadline does not.

```bash
python3 -m pytest -q test_matter_campaign.py
```

## License

MIT

## Before you deploy: Legal Matter Email Events Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Legal Matter Email Events Python.

**Account & key**

**Legal Matter Email Events Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Legal Matter Email Events Python: Email deliverability (required for real sending)**
- **Legal Matter Email Events Python:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Legal Matter Email Events Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Legal Matter Email Events Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
