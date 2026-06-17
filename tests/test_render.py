"""Tests for the Markdown emitters."""

import datetime
import re
from pathlib import Path

from zensical_updates.model import Post, group_by_category, group_by_tag
from zensical_updates.render import (
    render_archive_index,
    render_browse,
    render_category,
    render_category_index,
    render_index,
    render_post_entry,
    render_tag,
    render_tag_index,
    render_year,
)


def _post(
    slug: str,
    *,
    title: str | None = None,
    date: tuple[int, int, int] = (2026, 6, 1),
    categories: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    excerpt: str = "",
) -> Post:
    year, month, day = date
    return Post(
        slug=slug,
        title=title or slug,
        date=datetime.date(year, month, day),
        categories=categories,
        tags=tags,
        body="",
        excerpt=excerpt,
        source_path=Path(f"{slug}.md"),
    )


def _assert_brackets_are_links(md: str) -> None:
    """Every ``]`` must be immediately followed by ``(`` (a real inline link)."""
    for match in re.finditer(r"\]", md):
        following = md[match.end() : match.end() + 1]
        context = md[max(0, match.start() - 25) : match.end() + 5]
        assert following == "(", f"dangling bracket near: {context!r}"


def test_index_includes_intro_and_post_links() -> None:
    posts = [_post("hello-world", title="Hello World", excerpt="The lede.")]
    md = render_index(posts, "updates", intro="# Updates\n\nWelcome.")
    assert "Welcome." in md
    assert "[Hello World](/updates/hello-world/)" in md
    assert "The lede." in md
    _assert_brackets_are_links(md)


def test_post_entry_links_categories_and_tags() -> None:
    p = _post("p", categories=("weekly-update",), tags=("epf", "intro"))
    md = render_post_entry(p, "updates")
    assert "[weekly-update](/updates/categories/weekly-update/)" in md
    assert "[epf](/updates/tags/epf/)" in md
    _assert_brackets_are_links(md)


def test_archive_index_lists_years_with_links() -> None:
    posts = [_post("a", date=(2026, 1, 1)), _post("b", date=(2025, 1, 1))]
    md = render_archive_index(posts, "updates")
    assert "[2026](/updates/archive/2026/)" in md
    assert "[2025](/updates/archive/2025/)" in md
    _assert_brackets_are_links(md)


def test_year_and_taxonomy_pages_list_posts() -> None:
    posts = [_post("hello", title="Hello")]
    assert "[Hello](/updates/hello/)" in render_year(2026, posts, "updates")
    assert "[Hello](/updates/hello/)" in render_tag("epf", posts, "updates")
    assert "[Hello](/updates/hello/)" in render_category("news", posts, "updates")


def test_tag_index_lists_tags_with_links() -> None:
    md = render_tag_index(group_by_tag([_post("a", tags=("epf",))]), "updates")
    assert "[epf](/updates/tags/epf/)" in md
    _assert_brackets_are_links(md)


def test_category_index_lists_categories_with_links() -> None:
    md = render_category_index(group_by_category([_post("a", categories=("news",))]), "updates")
    assert "[news](/updates/categories/news/)" in md
    _assert_brackets_are_links(md)


def test_empty_listing_has_a_placeholder() -> None:
    md = render_index([], "updates")
    assert "No updates yet" in md
    _assert_brackets_are_links(md)


def test_browse_links_enabled_indexes_and_omits_current() -> None:
    nav = render_browse("updates", current="tags", categories=True, archive=True)
    assert "[Updates](/updates/)" in nav
    assert "[Categories](/updates/categories/)" in nav
    assert "[Archive](/updates/archive/)" in nav
    assert "[Tags]" not in nav
    _assert_brackets_are_links(nav)


def test_browse_drops_disabled_indexes() -> None:
    nav = render_browse("updates", current="index", tags=True, categories=False, archive=False)
    assert "[Tags](/updates/tags/)" in nav
    assert "[Categories]" not in nav
    assert "[Archive]" not in nav


def test_browse_is_empty_when_no_other_target() -> None:
    nav = render_browse("updates", current="tags", categories=False, archive=False)
    assert nav == "[Updates](/updates/)"
