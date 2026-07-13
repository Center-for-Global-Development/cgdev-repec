#!/usr/bin/env python3
"""Validate ReDIF paper templates (.rdf files) in the archive.

Usage:
    validate_redif.py FILE [FILE ...]

Intended to run in CI against files added or changed in a push/PR, so that
a malformed record fails visibly here instead of silently never appearing
on IDEAS/EconPapers. Legacy files are grandfathered by only validating
what changed.

Checks are limited to what RePEc's harvester actually needs; stylistic
issues are warnings only. File bytes are read permissively (UTF-8, then
Windows-1252) because the archive predates any consistent encoding.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# RePEC/cgd/wpaper/wp123.rdf -> series "wpaper", prefix "wp", number "123"
SERIES = {"wpaper": "wp", "ppaper": "pp"}
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def read_fields(path: Path):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")
    text = text.lstrip("\ufeff")  # a few legacy files carry a UTF-8 BOM
    fields = []
    for line in re.split(r"\r\n|\r|\n", text):
        m = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s?(.*)$", line)
        if m:
            fields.append((m.group(1).lower(), m.group(2).strip()))
        elif fields and line.strip():
            # ReDIF wraps long values onto continuation lines
            key, value = fields[-1]
            fields[-1] = (key, f"{value} {line.strip()}".strip())
    return fields


def validate(path: Path):
    errors, warnings = [], []
    rel = path.relative_to(REPO) if path.is_absolute() else path

    parts = rel.parts
    if len(parts) != 4 or parts[0] != "RePEC" or parts[1] != "cgd":
        errors.append("file is not under RePEC/cgd/<series>/ — RePEc will not see it")
        return errors, warnings
    series = parts[2]
    if series not in SERIES:
        errors.append(f"unknown series directory {series!r} (expected wpaper or ppaper)")
        return errors, warnings

    m = re.fullmatch(rf"{SERIES[series]}(\d+[a-z]?)\.rdf", path.name)
    if not m:
        errors.append(f"filename must look like {SERIES[series]}<number>.rdf")
        return errors, warnings
    number = m.group(1)

    fields = read_fields(path)
    names = [k for k, _ in fields]

    def get(key):
        return next((v for k, v in fields if k == key), None)

    template = get("template-type")
    if template != "ReDIF-Paper 1.0":
        errors.append(f"Template-Type must be 'ReDIF-Paper 1.0', got {template!r}")

    expected_handle = f"RePEc:cgd:{series}:{number}"
    handle = get("handle")
    if handle != expected_handle:
        errors.append(f"Handle must be {expected_handle!r} to match the filename, got {handle!r}")

    if not get("title"):
        errors.append("missing Title")
    if "author-name" not in names:
        errors.append("missing Author-Name")

    file_url = get("file-url")
    if not file_url:
        warnings.append("no File-URL — record will have no full-text link")
    elif not re.match(r"^https?://", file_url):
        errors.append(f"File-URL is not an http(s) URL: {file_url!r}")

    creation = get("creation-date")
    if not creation:
        warnings.append("no Creation-Date")
    elif not DATE_RE.match(creation):
        errors.append(f"Creation-Date must be YYYY[-MM[-DD]], got {creation!r}")

    paper_number = get("number")
    if paper_number and paper_number != number:
        warnings.append(f"Number field is {paper_number!r} but filename says {number}")

    return errors, warnings


def main(argv):
    if not argv:
        print("usage: validate_redif.py FILE [FILE ...]")
        return 0
    failed = False
    for arg in argv:
        path = Path(arg)
        if not path.exists():  # deleted in this change set
            continue
        if path.suffix != ".rdf" or path.name in ("cgdarch.rdf", "cgdseri.rdf"):
            continue
        errors, warnings = validate(path.resolve())
        for w in warnings:
            print(f"WARNING {arg}: {w}")
        for e in errors:
            print(f"ERROR   {arg}: {e}")
            failed = True
        if not errors and not warnings:
            print(f"OK      {arg}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
