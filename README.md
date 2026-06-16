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

Not on PyPI yet. Pin from git:

```bash
uv add "zensical-updates @ git+https://github.com/IvanAnishchuk/zensical-updates"
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
