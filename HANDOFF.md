# Handoff: zensical-updates

Greenfield project, seeded by a build spike done in the EPF site repo on
2026-06-17. This file is the discovery that justifies `PLAN.md`. Read both, then
start at NEXT ACTION.

## Where this came from

The EPF site (`~/src/IvanAnishchuk/eth-protocol-fellowship`) needs a dated
"Updates" blog on zensical, which has no blog plugin. A spike evaluated the
existing `knu2xs/zensical-blog` sidecar (git pin `305e30a8`) against zensical
`0.0.45`. The integration was rejected for that repo, and the decision is to build
our own generator here as a clean-room CC0 rewrite. The spike's findings are the
spec. Do not pull in the upstream code; it is inspiration only.

## What the spike established (all verified against zensical 0.0.45)

1. **No plugin system yet.** zensical 0.0.45 discovers only `mkdocs.themes` entry
   points. There is no `zensical.plugins` discovery and no plugin lifecycle hook
   gets called. A "single build" plugin is impossible today. The tool must be a
   CLI that writes Markdown before `zensical build` runs. (Confirmed in
   `zensical/config.py` and by an empirical build where a registered plugin
   produced no output.)

2. **`--strict` validates links and footnotes only.** It does not fail on pages
   absent from the nav. So generated taxonomy pages need no nav entries. (Source:
   the validation config maps only `invalid_links`, `invalid_link_anchors`,
   `shadowed_footnotes`; the code comment says navigation validation is
   deliberately not implemented yet.)

3. **The strict link validator scans front matter.** A post with
   `categories: [weekly-update]` fails `--strict`: the validator reads the
   `[weekly-update]` flow sequence as an unresolved Markdown reference link, with a
   diagnostic pointing at the front-matter line. Block-list front matter
   (`- weekly-update`) builds clean. This sets the post authoring convention and
   constrains the Markdown the generator emits (no dangling `[x]`).

4. **A post's URL is its file path.** `docs/updates/posts/2026-06-11-hello.md`
   built to `/updates/posts/2026-06-11-hello/`. The upstream sidecar linked the
   same post as `/updates/hello/` (it stripped the date and dropped the subdir),
   so the listing link was dead. Crucially, `--strict` did **not** catch it:
   zensical only validates relative links, and these generated links are
   site-absolute (`/...`), so a wrong one ships green. The fix is the flat layout
   in `PLAN.md` contract 2: post at `docs/updates/<slug>.md` builds to
   `/updates/<slug>/`, which is exactly what the generator links. Verified: a post
   at `docs/updates/hello.md` builds to `site/updates/hello/index.html` and the
   `/updates/hello/` link resolves.

5. **The upstream sidecar mutates committed files.** It appended generated blocks
   into the canonical `index.md` and wrote taxonomy pages into the docs tree
   (sentinel-marked). In a flat layout it also re-discovered its own generated
   files as posts (seven "no date, skipped" warnings per run). Our design must
   keep generated output gitignorable and out of the writer's files (`PLAN.md`
   contracts 5 and 6).

## Consumer state (the EPF site)

- The Updates page is a static stub at `docs/updates/index.md`, in the nav as
  `{ "Updates" = "updates/index.md" }`. No plugin dependency. Its `CLAUDE.md`
  already documents the flat `/updates/<slug>/` layout and the block-list
  front-matter rule, so the two repos agree on the contract.
- When v1 ships, that repo adds the dependency, a `[project.extra.zensical_updates]`
  table, a CI generate step, and swaps the stub for the generated section
  (`PLAN.md` Stage 7).

## NEXT ACTION

Scaffold the package from `~/src/python-project-templates` (library template:
`zensical_updates`, CC0, Python >= 3.11, CLI), then implement Stages 1 to 5 in
`PLAN.md`. Build the integration test first or early: it is the only guard against
the two silent failures above (wrong post URLs and front-matter link reads). Keep
generated output gitignored. License CC0, clean-room, no upstream code.
