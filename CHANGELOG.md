# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
