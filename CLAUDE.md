# zensical-updates, Agent Notes

A sidecar "Updates" (blog) generator for [zensical](https://zensical.org) static
sites. zensical ships no blog plugin, so this tool generates a dated, linkable
Updates section (index listing, per-year archives, tag and category pages) as
plain Markdown that zensical then builds. It runs as a CLI pre-build step:
`zensical-updates build` before `zensical build`.

- **Package:** `zensical_updates`. **CLI:** `zensical-updates`. **License:** CC0-1.0.
- **Status:** Stage 0 scaffolded (uv, `src/` layout, typer CLI, CI). Building per
  `PLAN.md`'s staged plan; `HANDOFF.md` is the seeding discovery.

## Hard rules

- **Original implementation, CC0.** This is an original CC0 implementation
  inspired by the concept of `knu2xs/zensical-blog`. You may read the upstream for
  understanding, but write original code: do not copy, paste, or adapt its source,
  text, file layout, or test code. `PLAN.md` captures the requirements, derived
  from this project's own analysis of how zensical behaves. Where something is
  unspecified, reason it out from zensical's observable behavior and write it down.
- **Honor the integration contract.** The consumer site
  (`~/src/IvanAnishchuk/eth-protocol-fellowship`, public, GitHub Pages) drives the
  layout and URL requirements. They are pinned in `PLAN.md` under "Integration
  contract". The build is correct only when generated post links resolve to the
  pages zensical actually renders.
- **Never mutate committed prose.** Generated artifacts stay cleanly separable
  from hand-written content and stay out of git. No in-place edits to a writer's
  Markdown.

## Stack

- Python with **uv**. `src/` layout, `py.typed`. Scaffold from
  `~/src/python-project-templates` (the `library` flavor: packaged library plus a
  CLI). Pick CC0 and `requires-python >= 3.11` at generation time.
- A CLI (`click` or `typer`), front-matter parsing (stdlib `tomllib` for config,
  a small YAML read for post front matter), deterministic Markdown emission.
- Tests with `pytest`. The decisive test is an **integration test** that runs the
  generator and then `zensical build --clean --strict` over a fixture site and
  asserts every generated link resolves (see `PLAN.md`).

## The consumer

`~/src/IvanAnishchuk/eth-protocol-fellowship` is the first and primary user. Its
Updates page is a static stub today; it will depend on this package and switch to
the generated section once v1 ships. Keep the URL/layout contract in lockstep with
that repo's `CLAUDE.md` (the `docs/updates/<slug>.md` -> `/updates/<slug>/` rule
and the block-list front-matter rule both live there too).

## Writing style

Binds on docs, comments, commit messages, PR text. Mirrors Ivan's conventions.

- No em-dashes for subphrases. Use commas, or split into two sentences.
- No contrastive negation ("not X, but Y"). State the positive directly.
- Vary sentence length. Prefer active voice.
- No filler openers or summary closers. Avoid AI-tell vocabulary (delve, leverage,
  robust, seamless, tapestry, landscape, and similar).
