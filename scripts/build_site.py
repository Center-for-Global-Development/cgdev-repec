#!/usr/bin/env python3
"""Build the GitHub Pages site for the RePEc archive.

Copies the RePEC/ tree into _site/ unchanged and generates an index.html
in every directory. RePEc's harvesters discover files by crawling HTML
directory listings (the old Apache host had `Options +Indexes`), so these
generated pages are what keeps the archive harvestable.

File bytes are never modified: .rdf files are copied verbatim.
"""

import html
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "RePEC"
OUT = ROOT / "_site"

PAGE = """<!DOCTYPE html>
<html>
<head><title>Index of {path}</title></head>
<body>
<h1>Index of {path}</h1>
<hr>
<pre>
{rows}
</pre>
<hr>
</body>
</html>
"""


def listing_rows(directory: Path, web_path: str) -> str:
    rows = []
    if web_path != "/":
        rows.append('<a href="../">../</a>')
    entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name))
    for entry in entries:
        if entry.name == "index.html" or entry.name.startswith("."):
            continue
        name = entry.name + ("/" if entry.is_dir() else "")
        size = "-" if entry.is_dir() else str(entry.stat().st_size)
        link = f'<a href="{html.escape(name, quote=True)}">{html.escape(name)}</a>'
        rows.append(f"{link}{' ' * max(1, 60 - len(name))}{size:>10}")
    return "\n".join(rows)


def write_indexes(directory: Path, web_path: str) -> None:
    page = PAGE.format(path=html.escape(web_path), rows=listing_rows(directory, web_path))
    (directory / "index.html").write_text(page, encoding="utf-8")
    for child in directory.iterdir():
        if child.is_dir():
            write_indexes(child, f"{web_path}{child.name}/")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC, OUT / "RePEC")

    # Pages served via a workflow artifact bypass Jekyll, but .nojekyll is
    # harmless insurance if the deploy method ever changes.
    (OUT / ".nojekyll").touch()

    write_indexes(OUT, "/")
    total = sum(1 for p in (OUT / "RePEC").rglob("*") if p.is_file())
    print(f"Built _site/ with {total} archive files")


if __name__ == "__main__":
    main()
