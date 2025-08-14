# jotmd

A tiny CLI to jot structured markdown notes by **date** into per-year files (`YYYY.md`).

- Date headers: `# MMDDYYYY` (e.g., `# 08/14/2025`)
- Default notes folder: `./notes/`
- Non-ticket tags (e.g., `CHRIS`) render as `* CHRIS: message`
- Ticket-like tags (e.g., `DT-1234`) render as:
  ```
  * DT-1234
      * message
  ```
- New year? It auto-creates the next `YYYY.md`.

## Requirements

- Python **3.9+**

## Install

### Recommended (isolated CLI via pipx)

```bash
# macOS (Homebrew)
brew install pipx
pipx ensurepath

# from repo root
pipx install .
```

## Quick start

```bash
# add a freeform note under today's date
jotmd "Investigated Kafka consumer lag"

# tag a person
jotmd "Wants me to update a ticket" -t/--tag CHRIS

# tag a ticket
jotmd "Learned about Apache Walrus" -t/--tag DT-9999

# multiple tags (one person line, one ticket block)
jotmd "Prepared retro notes" -t/--tag CHRIS -t/--tag DT-1234

# backdate (YYYY-MM-DD, MM/DD/YYYY, or MMDDYYYY)
jotmd "Caught up on planning" -d/--date 2025-08-13 -t/--tag CHRIS
```

This writes to `./notes/2025.md` (or `./notes/2026.md` once the year rolls over).
If the date section doesn’t exist yet, it’s created: `# 08/13/2025`, etc.

## CLI reference

```bash
jotmd "MESSAGE" [-t/--tag TAG ...] [-d/--date DATE] [-n/--notes-dir PATH]
```
- `--tag TAG`
  - Non-ticket (e.g., `CHRIS`) → `* CHRIS: MESSAGE`
  - Ticket pattern `[A-Z]{2,}-\d+` (e.g., `DT-1234`) → as a parent bullet with an indented message
- `--date DATE` Backdate using `YYYY-MM-DD`, `MM/DD/YYYY`, or `MMDDYYYY`. Default: today.
- `--notes-dir PATH` Where `YYYY.md` lives. Default: `./notes`.

## Output examples

**People tag**

```
# 08/14/2025
* CHRIS: Wants me to set up a meeting with UCS Team for Thursday
```

**Ticket tag**

```
# 08/14/2025
* DT-YYYY
    * Learned about Apache Walrus
```

## Uninstall

```bash
pipx uninstall jotmd    # if installed via pipx
# or remove your venv if installed editable
```

## License

MIT
