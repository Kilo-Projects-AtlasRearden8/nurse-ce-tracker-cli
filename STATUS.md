# STATUS.md

## What Was Built

**Nurse CE Tracker CLI** — a command-line Python tool for nurses to log continuing-education hours, track license-renewal deadlines, and export CSV reports.

Built by **Asdale Dynamics, LLC** (Dylan Asdale, RN, Indiana). Education only — not medical or legal advice. MIT License.

### Files

| File | Purpose |
|------|---------|
| `LICENSE` | MIT License, copyright Asdale Dynamics, LLC 2026 |
| `README.md` | Usage documentation with Asdale Dynamics credit |
| `pyproject.toml` | Project config, package metadata, dev dependencies |
| `nurse_ce_tracker/__init__.py` | Package init, public API exports |
| `nurse_ce_tracker/__main__.py` | CLI entry point: add, list, totals, license, export, remove, renewal |
| `tests/test_ce_tracker.py` | 24 tests covering date math, totals, CE entries, license, integration |
| `.gitignore` | Excludes build artifacts, venv, caches |

## How to Run

### Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

### CLI Usage

```bash
# Set license info
.venv/bin/nurse-ce-tracker license --set \
  --number RN12345 --state IN --renewal-date 2026-12-31 --cycle 2 --required 30

# Add CE entries
.venv/bin/nurse-ce-tracker add 2026-01-15 "IV Therapy" "NurseCEU" 2.0 clinical
.venv/bin/nurse-ce-tracker add 2026-02-20 "Pharm Review" "AANP" 3.0 pharmacology

# List entries
.venv/bin/nurse-ce-tracker list

# Totals
.venv/bin/nurse-ce-tracker totals --by-category

# Renewal countdown
.venv/bin/nurse-ce-tracker renewal

# Export CSV
.venv/bin/nurse-ce-tracker export ce_report.csv
```

### Run Tests

```bash
.venv/bin/pytest
```

## Verification Results

- **Tests:** 24 passed, 0 failed
- **CLI functional test:** All commands verified working (license set/add, add entries, list, totals by category, renewal countdown, CSV export)
- **Package build:** `pip install -e ".[dev]"` succeeds
- **No .github/workflows files** present
- **No secrets, API keys, or personal data** in any file
- **LICENSE copyright line:** `Copyright (c) 2026 Asdale Dynamics, LLC` (exact match)
- **README credits:** Asdale Dynamics, LLC credited in README
- **Git:** Initialized, two commits, plain messages, no Co-authored-by trailers, not pushed

## Known Gaps

- No `.github/workflows` CI configuration (intentionally omitted per requirements)
- No GUI — CLI only
- Data stored as JSON in `~/.nurse-ce-tracker/` (no database backend)
- No sync/backup or multi-device support
- Renewal cycle calculated by calendar years (365 days approximation for cycle start)
- No input validation on hours beyond float parsing (negative hours technically possible)
- No unit tests for CLI command functions directly (integration test covers full workflow)