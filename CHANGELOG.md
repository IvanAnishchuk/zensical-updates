# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- A sitemap for the generated section. With `site_url` set, the build writes
  `docs/<base>/sitemap.xml` listing every generated page (the section index, each
  post, and the taxonomy and archive pages you enable), so the content is in a
  sitemap a crawler can read. zensical's own sitemap covers its `nav` pages only.
  The new `emit_sitemap` config key (default `true`) toggles it, and the CLI warns
  when it is skipped for a missing `site_url`, the same as the feed.

### Changed

- `uv.lock` is now the single source of truth for dependencies.
  `requirements.txt` / `requirements-dev.txt` are no longer committed; they are
  generated on demand. `scripts/regen_requirements.py` gained a `--stdout`
  (pipe one set) and `--output-dir DIR` (write both into a directory) mode, and
  `scripts/audit.py` now exports into a temporary directory for pip-audit and
  SBOM rather than reading committed files. The release SBOM step exports
  prod-only requirements through the helper. A Dependabot bump no longer needs
  a committed-requirements regen to pass audit.
- Merge policy: only merge commits are allowed on this repo now.
  `.github/settings.yml` sets `allow_squash_merge` and `allow_rebase_merge` to
  `false` so history is preserved.

- Dropped `from __future__ import annotations` and the `if TYPE_CHECKING:`
  guards across the codebase, and retired the flake8-type-checking (TCH) ruff
  rule. The project targets Python 3.14+, where PEP 649 defers annotation
  evaluation, so the future import and the type-only-import guarding are no
  longer needed. Internal only; no API or output change.

### Fixed

- Release pipeline: the `pypi` deployment environment now matches the release
  tag. Its `v*.*.*` policy was typed as a branch, which never matches a `vX.Y.Z`
  tag, so the publish was blocked. The policy is now tag-typed, and a required
  reviewer gates the PyPI publish. `testpypi` gained a matching tag policy so
  pre-release tags can deploy.
- Branch protection on `main` now applies. The `settings.yml` protection block
  omitted the `restrictions` key, and the Settings app skips the whole block
  unless every top-level protection key is present (set to `null` when unused).
  Added `restrictions: null`, so the declared review and status-check rules take
  effect.

### Removed

- Committed `requirements.txt` and `requirements-dev.txt`, and the
  `regen-requirements` pre-commit hook that kept them in sync. Generated on
  demand from `uv.lock` instead.

### Security

- Bump `msgpack` to 1.2.1 (GHSA-6v7p-g79w-8964). The 1.2.0 streaming `Unpacker`
  could crash with a SEGV when reused after an error, a DoS risk on untrusted
  input, though it is a dev-only transitive dependency (via `cachecontrol`) so
  the published package never shipped it. The pre-push `pip-audit` gate flags it
  on every push.

## [0.1.5] - 2026-06-18

### Added

- RSS feed items now split the body: the post excerpt goes in `<description>` and
  the full rendered HTML goes in `<content:encoded>`. A post with no excerpt keeps
  the full HTML in `<description>`. feedgen emits both elements natively, so no
  custom extension is needed.
- Code-review bot configuration so automated reviewers honor the project's house
  style and skip generated files: `.coderabbit.yaml` (CodeRabbit), `.gemini/`
  (Gemini Code Assist), `code_review.md` with an `AGENTS.md` pointer (Codex), and
  an expanded `.github/copilot-instructions.md` (Copilot). Each encodes the same
  review focus (URL base-path correctness, feed determinism, public-API
  discipline) and the intentional-choice list, and defers to `AGENTS.md`.
- Tags and Categories index pages now render a frequency-ordered cloud (busiest
  term first, with post counts). The main Updates index and each taxonomy/archive
  index carry a `Browse:` nav linking the enabled index pages.

### Changed

- Repository merge policy in `.github/settings.yml`: merge commits are the
  preferred merge method. Squash merging is disabled and `required_linear_history`
  is off so merge commits are allowed on `main`.

## [0.1.4] - 2026-06-17

### Removed

- Dropped support for Python 3.11, 3.12, and 3.13. The package now requires
  Python 3.14 or newer. This is a breaking change for consumers still on an
  older interpreter.

## [0.1.3] - 2026-06-17

### Added

- RSS 2.0 feed at `docs/<base>/feed.xml`, generated when `site_url` is set. Each
  item carries the full post HTML, rendered by zensical so it matches the site,
  with links rewritten to fully-qualified URLs for off-site readers. Two config
  keys control it: `emit_feed` (default true) and `feed_limit` (default 0, no cap).

## [0.1.2] - 2026-06-17

### Fixed

- Carry the site sub-path in every emitted link. On a project Pages site served
  under a base path (e.g. `/eth-protocol-fellowship/`), generated post, tag,
  category, and archive links dropped the prefix and 404'd. The generator now
  reads `[project] site_url` and prepends its path, so a link resolves to
  `/eth-protocol-fellowship/updates/<slug>/`. Root-served sites are unchanged
  (no `site_url` path means no prefix and no extra slash). The on-disk output
  dir stays `docs/<base>/`, so only the emitted URLs gain the prefix.

## [0.1.1] - 2026-06-17

### Fixed

- Drop the empty gitleaks allowlist that newer gitleaks (v8.30) rejects with
  "allowlists must contain at least one check", which failed the pre-commit CI
  job. The standalone gitleaks action tolerated it, which masked the bug.

### Changed

- Source `__version__` from the installed package metadata instead of a
  hard-coded string, so a release bumps only `pyproject.toml`; the tests no
  longer pin the version number.
- Bump tooling: hatchling >=1.30.1, mkdocs-typer2[zensical] >=0.4.0, and the
  uv-pre-commit hook to 0.11.21 (dependabot).

## [0.1.0] - 2026-06-17

### Added

- Initial project scaffold.
- Post discovery and the content model: YAML front-matter parsing (block-list
  aware), post loading (slug from file stem, date coercion, taxonomies,
  excerpt), newest-first discovery, and grouping by category, tag, and year.
- Markdown emitters for the index listing, archive landing and per-year pages,
  and tag/category pages and their indexes. Output is zensical-safe: every link
  is a site-absolute directory URL and there are no bare reference brackets.
- A `build`/`clean` CLI and a `zensical.toml` config loader (the
  `[project.extra.zensical_updates]` table). `build` discovers source posts,
  copies them into `docs/<base>/`, and writes the generated pages; `clean`
  removes that output. An invalid post (e.g. missing date) fails the build.
- An end-to-end integration test: generate a fixture site, run
  `zensical build --clean --strict`, and assert every generated post,
  taxonomy, and archive link resolves to a rendered page. This guards the two
  silent failures (wrong post URLs and front-matter link reads).
- Documentation: README and a usage guide covering how to write posts,
  configure the generator, and run the build.
