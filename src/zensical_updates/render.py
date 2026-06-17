"""Render generated pages as zensical-safe Markdown.

Every link is a site-absolute directory URL (see :mod:`urls`). Markup uses only
real ``[text](url)`` links, never a bare ``[label]``: zensical's strict build
reads a bare bracket as an unresolved reference link and fails.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from zensical_updates.model import group_by_year
from zensical_updates.urls import (
    archive_url,
    category_index_url,
    category_url,
    index_url,
    post_url,
    tag_index_url,
    tag_url,
    year_url,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping
    from typing import Literal

    from zensical_updates.model import Post

_EMPTY = "_No updates yet._"


def render_browse(
    base: str,
    *,
    current: Literal["index", "tags", "categories", "archive"],
    tags: bool = True,
    categories: bool = True,
    archive: bool = True,
) -> str:
    """Build the inline nav line linking the enabled index pages.

    ``current`` (one of ``"index"``, ``"tags"``, ``"categories"``, ``"archive"``)
    names the page being rendered, so it is never linked to itself. The Updates
    index is always a target. Returns ``""`` only when ``current`` is ``"index"``
    and the other sections are all disabled.
    """
    targets = [
        ("Updates", index_url(base), "index", True),
        ("Tags", tag_index_url(base), "tags", tags),
        ("Categories", category_index_url(base), "categories", categories),
        ("Archive", archive_url(base), "archive", archive),
    ]
    links = [
        f"[{label}]({url})" for label, url, key, enabled in targets if enabled and key != current
    ]
    return " · ".join(links)


def _term_links(terms: Iterable[str], url: Callable[[str], str]) -> str:
    return ", ".join(f"[{term}]({url(term)})" for term in terms)


def render_post_entry(post: Post, base: str) -> str:
    """Render one listing entry: linked title, date, taxonomies, excerpt."""
    parts = [f"## [{post.title}]({post_url(base, post.slug)})", "", post.date.isoformat()]
    if post.categories:
        links = _term_links(post.categories, lambda c: category_url(base, c))
        parts += ["", f"Categories: {links}"]
    if post.tags:
        links = _term_links(post.tags, lambda t: tag_url(base, t))
        parts += ["", f"Tags: {links}"]
    if post.excerpt:
        parts += ["", post.excerpt]
    return "\n".join(parts)


def render_listing(posts: Iterable[Post], base: str) -> str:
    entries = [render_post_entry(post, base) for post in posts]
    return "\n\n".join(entries) if entries else _EMPTY


def render_index(posts: Iterable[Post], base: str, *, intro: str = "") -> str:
    """Render the section landing: the intro (or a default H1) plus the listing."""
    head = intro.strip() or "# Updates"
    return f"{head}\n\n{render_listing(posts, base)}\n"


def render_year(year: int, posts: Iterable[Post], base: str) -> str:
    return f"# Updates {year}\n\n{render_listing(posts, base)}\n"


def render_tag(tag: str, posts: Iterable[Post], base: str) -> str:
    return f"# Tag: {tag}\n\n{render_listing(posts, base)}\n"


def render_category(category: str, posts: Iterable[Post], base: str) -> str:
    return f"# Category: {category}\n\n{render_listing(posts, base)}\n"


def _term_index(title: str, groups: Mapping[str, list[Post]], url: Callable[[str], str]) -> str:
    lines = [f"# {title}", ""]
    lines += [f"- [{term}]({url(term)}) ({len(posts)})" for term, posts in groups.items()]
    return "\n".join(lines) + "\n"


def render_tag_index(groups: Mapping[str, list[Post]], base: str) -> str:
    return _term_index("Tags", groups, lambda t: tag_url(base, t))


def render_category_index(groups: Mapping[str, list[Post]], base: str) -> str:
    return _term_index("Categories", groups, lambda c: category_url(base, c))


def render_archive_index(posts: Iterable[Post], base: str) -> str:
    """Render the archive landing: each year, linked, with its post count."""
    lines = ["# Archive", ""]
    lines += [
        f"- [{year}]({year_url(base, year)}) ({len(year_posts)})"
        for year, year_posts in group_by_year(posts).items()
    ]
    return "\n".join(lines) + "\n"
