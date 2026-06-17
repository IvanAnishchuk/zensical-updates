# Review guidelines for zensical-updates

Guidance for automated code review (OpenAI Codex and other agent reviewers).
Codex applies the nearest `AGENTS.md`, which points here; the full project
conventions live in [`AGENTS.md`](AGENTS.md). This file is the shared review
focus, mirrored by `.github/copilot-instructions.md`, `.coderabbit.yaml`, and
`.gemini/styleguide.md` so every reviewer weighs the same things.

zensical-updates generates a dated Updates (blog) section for
[zensical](https://zensical.org) sites as plain Markdown plus an RSS feed,
running as a CLI pre-build step (`zensical-updates build` before `zensical build`).

**When asked to review, only review.** Report findings as comments or a linked
issue. Do not commit, push, or apply fixes on the author's behalf.

## What to focus reviews on

- **URL base-path correctness (P0).** `urls.py` emits site-absolute paths that
  zensical does not validate, so they must be exactly right. Every generated
  link carries the site base path; a missing base path 404s on project Pages
  (the regression fixed in 0.1.2). Scrutinize any change to URL construction.
- **Feed determinism and standards-compliance (P0).** The RSS 2.0 feed is built
  with feedgen and is deterministic: every date comes from post dates, so no
  wall-clock value leaks in. Flag any new `datetime.now()` or `date.today()`
  reaching feed or page output.
- **CLI pre-build contract (P1).** Generated artifacts stay separable from
  hand-written prose; the tool never edits a writer's Markdown in place.
- **Public API discipline (P1).** The supported surface is exactly `__all__` in
  `__init__.py`. Treat changes to it as API changes (semver + CHANGELOG). The
  version lives in both `pyproject.toml` and `__init__.py`; a bump to one
  without the other is a bug.
- **Missing tests or changelog entry (P1).** The decisive test runs `zensical
  build --strict` over a fixture and asserts every generated link resolves.
  User-visible changes need a `CHANGELOG.md` entry under `[Unreleased]`.

## Quality bar (do not weaken in suggestions)

- `ruff`, `mypy --strict`, `ty`, and `basedpyright` pass with zero errors and
  zero warnings. Never suggest a blanket `# type: ignore`, `# noqa`, or `|| true`
  to silence a real finding. A `# noqa` must name its rule and say why.
- `pytest` runs with branch coverage; the floor is 80% (actual ~99%). Hold
  coverage by structuring testable code, not by adding `pragma: no cover`.

## Intentional choices (do not flag these as bugs)

- Every module opens with `from __future__ import annotations`. Type-only
  imports sit under `if TYPE_CHECKING:` because the flake8-type-checking (TCH)
  ruff rules are on, so that guarding is required.
- Imports go at the top of the file. The one deliberate function-scoped import
  is `from feedgen.feed import FeedGenerator` in `feed.py`.
- `feed.py` reuses zensical's internal render API behind a `FeedError` guard, so
  the broad `except Exception` that wraps and re-raises is intentional. It names
  the supported range `zensical >=0.0.45,<0.1.0`.
- v1 carries the full post HTML in the RSS `<description>` as CDATA. The
  `content:encoded` summary/full split is a tracked follow-up (board item
  "[zu] Feed content:encoded"), so do not re-flag full HTML in `<description>`.

## Project context

Work is tracked on a shared board where item and PR titles carry a `[zu]`
prefix for this repo. A bare `#NN` reference may point at another repo on that
board, so read cross-references with that in mind.
