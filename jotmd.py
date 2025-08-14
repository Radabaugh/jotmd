#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

# ------------------------ Helpers ------------------------

DATE_HEADER_FMT = "%m/%d/%Y"  # e.g., 08/14/2025


def parse_date_string(s: str) -> datetime:
    s = s.strip()
    # Try common forms: YYYY-MM-DD, MM/DD/YYYY, MMDDYYYY
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m%d%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(
        f"Invalid date '{s}'. Use YYYY-MM-DD, MM/DD/YYYY, or MMDDYYYY."
    )


def is_ticket(tag: str) -> bool:
    # e.g., DT-1234, ABCD-12
    return bool(re.fullmatch(r"[A-Z]{2,}-\d+", tag))


@dataclass
class RenderedLines:
    lines: List[str]


def render_note_lines(message: str, tags: Iterable[str]) -> RenderedLines:
    """Render one or more markdown bullet lines for a note.

    Rules:
      - If no tags: produce a single bullet with the message.
      - For non-ticket tags (e.g., names): produce "* NAME: message" (one per tag).
      - For ticket-looking tags (ABC-123): produce "* ABC-123" then an indented
        sub-bullet with the message.
    """
    tags = [t.strip() for t in tags if t and t.strip()]
    lines: List[str] = []

    if not tags:
        lines.append(f"* {message}".rstrip())
        return RenderedLines(lines)

    # Person/topic lines first (alphabetical for tidy grouping), then tickets
    person_like = sorted([t for t in tags if not is_ticket(t)])
    tickets = sorted([t for t in tags if is_ticket(t)])

    for t in person_like:
        lines.append(f"* {t}: {message}".rstrip())

    for t in tickets:
        lines.append(f"* {t}")
        lines.append(f"    * {message}".rstrip())

    return RenderedLines(lines)


# --------------------- File Operations ---------------------

HEADER_RE = re.compile(r"^#\s+(\d{2}/\d{2}/\d{4})\s*$", re.MULTILINE)


def ensure_year_file(notes_dir: Path, dt: datetime) -> Path:
    notes_dir.mkdir(parents=True, exist_ok=True)
    path = notes_dir / f"{dt.year}.md"
    if not path.exists():
        # Create an empty file (no top-level title to keep it grep-friendly)
        path.touch()
    return path


def ensure_date_header(path: Path, dt: datetime) -> None:
    date_header = dt.strftime(DATE_HEADER_FMT)
    content = path.read_text(encoding="utf-8") if path.exists() else ""

    # If header already present anywhere, we're good
    if re.search(rf"^#\s+{date_header}\s*$", content, re.MULTILINE):
        return

    # Otherwise, append a fresh header at EOF
    with path.open("a", encoding="utf-8") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        # Separate from previous day with a blank line, then the header and another blank line
        if content:
            f.write("\n")
        f.write(f"# {date_header}\n\n")


def append_lines_under_today(path: Path, dt: datetime, lines: Iterable[str]) -> None:
    # We append at EOF, assuming the last header is today's if present; otherwise
    # ensure_date_header already appended it. This keeps the file chronological
    # without needing to insert into the middle of the file.
    with path.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


# ------------------------- CLI -------------------------


def cmd_add(args: argparse.Namespace) -> None:
    dt = parse_date_string(args.date) if args.date else datetime.now()

    default_notes_dir = Path.cwd() / "notes"
    notes_dir = (
        Path(args.notes_dir).expanduser().resolve()
        if args.notes_dir
        else default_notes_dir
    )

    year_file = ensure_year_file(notes_dir, dt)
    ensure_date_header(year_file, dt)

    rendered = render_note_lines(args.message.strip(), args.tag or [])
    append_lines_under_today(year_file, dt, rendered.lines)

    print(f"Appended {len(rendered.lines)} line(s) to {year_file}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jot",
        description="Append date-scoped markdown notes into <YEAR>.md files.",
    )
    p.add_argument("message", help="The note message text")
    p.add_argument(
        "-t",
        "--tag",
        action="append",
        help=(
            "Tag(s) to prefix or group the note by. Non-ticket tags (e.g., CHRIS) "
            "render as '* CHRIS: message'. Ticket-like tags (e.g., DT-1234) render as '\n* DT-1234\n    * message'. "
            "Use multiple -t/--tag flags for multiple tags."
        ),
    )
    p.add_argument(
        "-d",
        "--date",
        help="Backdate in YYYY-MM-DD, MM/DD/YYYY, or MMDDYYYY. Default: today.",
    )
    p.add_argument(
        "-n",
        "--notes-dir",
        default="notes",
        help="Directory where <YEAR>.md lives (default: ./notes).",
    )
    return p


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    cmd_add(args)


if __name__ == "__main__":
    main()
