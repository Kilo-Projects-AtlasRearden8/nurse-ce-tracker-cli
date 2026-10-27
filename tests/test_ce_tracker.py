"""Tests for Nurse CE Tracker.

Education only. Not medical advice. Not legal advice.
Licensed under MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import date, timedelta
from nurse_ce_tracker import (
    CEEntry,
    LicenseInfo,
    CEStore,
    parse_date,
    calculate_renewal_deadline,
    days_until_renewal,
)


class TestParseDate:
    """Tests for date parsing."""

    def test_valid_date(self):
        assert parse_date("2026-01-15") == date(2026, 1, 15)

    def test_invalid_date_format(self):
        with pytest.raises(Exception):
            parse_date("01/15/2026")

    def test_invalid_date(self):
        with pytest.raises(Exception):
            parse_date("2026-13-45")


class TestDateMath:
    """Tests for date calculation functions."""

    def test_calculate_renewal_deadline_future(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-12-31",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        # From mid-2026, next renewal should be 2026-12-31
        deadline = calculate_renewal_deadline(license_info, date(2026, 6, 15))
        assert deadline == date(2026, 12, 31)

    def test_calculate_renewal_deadline_past(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2024-12-31",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        # From 2026, next renewal should be 2026-12-31 (next even cycle)
        deadline = calculate_renewal_deadline(license_info, date(2026, 6, 15))
        assert deadline == date(2026, 12, 31)

    def test_calculate_renewal_deadline_exact(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-06-15",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        # Exact date should return same date
        deadline = calculate_renewal_deadline(license_info, date(2026, 6, 15))
        assert deadline == date(2026, 6, 15)

    def test_days_until_renewal_positive(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-12-31",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        days = days_until_renewal(license_info, date(2026, 6, 15))
        assert days == (date(2026, 12, 31) - date(2026, 6, 15)).days

    def test_days_until_renewal_zero(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-06-15",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        days = days_until_renewal(license_info, date(2026, 6, 15))
        assert days == 0

    def test_days_until_renewal_negative(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-01-01",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        days = days_until_renewal(license_info, date(2026, 6, 15))
        assert days < 0


class TestCEEntry:
    """Tests for CEEntry dataclass."""

    def test_create_entry(self):
        entry = CEEntry(
            id="test123",
            date="2026-01-15",
            title="Test Course",
            provider="Test Provider",
            hours=2.5,
            category="clinical",
            notes="Good course"
        )
        assert entry.hours == 2.5
        assert entry.category == "clinical"

    def test_entry_to_dict(self):
        entry = CEEntry(
            id="test123",
            date="2026-01-15",
            title="Test Course",
            provider="Test Provider",
            hours=2.5,
            category="clinical"
        )
        d = entry.to_dict()
        assert d["hours"] == 2.5
        assert d["title"] == "Test Course"

    def test_entry_from_dict(self):
        data = {
            "id": "test123",
            "date": "2026-01-15",
            "title": "Test Course",
            "provider": "Test Provider",
            "hours": 2.5,
            "category": "clinical",
            "notes": ""
        }
        entry = CEEntry.from_dict(data)
        assert entry.hours == 2.5


class TestLicenseInfo:
    """Tests for LicenseInfo dataclass."""

    def test_create_license(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-12-31",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        assert license_info.state == "IN"
        assert license_info.required_hours == 30.0

    def test_license_to_dict(self):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-12-31",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        d = license_info.to_dict()
        assert d["state"] == "IN"

    def test_license_from_dict(self):
        data = {
            "license_number": "RN12345",
            "state": "IN",
            "renewal_date": "2026-12-31",
            "renewal_cycle_years": 2,
            "required_hours": 30.0
        }
        license_info = LicenseInfo.from_dict(data)
        assert license_info.required_hours == 30.0


class TestCEStore:
    """Tests for CEStore."""

    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield CEStore(Path(tmpdir))

    def test_add_and_get_entry(self, store):
        entry = CEEntry(
            id="test1",
            date="2026-01-15",
            title="Course 1",
            provider="Provider A",
            hours=2.0,
            category="clinical"
        )
        store.add_entry(entry)
        entries = store.get_entries()
        assert len(entries) == 1
        assert entries[0].title == "Course 1"

    def test_total_hours(self, store):
        store.add_entry(CEEntry(id="1", date="2026-01-15", title="A", provider="P", hours=2.0, category="clinical"))
        store.add_entry(CEEntry(id="2", date="2026-02-15", title="B", provider="P", hours=3.0, category="pharmacology"))
        store.add_entry(CEEntry(id="3", date="2026-03-15", title="C", provider="P", hours=1.5, category="clinical"))
        
        total = store.total_hours()
        assert total == 6.5

    def test_total_hours_with_range(self, store):
        store.add_entry(CEEntry(id="1", date="2026-01-15", title="A", provider="P", hours=2.0, category="clinical"))
        store.add_entry(CEEntry(id="2", date="2026-02-15", title="B", provider="P", hours=3.0, category="pharmacology"))
        store.add_entry(CEEntry(id="3", date="2026-03-15", title="C", provider="P", hours=1.5, category="clinical"))
        
        total = store.total_hours(date(2026, 2, 1), date(2026, 2, 28))
        assert total == 3.0

    def test_hours_by_category(self, store):
        store.add_entry(CEEntry(id="1", date="2026-01-15", title="A", provider="P", hours=2.0, category="clinical"))
        store.add_entry(CEEntry(id="2", date="2026-02-15", title="B", provider="P", hours=3.0, category="pharmacology"))
        store.add_entry(CEEntry(id="3", date="2026-03-15", title="C", provider="P", hours=1.5, category="clinical"))
        
        by_cat = store.hours_by_category()
        assert by_cat["clinical"] == 3.5
        assert by_cat["pharmacology"] == 3.0

    def test_hours_by_category_with_range(self, store):
        store.add_entry(CEEntry(id="1", date="2026-01-15", title="A", provider="P", hours=2.0, category="clinical"))
        store.add_entry(CEEntry(id="2", date="2026-02-15", title="B", provider="P", hours=3.0, category="pharmacology"))
        
        by_cat = store.hours_by_category(date(2026, 2, 1), date(2026, 2, 28))
        assert by_cat["pharmacology"] == 3.0
        assert "clinical" not in by_cat

    def test_remove_entry(self, store):
        entry = CEEntry(id="test1", date="2026-01-15", title="Course", provider="P", hours=2.0, category="clinical")
        store.add_entry(entry)
        assert store.remove_entry("test1") is True
        assert len(store.get_entries()) == 0
        assert store.remove_entry("nonexistent") is False

    def test_license_persistence(self, store):
        license_info = LicenseInfo(
            license_number="RN12345",
            state="IN",
            renewal_date="2026-12-31",
            renewal_cycle_years=2,
            required_hours=30.0
        )
        store.set_license(license_info)
        retrieved = store.get_license()
        assert retrieved.license_number == "RN12345"
        assert retrieved.state == "IN"

    def test_get_entries_in_range(self, store):
        store.add_entry(CEEntry(id="1", date="2026-01-15", title="A", provider="P", hours=2.0, category="clinical"))
        store.add_entry(CEEntry(id="2", date="2026-02-15", title="B", provider="P", hours=3.0, category="pharmacology"))
        store.add_entry(CEEntry(id="3", date="2026-03-15", title="C", provider="P", hours=1.5, category="clinical"))
        
        entries = store.get_entries_in_range(date(2026, 2, 1), date(2026, 2, 28))
        assert len(entries) == 1
        assert entries[0].title == "B"


class TestIntegration:
    """Integration tests simulating CLI workflows."""

    def test_full_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = CEStore(Path(tmpdir))
            
            # Set license
            license_info = LicenseInfo(
                license_number="RN12345",
                state="IN",
                renewal_date="2026-12-31",
                renewal_cycle_years=2,
                required_hours=30.0
            )
            store.set_license(license_info)
            
            # Add entries across the cycle
            cycle_start = date(2025, 1, 1)
            cycle_end = date(2026, 12, 31)
            
            store.add_entry(CEEntry(id="1", date="2025-06-15", title="Course 1", provider="A", hours=10.0, category="clinical"))
            store.add_entry(CEEntry(id="2", date="2025-12-01", title="Course 2", provider="B", hours=5.0, category="pharmacology"))
            store.add_entry(CEEntry(id="3", date="2026-06-15", title="Course 3", provider="C", hours=8.0, category="ethics"))
            store.add_entry(CEEntry(id="4", date="2026-11-01", title="Course 4", provider="D", hours=7.0, category="clinical"))
            
            # Check totals
            total = store.total_hours(cycle_start, cycle_end)
            assert total == 30.0
            
            # Check by category
            by_cat = store.hours_by_category(cycle_start, cycle_end)
            assert by_cat["clinical"] == 17.0
            assert by_cat["pharmacology"] == 5.0
            assert by_cat["ethics"] == 8.0
            
            # Check renewal status
            days = days_until_renewal(license_info, date(2026, 6, 15))
            assert days > 0
            
            deadline = calculate_renewal_deadline(license_info, date(2026, 6, 15))
            assert deadline == date(2026, 12, 31)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])