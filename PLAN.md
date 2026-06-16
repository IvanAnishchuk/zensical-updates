# zensical-updates, Build Plan and Spec

**Goal:** a small, well-tested CLI that generates a dated "Updates" section for a
zensical site as plain Markdown, so a writer keeps authoring posts in Markdown and
the listing, archives, and taxonomy pages are produced for them. Ship a v1 the
EPF site (`~/src/IvanAnishchuk/eth-protocol-fellowship`) can depend on.

**License:** CC0-1.0. **Original implementation:** write original code; you may
read the upstream for understanding, do not copy its source, text, layout, or
tests. The requirements here come from this project's own analysis of zensical's
behavior. See `CLAUDE.md`.

---

## Integration contract (zensical 0.0.45)

These are hard requirements, each one learned from a build spike against the
pinned zensical. Violating any of them ships broken output.

1. **Delivery is a CLI pre-build step, not a plugin.** zensical 0.0.45 discovers
   only `mkdocs.themes` entry points. It does not discover a `zensical.plugins`
   group and never calls plugin lifecycle hooks (`on_pre_build` and friends do not
   run). So the tool must write Markdown into the docs tree first, then the site
   build runs:

   ```
   zensical-updates build      # writes the generated Markdown
   zensical build --clean --strict
   ```

   You may also register a `zensical.plugins` entry point for the day zensical
   grows a real module API, but the CLI path is the one that works today and the
   one tests and CI must exercise.

2. **A page's URL is its on-disk path.** With `use_directory_urls`,
   `docs/updates/foo.md` renders to `/updates/foo/`. zensical routes by file
   location; it has no per-file slug override we can rely on. Therefore every link
   the generator emits to a post must equal the post's real rendered path.

   **Separate source and output (decided).** Writers keep posts in a committed
   source dir outside `docs/` (default `updates/` at the repo root, config key
   `source`). The generator copies each post to `docs/<base>/<slug>.md` (for the
   EPF site `<base>` is `updates`) and emits the section around it, so a post
   renders at `/<base>/<slug>/` where `<slug>` is the file stem. No date prefix in
   the filename (it would land in the URL and break the link); the date comes from
   front matter. The whole `docs/<base>/` tree is generated output.

3. **Front matter lists must be block style.** zensical's strict build runs a link
   validator over the raw Markdown, **including the front matter**, and reads a
   YAML flow sequence like `categories: [weekly-update]` as a Markdown shortcut
   reference link `[weekly-update]` with no definition. That aborts
   `--strict`. Two consequences:
   - The authoring convention requires block lists in posts:
     `categories:\n  - weekly-update`. Document this; the EPF site already does.
   - The Markdown the generator itself emits must not contain bare `[label]`
     tokens outside real links. Use proper `[text](url)` links (these validate
     fine) and never leave a dangling `[x]`.

4. **No not-in-nav requirement.** zensical 0.0.45 validates links and footnotes
   only. It does not warn or fail on pages that exist but are absent from the nav.
   So generated archive, tag, and category pages need no nav entries; the
   generator can create as many as it likes. Only the section index
   (`docs/<base>/index.md`) needs a nav entry, which the consumer site adds.

5. **Generated output stays out of git and never overwrites prose.** The writer's
   post files and the section intro are committed source. Everything the generator
   produces (the listing, archives, tag and category pages) is build output: it
   must be gitignorable and regenerated each build. Do not append generated blocks
   into committed files in a way that leaves the working tree dirty or risks
   committing the block. The separate-source layout satisfies this: the writer's
   source tree is read-only to the generator, and the whole `docs/<base>/` output
   tree is gitignored (see "Resolved design decisions").

6. **Discovery ignores the generator's own output.** Post discovery reads the
   committed source dir, never the generated `docs/<base>/` output tree, so
   generated pages are never re-ingested as posts on the next run.

7. **Deterministic.** Stable slugs, stable ordering (sort posts by front-matter
   date, newest first), byte-stable output, so builds reproduce and diffs stay
   clean.

---

## v1 feature scope

- **Index listing:** recent posts with title, date, tags, categories, excerpt,
  linked to `/<base>/<slug>/`.
- **Archives:** a landing plus per-year pages.
- **Taxonomies:** tag pages and category pages, each listing its posts. The EPF
  site's categories are `weekly-update`, `project-update`, `news`; keep the tool
  generic (any tag or category string works).
- **Config:** read `[project.extra.zensical_updates]` from `zensical.toml`
  (zensical ignores the `[project.extra]` namespace, so it is a safe home).
  Suggested keys: `base` (the section dir and URL base, default `updates`),
  `source` (where the writer's post files live, default `updates/` at the repo
  root, outside `docs/`), toggles for tags/categories/archives, pagination,
  excerpt marker.
- **CLI:** `zensical-updates build` and `zensical-updates clean`. A
  `--strict`/`--fail-on-warnings` flag for CI is welcome.

---

## Staged build

- **Stage 0, scaffold.** Generate from `~/src/python-project-templates` (`library`
  template): package `zensical_updates`, CC0, `requires-python >= 3.11`, CLI on.
  `git init`, first commit. Add a CC0 `LICENSE`.
- **Stage 1, discovery + front matter.** Find post files under the configured
  posts dir, skip generated output (contract 6), derive `slug` from the file stem,
  read `date` and taxonomies from block-list front matter, validate.
- **Stage 2, model.** Posts, tags, categories, archive periods; sort newest first
  (contract 7).
- **Stage 3, emitters.** Produce the index listing, archive landing and per-year
  pages, tag pages, category pages, as zensical-safe Markdown whose post links are
  `/<base>/<slug>/` (contract 2) and whose own markup has no dangling `[x]`
  (contract 3).
- **Stage 4, CLI + config.** `build`/`clean`, config loader for
  `[project.extra.zensical_updates]`.
- **Stage 5, tests (the important one).** Unit tests for slug/sort/parse, plus an
  **integration test**: lay down a fixture site with a couple of posts, run the
  generator, run `zensical build --clean --strict`, and assert (a) the build
  succeeds and (b) each generated `/<base>/<slug>/` link resolves to a real
  `site/<base>/<slug>/index.html`. This test is what guards contracts 2 and 3,
  the two that fail silently otherwise (absolute links are not validated by
  zensical, so a wrong one ships green).
- **Stage 6, docs + release.** README, usage, changelog. Publishing to PyPI is
  optional; the consumer can start from a git pin.
- **Stage 7, integrate into the EPF site.** Add `zensical-updates` to that repo's
  `pyproject.toml`, add the `[project.extra.zensical_updates]` table, add the
  generate step to its `docs.yml` CI before the build, gitignore the generated
  output, and replace the stub `docs/updates/index.md` with the generated section.

---

## Resolved design decisions

- **Layout: separate source and output.** Writer's posts in a committed source
  dir outside `docs/` (default `updates/`, key `source`); the whole `docs/<base>/`
  is generated and gitignored. See contract 2.
- **Index intro + listing.** The generator owns `docs/<base>/index.md` (gitignored)
  and builds it from a committed intro partial (kept in the source tree, e.g.
  `updates/index.md`, configurable) followed by the generated recent-posts
  listing. Keeps git clean and the listing on the landing page.
- **Forward-compat plugin entry point.** Skip for v1 (YAGNI). Add a
  `zensical.plugins` entry point when zensical gains a module API.
- **Excerpts.** `<!-- more -->` marker, first-paragraph fallback, strip the post
  H1 so it never bleeds into the excerpt.
- **Build order.** `zensical-updates build` runs before `zensical build`/`serve`
  (contract 1); a bare build on a fresh clone finds an empty `docs/<base>/` until
  the generator runs. The Stage 5 integration test guards the full chain.

## Acceptance

`zensical-updates build && zensical build --clean --strict` over the fixture
passes, every generated post link resolves, no generated content is committed, and
tests are green at the template's coverage floor.
