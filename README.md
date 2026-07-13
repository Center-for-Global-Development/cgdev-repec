# CGD RePEc Archive

This repository is the source of truth for the Center for Global Development's
[RePEc](https://repec.org) archive (`RePEc:cgd`). It replaces the old shared-hosting
server at `cgdev-repec.org`, which contractors updated over FTP.

On every push to `main`, a GitHub Action publishes the `RePEC/` tree to GitHub
Pages, generating the HTML directory listings that RePEc's harvesters crawl to
discover records. RePEc fetches the archive at:

    http://cgdev-repec.org/RePEC/cgd/

(Note the unusual capitalization of `RePEC` in the path — it is what's registered
with RePEc and must not change. Paths are case-sensitive.)

## Layout

    RePEC/cgd/
      cgdarch.rdf     archive-level metadata (registered with RePEc; rarely changes)
      cgdseri.rdf     series definitions (Working Papers + Policy Papers)
      wpaper/wpN.rdf  one record per Working Paper N
      ppaper/ppN.rdf  one record per Policy Paper N

Each `.rdf` file is a plain-text [ReDIF](https://ideas.repec.org/t/papertemplate.html)
template describing one paper. The PDFs themselves are hosted on www.cgdev.org;
this archive holds only metadata.

## Adding a new paper (no git knowledge needed)

1. Prepare the record as a text file, e.g. `wp746.rdf` for Working Paper 746.
   Copy a recent file in `RePEC/cgd/wpaper/` as a starting template. The
   `Handle:` line must match the filename (`RePEc:cgd:wpaper:746`).
2. On GitHub, navigate to `RePEC/cgd/wpaper/` (or `ppaper/`), then
   **Add file → Upload files**, drag the file in, and commit.
3. That's it. A check validates the record (a red ✗ on the commit means it has
   a problem — click through for details), and the site redeploys automatically
   within a couple of minutes. RePEc harvests the archive roughly daily, and new
   records typically appear on IDEAS/EconPapers within a day or two.

To fix an existing record, open the file on GitHub and use the pencil (edit)
icon instead.

## Maintenance notes

- **Do not "clean up" old records' line endings or encoding.** Many legacy
  files use CRLF or CR-only endings and Windows-1252 characters; RePEc parses
  them fine, and `.gitattributes` tells git to leave all bytes alone. New files
  should be plain UTF-8.
- `scripts/build_site.py` builds the deployed site into `_site/` (run locally to
  preview). The generated `index.html` listings are required — RePEc's crawler
  discovers files through them, like Apache's `Options +Indexes` on the old host.
- `scripts/validate_redif.py FILE...` checks records the same way CI does.
- The old server's full backup is kept locally (git-ignored) at
  `repec backup july 13 2026/`; everything RePEc-relevant was extracted into
  `RePEC/`.

## DNS cutover

GitHub Pages must serve `cgdev-repec.org` before the old hosting is cancelled:

1. Repo **Settings → Pages**: set custom domain `cgdev-repec.org`.
2. At the DNS provider, point the apex at GitHub Pages
   (A records `185.199.108.153`, `.109.`, `.110.`, `.111.153`, or the
   provider's ALIAS/CNAME-flattening to `center-for-global-development.github.io`).
3. Verify `http://cgdev-repec.org/RePEC/cgd/` shows the directory listing and
   that individual `.rdf` files download byte-for-byte.
4. After a harvest cycle, confirm the archive still shows as reachable on
   [IDEAS' archive page for cgd](https://ideas.repec.org/s/cgd/wpaper.html).
