#!/usr/bin/env python3
"""
Nurse CE Tracker CLI - Continuing Education Tracker for Nurses

Education only. Not medical advice. Not legal advice.
Licensed under MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict, field


@dataclass
class CEEntry:
    """A single continuing education entry."""
    id: str
    date: str
    title: str
    provider: str
    hours: float
    category: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CEEntry":
        return cls(**data)


@dataclass
class LicenseInfo:
    """License renewal information."""
    license_number: str
    state: str
    renewal_date: str
    renewal_cycle_years: int = 2
    required_hours: float = 30.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LicenseInfo":
        return cls(**data)


class CEStore:
    """Storage for CE entries and license info."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.entries_file = self.data_dir / "ce_entries.json"
        self.license_file = self.data_dir / "license_info.json"
        self._entries: List[CEEntry] = []
        self._license: Optional[LicenseInfo] = None
        self._load()

    def _load(self) -> None:
        if self.entries_file.exists():
            with open(self.entries_file, "r") as f:
                data = json.load(f)
                self._entries = [CEEntry.from_dict(e) for e in data]
        if self.license_file.exists():
            with open(self.license_file, "r") as f:
                data = json.load(f)
                self._license = LicenseInfo.from_dict(data)

    def _save_entries(self) -> None:
        with open(self.entries_file, "w") as f:
            json.dump([e.to_dict() for e in self._entries], f, indent=2)

    def _save_license(self) -> None:
        if self._license:
            with open(self.license_file, "w") as f:
                json.dump(self._license.to_dict(), f, indent=2)

    def add_entry(self, entry: CEEntry) -> None:
        self._entries.append(entry)
        self._save_entries()

    def remove_entry(self, entry_id: str) -> bool:
        for i, e in enumerate(self._entries):
            if e.id == entry_id:
                self._entries.pop(i)
                self._save_entries()
                return True
        return False

    def get_entries(self) -> List[CEEntry]:
        return sorted(self._entries, key=lambda e: e.date)

    def get_entries_in_range(self, start: date, end: date) -> List[CEEntry]:
        result = []
        for e in self._entries:
            entry_date = datetime.strptime(e.date, "%Y-%m-%d").date()
            if start <= entry_date <= end:
                result.append(e)
        return sorted(result, key=lambda e: e.date)

    def set_license(self, license_info: LicenseInfo) -> None:
        self._license = license_info
        self._save_license()

    def get_license(self) -> Optional[LicenseInfo]:
        return self._license

    def total_hours(self, start: Optional[date] = None, end: Optional[date] = None) -> float:
        entries = self._entries
        if start or end:
            entries = self.get_entries_in_range(
                start or date.min,
                end or date.max
            )
        return sum(e.hours for e in entries)

    def hours_by_category(self, start: Optional[date] = None, end: Optional[date] = None) -> Dict[str, float]:
        entries = self._entries
        if start or end:
            entries = self.get_entries_in_range(
                start or date.min,
                end or date.max
            )
        result: Dict[str, float] = {}
        for e in entries:
            result[e.category] = result.get(e.category, 0.0) + e.hours
        return result


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


def generate_id() -> str:
    """Generate a unique ID based on timestamp."""
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def calculate_renewal_deadline(license_info: LicenseInfo, from_date: Optional[date] = None) -> date:
    """Calculate the next renewal deadline from a given date."""
    base = from_date or date.today()
    renewal = datetime.strptime(license_info.renewal_date, "%Y-%m-%d").date()
    cycle_years = license_info.renewal_cycle_years

    if base <= renewal:
        return renewal

    # Find smallest n such that renewal + n * cycle_years >= base
    years_diff = base.year - renewal.year
    n = max(0, (years_diff + cycle_years - 1) // cycle_years)

    candidate = renewal.replace(year=renewal.year + n * cycle_years)

    # Adjust if candidate falls before base due to month/day differences
    while candidate < base:
        candidate = candidate.replace(year=candidate.year + cycle_years)

    return candidate


def days_until_renewal(license_info: LicenseInfo, from_date: Optional[date] = None) -> int:
    """Calculate days until next renewal."""
    deadline = calculate_renewal_deadline(license_info, from_date)
    base = from_date or date.today()
    return (deadline - base).days


def format_entry(entry: CEEntry) -> str:
    """Format a CE entry for display."""
    return f"  [{entry.id}] {entry.date} | {entry.hours:.1f}h | {entry.category} | {entry.title} ({entry.provider})"


def format_license(license_info: LicenseInfo) -> str:
    """Format license info for display."""
    days = days_until_renewal(license_info)
    deadline = calculate_renewal_deadline(license_info)
    status = "OVERDUE" if days < 0 else f"{days} days"
    return (
        f"License: {license_info.license_number} ({license_info.state})\n"
        f"  Renewal Date: {license_info.renewal_date} (every {license_info.renewal_cycle_years} years)\n"
        f"  Required Hours: {license_info.required_hours:.1f}\n"
        f"  Next Renewal: {deadline} ({status})"
    )


def cmd_add(args: argparse.Namespace, store: CEStore) -> int:
    """Add a new CE entry."""
    entry = CEEntry(
        id=generate_id(),
        date=args.date.isoformat(),
        title=args.title,
        provider=args.provider,
        hours=args.hours,
        category=args.category,
        notes=args.notes or ""
    )
    store.add_entry(entry)
    print(f"Added CE entry: {entry.title} ({entry.hours:.1f} hours)")
    return 0


def cmd_list(args: argparse.Namespace, store: CEStore) -> int:
    """List CE entries."""
    entries = store.get_entries()
    
    if args.start or args.end:
        start = parse_date(args.start) if args.start else date.min
        end = parse_date(args.end) if args.end else date.max
        entries = store.get_entries_in_range(start, end)
    
    if not entries:
        print("No CE entries found.")
        return 0
    
    print(f"Found {len(entries)} CE entr{'y' if len(entries) == 1 else 'ies'}:")
    for entry in entries:
        print(format_entry(entry))
        if args.verbose and entry.notes:
            print(f"      Notes: {entry.notes}")
    
    total = sum(e.hours for e in entries)
    print(f"\nTotal hours: {total:.1f}")
    return 0


def cmd_totals(args: argparse.Namespace, store: CEStore) -> int:
    """Show total hours, optionally by category and date range."""
    start = parse_date(args.start) if args.start else None
    end = parse_date(args.end) if args.end else None
    
    total = store.total_hours(start, end)
    print(f"Total CE hours: {total:.1f}")
    
    if args.by_category:
        by_cat = store.hours_by_category(start, end)
        if by_cat:
            print("\nBy category:")
            for cat, hours in sorted(by_cat.items()):
                print(f"  {cat}: {hours:.1f}h")
    
    return 0


def cmd_license(args: argparse.Namespace, store: CEStore) -> int:
    """Manage license information."""
    if args.set:
        license_info = LicenseInfo(
            license_number=args.number,
            state=args.state,
            renewal_date=args.renewal_date,
            renewal_cycle_years=args.cycle,
            required_hours=args.required
        )
        store.set_license(license_info)
        print("License information saved.")
        return 0
    
    license_info = store.get_license()
    if not license_info:
        print("No license information set. Use --set to configure.")
        return 1
    
    print(format_license(license_info))
    
    # Show progress toward renewal
    start = calculate_renewal_deadline(license_info) - timedelta(days=license_info.renewal_cycle_years * 365)
    end = calculate_renewal_deadline(license_info)
    hours_earned = store.total_hours(start, end)
    print(f"\nHours earned this cycle: {hours_earned:.1f} / {license_info.required_hours:.1f}")
    if hours_earned >= license_info.required_hours:
        print("✓ Requirement met!")
    else:
        remaining = license_info.required_hours - hours_earned
        print(f"  Remaining: {remaining:.1f} hours")
    
    return 0


def cmd_export(args: argparse.Namespace, store: CEStore) -> int:
    """Export CE entries to CSV."""
    entries = store.get_entries()
    
    if args.start or args.end:
        start = parse_date(args.start) if args.start else date.min
        end = parse_date(args.end) if args.end else date.max
        entries = store.get_entries_in_range(start, end)
    
    if not entries:
        print("No entries to export.")
        return 1
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ["id", "date", "title", "provider", "hours", "category", "notes"]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())
    
    print(f"Exported {len(entries)} entries to {output_path}")
    return 0


def cmd_remove(args: argparse.Namespace, store: CEStore) -> int:
    """Remove a CE entry by ID."""
    if store.remove_entry(args.id):
        print(f"Removed entry {args.id}")
        return 0
    else:
        print(f"Entry {args.id} not found.")
        return 1


def cmd_renewal(args: argparse.Namespace, store: CEStore) -> int:
    """Show renewal countdown and requirements."""
    license_info = store.get_license()
    if not license_info:
        print("No license information set. Use 'license --set' to configure.")
        return 1
    
    days = days_until_renewal(license_info)
    deadline = calculate_renewal_deadline(license_info)
    
    if days < 0:
        print(f"⚠ RENEWAL OVERDUE by {abs(days)} days! Deadline was {deadline}")
    elif days == 0:
        print(f"⚠ RENEWAL DUE TODAY! Deadline: {deadline}")
    elif days <= 30:
        print(f"⚠ Renewal due in {days} days ({deadline})")
    else:
        print(f"Renewal due in {days} days ({deadline})")
    
    # Cycle progress
    cycle_start = deadline - timedelta(days=license_info.renewal_cycle_years * 365)
    hours_earned = store.total_hours(cycle_start, deadline)
    print(f"\nCurrent cycle: {cycle_start} to {deadline}")
    print(f"Hours earned: {hours_earned:.1f} / {license_info.required_hours:.1f}")
    
    if hours_earned >= license_info.required_hours:
        print("✓ Requirement met!")
    else:
        remaining = license_info.required_hours - hours_earned
        print(f"Remaining: {remaining:.1f} hours")
        # Projected daily rate needed
        if days > 0:
            daily_rate = remaining / days
            print(f"Needed rate: {daily_rate:.2f} hours/day")
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="nurse-ce-tracker",
        description="Track continuing education hours and license renewal deadlines for nurses.",
        epilog="Education only. Not medical or legal advice. Copyright (c) 2026 Asdale Dynamics, LLC."
    )
    parser.add_argument(
        "--data-dir",
        default=Path.home() / ".nurse-ce-tracker",
        type=Path,
        help="Data directory (default: ~/.nurse-ce-tracker)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # add
    p_add = subparsers.add_parser("add", help="Add a CE entry")
    p_add.add_argument("date", type=parse_date, help="Date (YYYY-MM-DD)")
    p_add.add_argument("title", help="Course/activity title")
    p_add.add_argument("provider", help="Provider/organization")
    p_add.add_argument("hours", type=float, help="Credit hours")
    p_add.add_argument("category", help="Category (e.g., clinical, pharmacology, ethics)")
    p_add.add_argument("--notes", "-n", default="", help="Optional notes")
    p_add.set_defaults(func=cmd_add)
    
    # list
    p_list = subparsers.add_parser("list", help="List CE entries")
    p_list.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_list.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_list.add_argument("--verbose", "-v", action="store_true", help="Show notes")
    p_list.set_defaults(func=cmd_list)
    
    # totals
    p_totals = subparsers.add_parser("totals", help="Show total hours")
    p_totals.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_totals.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_totals.add_argument("--by-category", "-c", action="store_true", help="Break down by category")
    p_totals.set_defaults(func=cmd_totals)
    
    # license
    p_license = subparsers.add_parser("license", help="Manage license info")
    p_license.add_argument("--set", action="store_true", help="Set license information")
    p_license.add_argument("--number", help="License number")
    p_license.add_argument("--state", help="State (e.g., IN, CA)")
    p_license.add_argument("--renewal-date", help="Renewal date (YYYY-MM-DD)")
    p_license.add_argument("--cycle", type=int, default=2, help="Renewal cycle in years (default: 2)")
    p_license.add_argument("--required", type=float, default=30.0, help="Required CE hours (default: 30)")
    p_license.set_defaults(func=cmd_license)
    
    # export
    p_export = subparsers.add_parser("export", help="Export entries to CSV")
    p_export.add_argument("output", help="Output CSV file path")
    p_export.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_export.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_export.set_defaults(func=cmd_export)
    
    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a CE entry")
    p_remove.add_argument("id", help="Entry ID to remove")
    p_remove.set_defaults(func=cmd_remove)
    
    # renewal
    p_renewal = subparsers.add_parser("renewal", help="Show renewal countdown")
    p_renewal.set_defaults(func=cmd_renewal)
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    store = CEStore(args.data_dir)
    return args.func(args, store)


if __name__ == "__main__":
    sys.exit(main())