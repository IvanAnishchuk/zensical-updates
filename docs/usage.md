# Usage

## Write posts

Put one Markdown file per post in your source directory (default `updates/`, set
by the `source` config key). The file stem becomes the slug and the URL segment,
so name files for the URL you want: `updates/hello-world.md` renders at
`/updates/hello-world/`.

Each post needs a `date` in front matter. Use block-style lists for `categories`
and `tags`; a flow list like `[weekly-update]` breaks zensical's strict build,
which reads it as an unresolved reference link.

```markdown
---
date: 2026-06-11
categories:
  - weekly-update
tags:
  - epf
---

# Hello world

The first paragraph becomes the listing excerpt. Mark a cut point with
`<!-- more -->` to control where the excerpt ends.
```

An optional `updates/index.md` holds the section intro. Its body is placed above
the generated listing on the landing page.

## Configure

Settings live in `zensical.toml` under `[project.extra.zensical_updates]`:

```toml
[project.extra.zensical_updates]
base = "updates"        # section dir under docs/ and the URL base
source = "updates"      # where your post files live, outside docs/
intro = "index.md"      # the intro file within source/
excerpt_marker = "<!-- more -->"
emit_tags = true
emit_categories = true
emit_archive = true
```

## Project Pages and the base path

A site served under a sub-path needs that sub-path in every link. GitHub project
Pages serve at `https://<user>.github.io/<repo>/`, so a link to `/updates/foo/`
404s; it has to be `/<repo>/updates/foo/`. The generator reads `[project]
site_url` and prepends its path to every emitted link.

```toml
[project]
site_url = "https://ivananishchuk.github.io/eth-protocol-fellowship/"
```

With that set, a post link becomes `/eth-protocol-fellowship/updates/foo/`. The
files on disk still live at `docs/<base>/`; only the URLs gain the prefix. A
root-served site (no `site_url`, or one with no path) gets plain `/updates/foo/`.

`site_url` also gates the `feed.xml` and `sitemap.xml` the build writes for the
section. Both carry fully-qualified URLs, so the build prints a warning and skips
them when `site_url` is absent.

## Build

```bash
zensical-updates build              # generate docs/<base>/
zensical build --clean --strict     # build the site
```

The generated `docs/<base>/` tree is build output. Add it to `.gitignore`. Run
`zensical-updates clean` to remove it. An invalid post (for example one with no
`date`) fails the build with a message naming the file.

## Library

The same operations are available as functions:

```python
from pathlib import Path

from zensical_updates import Config, build_site, clean_site

result = build_site(Config(), Path("."))
print(result.post_urls)
```

The supported surface is whatever `zensical_updates.__all__` lists. See the
[API Reference](api.md).
