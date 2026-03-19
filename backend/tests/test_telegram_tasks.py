from datetime import datetime

from app.tasks.telegram_tasks import _parse_message_datetime


def test_parse_message_datetime_accepts_utc_z_suffix():
    parsed = _parse_message_datetime("2026-03-01T11:10:05Z")

    assert parsed == datetime(2026, 3, 1, 11, 10, 5)


def test_parse_message_datetime_accepts_offset_with_trailing_z():
    parsed = _parse_message_datetime("2026-03-01T11:10:05+00:00Z")

    assert parsed == datetime(2026, 3, 1, 11, 10, 5)
