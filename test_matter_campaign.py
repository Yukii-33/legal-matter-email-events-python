from datetime import date

from matter_campaign import Matter, follow_up_needed


def test_unsigned_matter_due_today_needs_follow_up():
    matter = Matter("MAT-7", "client@example.com", date(2026, 10, 24))
    assert follow_up_needed(matter, date(2026, 10, 24)) is True


def test_signed_matter_does_not_need_follow_up_after_deadline():
    matter = Matter("MAT-7", "client@example.com", date(2026, 10, 20), signed_document=True)
    assert follow_up_needed(matter, date(2026, 10, 24)) is False
