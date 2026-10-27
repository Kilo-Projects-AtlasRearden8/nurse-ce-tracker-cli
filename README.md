# Nurse CE Tracker CLI

A command-line tool for nurses to log continuing-education hours, track license-renewal deadlines, and export CSV reports.

> **Education only.** This tool is for tracking continuing education credits and license renewals. It does not provide medical advice, legal advice, or guarantee compliance with any licensing board. Always verify requirements with your state board of nursing.

## Features

- **Log CE entries** — Record date, title, provider, hours, category, and notes
- **Track license renewal** — Store license number, state, renewal date, cycle, and required hours
- **View totals** — See total hours overall, by date range, or broken down by category
- **Renewal countdown** — Days until renewal, hours earned this cycle, remaining hours needed
- **Export to CSV** — Export all entries or a date range for reporting
- **Local-first** — All data stored locally in `~/.nurse-ce-tracker/` as JSON

## Installation

```bash
# Clone and install in development mode
git clone <repository-url>
cd nurse-ce-tracker-cli
pip install -e .
```

Or install directly:

```bash
pip install -e .
```

The `nurse-ce-tracker` command will be available after installation.

## Quick Start

```bash
# Set up your license information
nurse-ce-tracker license --set \
  --number RN123456 \
  --state IN \
  --renewal-date 2026-12-31 \
  --cycle 2 \
  --required 30

# Add CE entries
nurse-ce-tracker add 2026-01-15 "IV Therapy Update" "NurseCEU" 2.0 clinical
nurse-ce-tracker add 2026-02-20 "Pharmacology Review" "AANP" 3.0 pharmacology --notes "Good refresher"
nurse-ce-tracker add 2026-03-10 "Ethics in Nursing" "MedBridge" 1.5 ethics

# View all entries
nurse-ce-tracker list

# View totals
nurse-ce-tracker totals
nurse-ce-tracker totals --by-category

# Check renewal status
nurse-ce-tracker renewal

# Export to CSV
nurse-ce-tracker export ce_report.csv
```

## Commands

| Command | Description |
|---------|-------------|
| `add` | Add a new CE entry |
| `list` | List all CE entries (optionally filtered by date range) |
| `totals` | Show total hours (optionally by category and date range) |
| `license` | View or set license information |
| `renewal` | Show renewal countdown and cycle progress |
| `export` | Export entries to CSV |
| `remove` | Remove a CE entry by ID |

### `add` — Add a CE Entry

```bash
nurse-ce-tracker add DATE TITLE PROVIDER HOURS CATEGORY [--notes NOTES]
```

- `DATE` — Date in YYYY-MM-DD format
- `TITLE` — Course/activity title
- `PROVIDER` — Provider/organization name
- `HOURS` — Credit hours (decimal allowed, e.g., 1.5)
- `CATEGORY` — Category (e.g., clinical, pharmacology, ethics, leadership)
- `--notes` — Optional notes

### `list` — List Entries

```bash
nurse-ce-tracker list [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--verbose]
```

### `totals` — Show Totals

```bash
nurse-ce-tracker totals [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--by-category]
```

### `license` — Manage License Info

```bash
# View current license
nurse-ce-tracker license

# Set license info
nurse-ce-tracker license --set --number RN123456 --state IN --renewal-date 2026-12-31 [--cycle 2] [--required 30]
```

### `renewal` — Renewal Countdown

```bash
nurse-ce-tracker renewal
```

Shows days until renewal, hours earned this cycle, remaining hours, and required daily rate.

### `export` — Export to CSV

```bash
nurse-ce-tracker export OUTPUT.csv [--start YYYY-MM-DD] [--end YYYY-MM-DD]
```

CSV columns: `id`, `date`, `title`, `provider`, `hours`, `category`, `notes`

### `remove` — Remove Entry

```bash
nurse-ce-tracker remove ENTRY_ID
```

## Data Storage

All data is stored locally in `~/.nurse-ce-tracker/`:
- `ce_entries.json` — CE entries
- `license_info.json` — License information

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=nurse_ce_tracker
```

## License

MIT License — Copyright (c) 2026 Asdale Dynamics, LLC

See [LICENSE](LICENSE) for full terms.

## Credits

Built by **Asdale Dynamics, LLC** — Beginner-friendly AI education, books, guides, and practical tools.

- Founder: Dylan Asdale (RN, AI author)
- Book: *The Massive AI Manual*
- Hub: [dylanasdale.github.io](https://dylanasdale.github.io)

---

*Education only. Not medical advice. Not legal advice.*