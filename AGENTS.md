# AGENTS.md — zensical-updates

zensical-updates — Generate a dated Updates (blog) section for zensical sites as plain Markdown

Importable **Python library** (src layout under `src/zensical_updates/`),
Python 3.14+, shipping a `py.typed` marker. A thin
**typer + rich** maintenance CLI rides along for introspection. Guidance for AI
coding agents working in this repo; humans get the same rules via `CLAUDE.md` and
`.github/copilot-instructions.md`.

## Build & run

```bash
uv sync                                              # install deps
uv run pytest                                        # tests + coverage
uv run ruff check --fix src/ tests/                  # lint
uv run ruff format src/ tests/                       # format
uv run mypy
uv run ty check
uv run basedpyright
uv run pre-commit run --all-files                  # full hook suite
uv run python scripts/audit.py                       # supply-chain audit
uv sync --group docs && uv run zensical build --strict  # API docs (CI gate)
uv run zensical-updates info          # maintenance CLI
```

## Review priorities & invariants (this project)

- **The public API is the product.** The supported surface is exactly what
  `zensical_updates/__init__.py` re-exports and lists in `__all__`;
  implementation lives in private modules (`_core.py`, …). Adding to `__all__` is
  what makes a name public — and what marks it as an explicit re-export for the
  type checkers (mypy `strict` implies `no_implicit_reexport`) and for autodoc.
  Treat `__all__` changes as API changes (semver + changelog).
- **Docstrings are documentation.** Public names use **Google-style** docstrings;
  `docs/api.md` autogenerates the API reference from them via `mkdocstrings`, and
  `docs/cli.md` autogenerates the CLI reference via `mkdocs-typer2`. `zensical
  build --strict` is a CI gate — a broken docstring/reference fails the build.
- The maintenance CLI (`zensical_updates.cli:app`) is a convenience,
  not the product; its output goes through `rich.console.Console`, never bare
  `print()` (ruff `T20`). `__main__.py` enables `python -m zensical_updates`.
- Coverage floor is **80%** — a library should be
  well-tested. Raise it as the API stabilizes; do not lower it, and do not add
  hollow tests purely to clear it.
- **Releases publish to PyPI** (`release.yml`): bump the version, update the
  changelog, tag `vX.Y.Z`. Pre-release tags route to TestPyPI.

## Review guidelines

Automated reviewers (Codex, Copilot, CodeRabbit, Gemini) apply these on PRs. The
shared review focus, quality bar, and intentional-choice list live in
[`code_review.md`](code_review.md). The essentials:

- Scrutinize **URL base-path correctness** (`urls.py` paths are unvalidated and
  404 on project Pages if the site base path is missing) and **feed determinism**
  (no `datetime.now()` / `date.today()` may leak into feed or page output).
- Do NOT flag these as bugs: the per-module `from __future__ import annotations`
  and `if TYPE_CHECKING:` guards (the TCH ruff rules are on), the function-scoped
  `from feedgen.feed import FeedGenerator` in `feed.py`, the broad
  `except Exception` wrapped and re-raised as `FeedError`, or the feed item body
  split into a `<description>` excerpt plus full post HTML in `<content:encoded>`
  as CDATA (a post with no excerpt keeps the full HTML in `<description>`).

<!-- universal:begin -->
<!--
  Universal conventions — shared verbatim across all python-project-templates.
  This block is byte-identical in every template's AGENTS.md; edit it in one
  place and propagate, or scripts/check_docs_sync.py will flag the drift.
-->
## Universal conventions

These apply to every project generated from these templates, regardless of type.

### Tooling

- **Package manager: `uv`** — never raw `pip`. Lock with `uv lock`, sync with
  `uv sync --frozen`. Run all tooling through `uv run`.
- **Lint + format: `ruff`** — line length 100, security rules (`S`/`BLE`/`TRY`)
  enabled. When a pylint (`PL`) limit is genuinely too tight, raise the
  threshold in `pyproject.toml`; do not silence the rule with a blanket ignore.
- **Type checking** — all public APIs typed; modern syntax (`list[str]`,
  `str | None`). The configured checkers run via `uv run` (see the build
  commands above for which are enabled in this project).
- **Testing: `pytest`** with branch coverage; the floor lives in
  `pyproject.toml`. Prefer fixtures and in-memory doubles over heavy mocking.
- **No checked-in shell scripts or Makefiles** — operational tooling lives in
  `scripts/*.py`, run via `uv run python scripts/<name>.py`.

### Code style

- **Imports go at the top of the file.** Do not silence ruff `PLC0415`
  (import-outside-top-level) to keep a diff small or to scope a name locally.
  The only acceptable inline imports are: a real circular dependency that
  `if TYPE_CHECKING:` cannot break, a heavy optional dependency that needs lazy
  loading, or deferred filesystem-touching imports inside test helpers.
- **Double quotes**, f-strings over `.format()`/`%`, `pathlib.Path` over
  `os.path`.
- **Every `# noqa` / `# type: ignore` must name the rule and say why.**

### Security & supply chain

- All `subprocess` calls use list args — never `shell=True`.
- Catch the narrowest exception possible; never bare `except:` or an
  unjustified `except Exception:`. Chain with `raise ... from err`.
- Validate URLs before fetching. Never hardcode secrets — use env vars or
  Pydantic Settings; `.env` is local-only and gitignored.
- Releases are signed (sigstore) and ship PEP 740 attestations + an SBOM.

### Workflow

- **Never push to `main`** — always a short-lived branch and a PR.
- **Conventional Commits** (`--strict`): `feat`, `fix`, `chore`, `security`,
  `perf`, `docs`, `test`, `refactor`, `ci`, `build`, `revert`, `style`.
- Run `uv run pre-commit run --all-files` before pushing; all CI checks must
  pass before merge.
- **Solo maintainer:** branch protection requires one approving review you
  cannot give your own PR — merge your reviewed PRs with `gh pr merge --admin`
  (permitted because `enforce_admins: false`).
- **Bump the version in both** `pyproject.toml` and `src/<package>/__init__.py`.
- **Changelog:** every PR adds an entry under `[Unreleased]` in `CHANGELOG.md`
  (Keep a Changelog format) — fixes, CI, and docs changes included.

### Review process

**When asked to "review", only review.** Do not create commits, push, or apply
fixes — report findings as review comments (with code suggestions where
applicable) or file a linked issue. Specifically:

- Triage every comment, including low-confidence hidden ones.
- Never dismiss a comment without explicit owner confirmation; reply with the
  linked issue number or a reason before resolving a conversation.
- Re-review after changes before approving.
- Verify `CHANGELOG.md` is updated for user-visible changes.
<!-- universal:end -->
