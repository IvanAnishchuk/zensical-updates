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
