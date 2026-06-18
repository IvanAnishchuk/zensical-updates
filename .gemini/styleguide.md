# Review style guide for zensical-updates

zensical-updates generates a dated Updates (blog) section for [zensical](https://zensical.org)
sites as plain Markdown, plus an RSS feed. It runs as a CLI pre-build step:
`zensical-updates build` before `zensical build`. It is an importable Python
library (`src/zensical_updates/`, Python 3.14+, `py.typed`, CC0-1.0) with a thin
typer + rich maintenance CLI.

The full conventions live in [`AGENTS.md`](../AGENTS.md). This guide tells Gemini
what to weigh in a review and what is deliberate.

## What to focus reviews on

- **The CLI pre-build contract.** The generator writes Markdown that zensical
  then builds. Generated artifacts stay separable from hand-written prose, and
  the tool never edits a writer's Markdown in place.
- **URL base-path correctness.** `urls.py` emits site-absolute paths. zensical
  does not validate them, so they must be exactly right. Every generated link
  carries the site base path; a missing base path makes project-Pages links 404
  (the regression fixed in 0.1.2). Scrutinize any change to URL construction.
- **Feed standards-compliance and determinism.** The RSS feed is RSS 2.0 via
  feedgen. It is deterministic: every date comes from post dates, so no
  wall-clock value leaks in. Flag any new `datetime.now()` or `date.today()`
  reaching feed or page output.
- **Public API discipline.** The supported surface is exactly what
  `__init__.py` re-exports in `__all__`. Treat `__all__` changes as API changes
  (semver plus a CHANGELOG entry). The version string lives in both
  `pyproject.toml` and `src/zensical_updates/__init__.py`; a bump to one without
  the other is a bug.

## Quality bar (do not weaken in suggestions)

- `ruff`, `mypy --strict`, `ty`, and `basedpyright` all pass with zero errors
  and zero warnings. Never suggest a blanket `# type: ignore`, `# noqa`, or
  `|| true` to silence a real finding. A `# noqa` must name its rule and say why.
- `pytest` runs with branch coverage; the floor is 80% and actual sits near
  99%. Hold coverage by structuring testable code, not by adding `pragma: no
  cover`.
- The decisive test runs `zensical build --strict` over a fixture site and
  asserts every generated link resolves. Changes that weaken link-resolution or
  determinism checks deserve a flag, not a relaxed expectation.

## Intentional choices (do not flag these as bugs)

- Modules do not use `from __future__ import annotations`. The project targets
  Python 3.14+, where PEP 649 defers annotation evaluation, so the future import
  is unnecessary. All imports, including type-only ones, sit at the top of the
  file; there are no `if TYPE_CHECKING:` guards and the TCH ruff rule is off. Do
  not suggest re-adding the future import or moving imports under `TYPE_CHECKING`.
- Declare any type alias with the `type X = ...` statement (PEP 695), not
  `X: TypeAlias = ...`.
- Imports go at the top of the file. The one deliberate function-scoped import
  is `from feedgen.feed import FeedGenerator` in `feed.py`.
- `feed.py` reuses zensical's internal render API behind a `FeedError` guard.
  The broad `except Exception` that wraps and re-raises (`raise FeedError(...)
  from exc`) is intentional, since any internal-API move should surface as one
  clear error naming the supported range `zensical >=0.0.45,<0.1.0`.
- The feed puts the post excerpt in the RSS `<description>` and the full post
  HTML in `<content:encoded>` as CDATA. A post with no excerpt keeps the full
  HTML in `<description>`, so do not flag that fallback as a bug.

## Project context

Work is tracked on a shared board where item and PR titles carry a `[zu]`
prefix for this repo. A bare `#NN` reference in a commit may point at another
repo on that board, so read cross-references with that in mind.
