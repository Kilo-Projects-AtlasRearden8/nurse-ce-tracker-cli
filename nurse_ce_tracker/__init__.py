"""Nurse CE Tracker - Continuing Education Tracker for Nurses.

Education only. Not medical advice. Not legal advice.
Licensed under MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
"""

from .__main__ import main, CEEntry, LicenseInfo, CEStore, parse_date, calculate_renewal_deadline, days_until_renewal

__version__ = "1.0.0"
__author__ = "Asdale Dynamics, LLC"
__license__ = "MIT"

__all__ = [
    "main",
    "CEEntry",
    "LicenseInfo",
    "CEStore",
    "parse_date",
    "calculate_renewal_deadline",
    "days_until_renewal",
]