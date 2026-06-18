"""Post model, discovery, and grouping.

A post is one Markdown file in the source tree. Its slug is the file stem: the
on-disk path under ``docs/<base>/`` is the rendered URL, so the stem becomes the
URL segment. Front matter carries the date and taxonomies; the body feeds the
excerpt and the rendered page.
"""

import datetime
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from zensical_updates.frontmatter import split_front_matter


class PostError(ValueError):
    """A post file is missing required front matter or carries an invalid value."""


@dataclass(frozen=True)
class Post:
    """One update post, parsed from a source Markdown file."""

    slug: str
    title: str
    date: datetime.date
    categories: tuple[str, ...]
    tags: tuple[str, ...]
    body: str
    excerpt: str
    source_path: Path


def load_post(path: Path) -> Post:
    """Parse a single post file into a :class:`Post`."""
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    raw_date = meta.get("date")
    if raw_date is None:
        msg = f"{path}: post front matter is missing a 'date'"
        raise PostError(msg)
    title = meta.get("title") or path.stem
    return Post(
        slug=path.stem,
        title=str(title),
        date=_coerce_date(raw_date, path),
        categories=_str_tuple(meta.get("categories")),
        tags=_str_tuple(meta.get("tags")),
        body=body,
        excerpt=make_excerpt(body),
        source_path=path,
    )


def discover_posts(source: Path, *, index_name: str = "index.md") -> list[Post]:
    """Find and parse every post in ``source``, newest first.

    The intro file (``index_name``) is the section landing copy, not a post, so
    it is skipped. Ordering is date descending, ties broken by slug ascending,
    so the output is deterministic.
    """
    posts = [load_post(path) for path in sorted(source.glob("*.md")) if path.name != index_name]
    posts.sort(key=lambda p: p.slug)
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def make_excerpt(body: str, *, marker: str = "<!-- more -->") -> str:
    """Return a short excerpt: text up to ``marker``, else the first paragraph.

    A leading H1 is skipped so the post title never bleeds into the excerpt.
    """
    head = body.split(marker, 1)[0] if marker in body else body
    for para in head.split("\n\n"):
        block = para.strip()
        if not block or block.startswith("# "):
            continue
        return " ".join(line.strip() for line in block.splitlines())
    return ""


def group_by_category(posts: Iterable[Post]) -> dict[str, list[Post]]:
    """Map each category to its posts, keys sorted alphabetically."""
    return _group_by_terms(posts, lambda p: p.categories)


def group_by_tag(posts: Iterable[Post]) -> dict[str, list[Post]]:
    """Map each tag to its posts, keys sorted alphabetically."""
    return _group_by_terms(posts, lambda p: p.tags)


def group_by_year(posts: Iterable[Post]) -> dict[int, list[Post]]:
    """Map each year to its posts, newest year first."""
    out: dict[int, list[Post]] = {}
    for post in posts:
        out.setdefault(post.date.year, []).append(post)
    return dict(sorted(out.items(), reverse=True))


def _group_by_terms(
    posts: Iterable[Post], terms: Callable[[Post], tuple[str, ...]]
) -> dict[str, list[Post]]:
    out: dict[str, list[Post]] = {}
    for post in posts:
        for term in terms(post):
            out.setdefault(term, []).append(post)
    return dict(sorted(out.items()))


def _coerce_date(value: object, path: Path) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError as exc:
            msg = f"{path}: invalid date {value!r}"
            raise PostError(msg) from exc
    msg = f"{path}: invalid date {value!r}"
    raise PostError(msg)


def _str_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(v) for v in value)
    msg = f"expected a list or string, got {type(value).__name__}"
    raise PostError(msg)
