"""Orchestrate a build: discover source posts, then write the generated section.

Reads posts from ``<root>/<source>`` and writes the whole generated section to
``<root>/docs/<base>/`` (copied posts plus the index, archive, and taxonomy
pages). The output tree is regenerated each run and is meant to be gitignored.
The source tree is read-only here, so committed prose is never touched.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from zensical_updates.feed import build_feed, make_renderer
from zensical_updates.frontmatter import split_front_matter
from zensical_updates.model import (
    discover_posts,
    group_by_category,
    group_by_tag,
    group_by_year,
)
from zensical_updates.render import (
    render_archive_index,
    render_category,
    render_category_index,
    render_index,
    render_tag,
    render_tag_index,
    render_year,
)
from zensical_updates.urls import post_url, slugify

if TYPE_CHECKING:
    from pathlib import Path

    from zensical_updates.config import Config


@dataclass
class BuildResult:
    """What a build produced: the output dir, files written, and post URLs."""

    out_dir: Path
    written: list[Path] = field(default_factory=list)
    post_urls: list[str] = field(default_factory=list)
    feed_path: Path | None = None


def clean_site(config: Config, root: Path) -> None:
    """Remove the generated output tree, if present."""
    out_dir = root / "docs" / config.base
    if out_dir.exists():
        shutil.rmtree(out_dir)


def build_site(config: Config, root: Path) -> BuildResult:
    """Generate the full section into ``docs/<base>/`` and report what was written."""
    source_dir = root / config.source
    out_dir = root / "docs" / config.base
    clean_site(config, root)
    out_dir.mkdir(parents=True, exist_ok=True)

    posts = discover_posts(source_dir, index_name=config.intro)
    # Links carry the site sub-path (config.url_base); the output dir above uses
    # config.base, so a project Pages deploy is served correctly without moving files.
    base = config.url_base
    result = BuildResult(out_dir=out_dir)

    # Copy each post verbatim so it renders at /<base>/<slug>/.
    for post in posts:
        dest = out_dir / f"{post.slug}.md"
        shutil.copyfile(post.source_path, dest)
        result.written.append(dest)
        result.post_urls.append(post_url(base, post.slug))

    intro = _read_intro(source_dir / config.intro)
    _write(out_dir / "index.md", render_index(posts, base, intro=intro), result)

    if config.emit_archive:
        _write(out_dir / "archive" / "index.md", render_archive_index(posts, base), result)
        for year, year_posts in group_by_year(posts).items():
            page = render_year(year, year_posts, base)
            _write(out_dir / "archive" / str(year) / "index.md", page, result)

    if config.emit_tags:
        tags = group_by_tag(posts)
        _write(out_dir / "tags" / "index.md", render_tag_index(tags, base), result)
        for tag, tag_posts in tags.items():
            page = render_tag(tag, tag_posts, base)
            _write(out_dir / "tags" / slugify(tag) / "index.md", page, result)

    if config.emit_categories:
        cats = group_by_category(posts)
        _write(out_dir / "categories" / "index.md", render_category_index(cats, base), result)
        for cat, cat_posts in cats.items():
            page = render_category(cat, cat_posts, base)
            _write(out_dir / "categories" / slugify(cat) / "index.md", page, result)

    if config.emit_feed and config.site_url:
        render = make_renderer(root, config)
        feed_posts = posts if config.feed_limit <= 0 else posts[: config.feed_limit]
        feed_xml = build_feed(config, feed_posts, render)
        feed_file = out_dir / "feed.xml"
        feed_file.write_text(feed_xml, encoding="utf-8")
        result.written.append(feed_file)
        result.feed_path = feed_file

    return result


def _read_intro(path: Path) -> str:
    if not path.exists():
        return ""
    _, body = split_front_matter(path.read_text(encoding="utf-8"))
    return body.strip()


def _write(path: Path, content: str, result: BuildResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    result.written.append(path)
