# zensical-updates

Generate a dated "Updates" (blog) section for zensical sites as plain Markdown.
zensical has no blog plugin, so this CLI runs as a pre-build step that writes an
index listing, per-year archives, and tag and category pages.

## Install

Not on PyPI yet. Pin from git:

```bash
uv add "zensical-updates @ git+https://github.com/IvanAnishchuk/zensical-updates"
```

## Quickstart

```bash
zensical-updates build              # writes docs/<base>/
zensical build --clean --strict
```

## Documentation

- [Usage](usage.md) — write posts, configure, and run the build.
- [CLI](cli.md) — the `build`/`clean` commands.
- [API Reference](api.md) — generated from docstrings.
- [Changelog](changelog.md) — version history.
