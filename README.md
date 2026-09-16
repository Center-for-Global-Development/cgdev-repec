# CGD RePEc Archive

This repository is the source of truth for the Center for Global Development's
[RePEc](https://repec.org) archive (`RePEc:cgd`). It is live: RePEc harvests the
archive from

    http://cgdev-repec.org/RePEC/cgd/

which is served by GitHub Pages from this repo (DNS is at Cloudflare and
proxies to Pages; `www.` and `https://` both resolve to the same content).
The old shared-hosting server that contractors updated over FTP has been
retired; its final state is kept locally as a git-ignored backup.

Note the unusual capitalization of `RePEC` in the path. It is what's registered
with RePEc and must not change. Paths are case-sensitive.

## How it works

1. A commit lands on `main`.
2. `validate.yml` runs `scripts/validate_redif.py` on every `.rdf` that changed.
   A red ✗ on the commit means a record has a problem; click through for the
   message.
3. `deploy.yml` runs `scripts/build_site.py`, which copies `RePEC/` verbatim
   into `_site/` and generates an `index.html` directory listing in every
   folder, then publishes `_site/` to GitHub Pages. The listings are required:
   RePEc's crawler discovers files through them, like Apache's
   `Options +Indexes` on the old host.
4. RePEc mirrors the archive roughly nightly. New records usually appear on
   IDEAS and EconPapers within a day or two.

## Layout

    RePEC/cgd/
      cgdarch.rdf     archive-level metadata (registered with RePEc; rarely changes)
      cgdseri.rdf     series definitions (Working Papers + Policy Papers)
      wpaper/wpN.rdf  one record per Working Paper N
      ppaper/ppN.rdf  one record per Policy Paper N
    repec_handles_reference.csv   RePEc author IDs (Short-IDs) for CGD fellows
    scripts/
      validate_redif.py   record checks, same as CI
      build_site.py       builds the Pages site into _site/ (run locally to preview)

Each `.rdf` file is a plain-text [ReDIF](https://ideas.repec.org/t/papertemplate.html)
template describing one paper. The PDFs live on www.cgdev.org; this archive
holds only metadata.

Numbering is contiguous apart from three papers CGD never issued: wp18, pp36
and pp84.

## Adding a new paper

Everything you need is on the paper's PDF cover and inside page, not the
cgdev.org landing page: series and number ("Working Paper 754"), page count,
JEL codes and keywords (when printed), and each author's affiliation. The
landing page's blurb is sometimes a shortened teaser, so take the abstract
from the PDF too.

1. Copy the most recent file in `RePEC/cgd/wpaper/` (or `ppaper/`) and name
   the copy for the new paper, e.g. `wp754.rdf` for Working Paper 754.
2. Fill it in following the conventions below. The `Handle:` line must match
   the filename (`RePEc:cgd:wpaper:754`) and `Number:` must match too.
3. Check it locally if you can:

       python3 scripts/validate_redif.py RePEC/cgd/wpaper/wp754.rdf

4. On GitHub, navigate to `RePEC/cgd/wpaper/` (or `ppaper/`), then
   **Add file → Upload files**, drag the file in, and commit to `main`.

To fix an existing record, open the file on GitHub and use the pencil (edit)
icon instead.

### Record conventions

These were established in the 2026 cleanup and apply to every record in the
archive. The validator errors on the first two and warns on the rest.

- **Author name fields** are `Author-Name`, `Author-Name-First` and
  `Author-Name-Last` only. There is no `Author-Name-Middle` field in ReDIF:
  write "Álvaro S. González" in `Author-Name`, "Álvaro" in First, "González"
  in Last. `Author-X-Name-*` fields are not valid either.
- **File bytes**: UTF-8 with a leading BOM, CRLF line endings, one trailing
  newline. Copying a recent record and editing it preserves this.
- **Two file blocks per paper**, landing page first, then the PDF:

      File-URL: https://www.cgdev.org/publication/<slug>?utm_source=repec&utm_medium=referral&utm_campaign=repec
      File-Format: text/html
      File-URL: https://www.cgdev.org/sites/default/files/<slug>.pdf
      File-Format: application/pdf

  The PDF filename usually matches the landing-page slug but not always;
  copy the real link from the landing page.
- **Title** is the paper's title alone, with no "Working Paper N" suffix.
- **Abstract** is one line, paragraphs joined with a space.
- **Length** is `N pages`; **Creation-Date** is `YYYY-MM-DD` (the cgdev.org
  publication date).
- **Author-Workplace-Name** is `Center for Global Development` for CGD staff
  and fellows; use the affiliation printed in the PDF for everyone else
  (`Consultant` is used for CGD consultants).
- **Author-Person** carries the author's RePEc Short-ID (e.g. `pke79`) when
  one is known. Check `repec_handles_reference.csv` and the author's earlier
  records in this archive; leave the line out otherwise.
- **Classification-JEL** and **Keywords** are comma-separated and included
  whenever the PDF cover prints them. Most policy papers have neither.

A complete record:

    Template-Type: ReDIF-Paper 1.0
    Author-Name: Charles Kenny
    Author-Name-First: Charles
    Author-Name-Last: Kenny
    Author-Workplace-Name: Center for Global Development
    Author-Person: pke79
    Title: Will There Be an African Energy Revolution? That Depends on Who Funds What
    Abstract: The reach of electricity in Africa is rapidly extending, ...
    Length: 16 pages
    Creation-Date: 2026-09-14
    File-URL: https://www.cgdev.org/publication/will-there-be-african-energy-revolution-depends-who-funds-what?utm_source=repec&utm_medium=referral&utm_campaign=repec
    File-Format: text/html
    File-URL: https://www.cgdev.org/sites/default/files/will-there-be-african-energy-revolution-depends-who-funds-what.pdf
    File-Format: application/pdf
    Number: 401
    Handle: RePEc:cgd:ppaper:401

## Checking the live archive

- [EconPapers data check for cgd](https://econpapers.repec.org/check/cgd/):
  nightly template validation and link checking, with per-series error counts
  and the mirroring logs. Template errors clear a day or two after a fix is
  deployed.
- [IDEAS series page](https://ideas.repec.org/s/cgd/wpaper.html) (and
  `ppaper.html`): confirms the archive is being harvested and shows the
  newest records.
- The link checker reports most cgdev.org landing-page URLs as bad. That is
  CGD's web application firewall blocking the `RePEc link checker` user agent,
  not a metadata problem; the PDF links pass. Allowlisting that user agent on
  www.cgdev.org is the outstanding fix.

## Maintenance notes

- `.gitattributes` marks every file `-text` so git never converts line
  endings. RePEc serves the files byte-for-byte, so keep it that way.
- Bulk changes should be scripted and made one concern per commit, with
  `python3 scripts/validate_redif.py RePEC/cgd/*/*.rdf` run before pushing.
  Read files with `utf-8-sig` and write them back with the BOM and CRLF.
- Do not rename or delete records. RePEc treats a handle as permanent; a
  withdrawn paper keeps its file.
- `cgdarch.rdf` and `cgdseri.rdf` are registered with RePEc. Changing the
  `URL:` in the archive template or the series handles requires coordinating
  with RePEc first.
- The old server's full backup is kept locally (git-ignored) at
  `repec backup july 13 2026/`; everything RePEc-relevant was extracted into
  `RePEC/`. Scratch files for cleanup work go in the git-ignored
  `working_directory/`.

## Hosting

GitHub Pages serves the repo at `center-for-global-development.github.io/cgdev-repec`,
which redirects to the custom domain `cgdev-repec.org` (repo
**Settings → Pages**). Cloudflare holds the DNS for `cgdev-repec.org` and
proxies it to Pages. If the archive stops resolving, check those two places
first, then the latest run of `deploy.yml` under **Actions**.
