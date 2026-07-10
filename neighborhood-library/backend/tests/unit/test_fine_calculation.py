"""
Unit tests for the fine calculation logic in loan_service.
These tests have ZERO dependencies on the database.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.services.loan_service import calculate_fine

RATE = 0.50  # $0.50 per day


def make_dt(days_offset: float = 0) -> datetime:
    base = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(days=days_offset)


class TestCalculateFine:
    def test_returned_exactly_on_due_date_no_fine(self):
        due = make_dt(0)
        returned = make_dt(0)
        assert calculate_fine(due, returned, RATE) == Decimal("0.00")

    def test_returned_before_due_date_no_fine(self):
        due = make_dt(5)
        returned = make_dt(3)
        assert calculate_fine(due, returned, RATE) == Decimal("0.00")

    def test_returned_one_full_day_late(self):
        due = make_dt(0)
        returned = make_dt(1)
        assert calculate_fine(due, returned, RATE) == Decimal("0.50")

    def test_returned_one_second_late_counts_as_one_day(self):
        due = make_dt(0)
        returned = due + timedelta(seconds=1)
        assert calculate_fine(due, returned, RATE) == Decimal("0.50")

    def test_returned_7_days_late(self):
        due = make_dt(0)
        returned = make_dt(7)
        assert calculate_fine(due, returned, RATE) == Decimal("3.50")

    def test_returned_30_days_late(self):
        due = make_dt(0)
        returned = make_dt(30)
        assert calculate_fine(due, returned, RATE) == Decimal("15.00")

    def test_higher_rate(self):
        due = make_dt(0)
        returned = make_dt(3)
        assert calculate_fine(due, returned, rate_per_day=1.00) == Decimal("3.00")

    def test_partial_day_at_boundary(self):
        due = make_dt(0)
        returned = due + timedelta(hours=23, minutes=59, seconds=59)
        # 0 full days, 86399 seconds > 0  → counts as 1 day
        assert calculate_fine(due, returned, RATE) == Decimal("0.50")

    def test_fine_rounds_correctly(self):
        due = make_dt(0)
        returned = make_dt(3)
        assert calculate_fine(due, returned, rate_per_day=0.333) == Decimal("1.00")

    def test_zero_rate_always_zero_fine(self):
        due = make_dt(0)
        returned = make_dt(100)
        assert calculate_fine(due, returned, rate_per_day=0.0) == Decimal("0.00")
