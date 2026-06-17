# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
