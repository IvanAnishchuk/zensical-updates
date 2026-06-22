# zensical-updates

Generate a dated "Updates" (blog) section for [zensical](https://zensical.org)
sites as plain Markdown. zensical ships no blog plugin, so this CLI runs as a
pre-build step. It reads your post files and writes an index listing, per-year
archives, and tag and category pages that zensical then builds.

## How it works

Writers keep posts in a source directory (default `updates/`), one Markdown file
per post. Each post carries a `date` and optional `categories`/`tags` in
block-list front matter:

```markdown
---
date: 2026-06-11
categories:
  - weekly-update
tags:
  - epf
---

# Hello world

The first paragraph becomes the listing excerpt.
```

`zensical-updates build` copies each post to `docs/<base>/<slug>.md` and writes
the generated section around it (the index, `archive/`, `tags/`, `categories/`).
A post at `docs/updates/hello.md` renders at `/updates/hello/`, and every
generated link points there. Run it before zensical:

```bash
zensical-updates build              # writes docs/updates/
zensical build --clean --strict
```

The generated `docs/<base>/` tree is build output. Gitignore it. The source tree
stays under version control, and the generator never edits it.

## Install

```bash
uv add zensical-updates
# or: pip install zensical-updates
```

## Configure

Settings live in `zensical.toml` under `[project.extra.zensical_updates]`, a
namespace zensical ignores:

```toml
[project.extra.zensical_updates]
base = "updates"        # section dir under docs/ and the URL base
source = "updates"      # where your post files live, outside docs/
emit_tags = true
emit_categories = true
emit_archive = true
```

Every key is optional. The defaults above apply when the table is absent.

## Feed

With `site_url` set in `zensical.toml`, the build writes an RSS 2.0 feed to
`docs/<base>/feed.xml`, served at `<site_url>/<base>/feed.xml` (for the default
section, `/updates/feed.xml`). Each item carries a short summary in
`<description>` (the post excerpt) and the full post HTML in `<content:encoded>`,
rendered by zensical so it matches the site, with every link rewritten to a
fully-qualified URL for readers off-site. A post with no excerpt keeps the full
HTML in `<description>`. Without `site_url` the build prints a warning and skips
the feed, since an off-site feed needs absolute links.

Two config keys tune it:

```toml
[project.extra.zensical_updates]
emit_feed = true   # generate feed.xml (default)
feed_limit = 0     # max items, 0 means no cap (default)
```

## Sitemap

With `site_url` set, the build writes a sitemap to `docs/<base>/sitemap.xml`,
served at `<site_url>/<base>/sitemap.xml` (for the default section,
`/updates/sitemap.xml`). It lists every page the build generates: the section
index, each post, and whichever taxonomy and archive pages you enable. zensical
writes its own sitemap for the pages in `nav` only, so the generated section is
otherwise missing from any sitemap, and a crawler never reaches the posts. The
locations are fully-qualified, so the sitemap needs `site_url` for the reason the
feed does, and the build prints a warning and skips it without one.

```toml
[project.extra.zensical_updates]
emit_sitemap = true   # generate sitemap.xml (default)
```

## Taxonomy pages

The Tags and Categories index pages list their terms as a frequency-ordered
cloud: busiest term first, with each term's post count. The main Updates index
and each index page carry a `Browse:` line linking the Tags, Categories, and
Archive index pages, so a reader can move between them. Only the indexes you
enable (`emit_tags`, `emit_categories`, `emit_archive`) appear in the links.

## CLI

```bash
zensical-updates build    # generate the section into docs/<base>/
zensical-updates clean    # remove the generated output
zensical-updates --help
```

## Development

```bash
git clone https://github.com/IvanAnishchuk/zensical-updates.git
cd zensical-updates
uv sync

uv run pytest                       # tests + coverage (includes the zensical build)
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy
uv run pre-commit run --all-files
```

## License

CC0-1.0. This is an original implementation inspired by the concept of
`knu2xs/zensical-blog`, written from this project's own analysis of how zensical
behaves.
