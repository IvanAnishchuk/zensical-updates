"""Tests for the post model, discovery, and grouping."""

import datetime
from pathlib import Path

import pytest

from zensical_updates.model import (
    Post,
    PostError,
    discover_posts,
    group_by_category,
    group_by_tag,
    group_by_year,
    load_post,
    make_excerpt,
)


def test_load_post_reads_slug_date_and_taxonomies(tmp_path: Path) -> None:
    p = tmp_path / "hello-world.md"
    p.write_text(
        "---\n"
        "title: Hello World\n"
        "date: 2026-06-11\n"
        "categories:\n"
        "  - weekly-update\n"
        "tags:\n"
        "  - intro\n"
        "  - epf\n"
        "---\n"
        "\n"
        "First paragraph.\n",
        encoding="utf-8",
    )
    post = load_post(p)
    assert post.slug == "hello-world"
    assert post.title == "Hello World"
    assert post.date == datetime.date(2026, 6, 11)
    assert post.categories == ("weekly-update",)
    assert post.tags == ("intro", "epf")


def test_load_post_requires_a_date(tmp_path: Path) -> None:
    p = tmp_path / "no-date.md"
    p.write_text("---\ntitle: No Date\n---\nbody\n", encoding="utf-8")
    with pytest.raises(PostError, match="date"):
        load_post(p)


def test_discover_posts_sorts_newest_first_and_skips_index(tmp_path: Path) -> None:
    (tmp_path / "index.md").write_text(
        "---\ntitle: Updates\n---\nintro, no date\n", encoding="utf-8"
    )
    (tmp_path / "older.md").write_text("---\ndate: 2026-06-01\n---\no\n", encoding="utf-8")
    (tmp_path / "newer.md").write_text("---\ndate: 2026-06-10\n---\nn\n", encoding="utf-8")
    posts = discover_posts(tmp_path)
    assert [p.slug for p in posts] == ["newer", "older"]


def test_make_excerpt_uses_more_marker() -> None:
    body = "# Title\n\nIntro paragraph.\n\n<!-- more -->\n\nThe rest.\n"
    assert make_excerpt(body) == "Intro paragraph."


def test_make_excerpt_falls_back_to_first_paragraph_and_strips_h1() -> None:
    body = "# Title\n\nFirst paragraph here.\n\nSecond paragraph.\n"
    assert make_excerpt(body) == "First paragraph here."


def test_load_post_sets_excerpt_from_body(tmp_path: Path) -> None:
    p = tmp_path / "x.md"
    p.write_text("---\ndate: 2026-06-01\n---\n# Hi\n\nLede sentence.\n", encoding="utf-8")
    assert load_post(p).excerpt == "Lede sentence."


def _post(
    slug: str,
    day: int,
    *,
    categories: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
) -> Post:
    return Post(
        slug=slug,
        title=slug,
        date=datetime.date(2026, 6, day),
        categories=categories,
        tags=tags,
        body="",
        excerpt="",
        source_path=Path(f"{slug}.md"),
    )


def test_group_by_category_collects_and_sorts_keys() -> None:
    newer = _post("newer", 2, categories=("news", "weekly-update"))
    older = _post("older", 1, categories=("news",))
    groups = group_by_category([newer, older])
    assert list(groups) == ["news", "weekly-update"]
    assert groups["news"] == [newer, older]
    assert groups["weekly-update"] == [newer]


def test_group_by_tag_collects_posts() -> None:
    p = _post("p", 1, tags=("epf",))
    assert group_by_tag([p]) == {"epf": [p]}


def test_group_by_year_newest_year_first() -> None:
    a = Post("a", "a", datetime.date(2025, 1, 1), (), (), "", "", Path("a.md"))
    b = Post("b", "b", datetime.date(2026, 1, 1), (), (), "", "", Path("b.md"))
    groups = group_by_year([b, a])
    assert list(groups) == [2026, 2025]
    assert groups[2026] == [b]


def test_load_post_accepts_quoted_string_date(tmp_path: Path) -> None:
    p = tmp_path / "q.md"
    p.write_text('---\ndate: "2026-06-05"\n---\nx\n', encoding="utf-8")
    assert load_post(p).date == datetime.date(2026, 6, 5)


def test_load_post_coerces_datetime_to_date(tmp_path: Path) -> None:
    p = tmp_path / "dt.md"
    p.write_text("---\ndate: 2026-06-01 09:30:00\n---\nx\n", encoding="utf-8")
    assert load_post(p).date == datetime.date(2026, 6, 1)


def test_load_post_rejects_invalid_date(tmp_path: Path) -> None:
    p = tmp_path / "bad.md"
    p.write_text("---\ndate: not-a-date\n---\nx\n", encoding="utf-8")
    with pytest.raises(PostError, match="invalid date"):
        load_post(p)


def test_load_post_accepts_a_scalar_category(tmp_path: Path) -> None:
    p = tmp_path / "s.md"
    p.write_text("---\ndate: 2026-06-01\ncategories: news\n---\nx\n", encoding="utf-8")
    assert load_post(p).categories == ("news",)


def test_load_post_rejects_a_mapping_taxonomy(tmp_path: Path) -> None:
    p = tmp_path / "m.md"
    p.write_text("---\ndate: 2026-06-01\ntags:\n  k: v\n---\nx\n", encoding="utf-8")
    with pytest.raises(PostError, match="expected a list or string"):
        load_post(p)


def test_make_excerpt_empty_when_only_h1() -> None:
    assert make_excerpt("# Only a title\n") == ""


def test_load_post_rejects_a_non_date_typed_date(tmp_path: Path) -> None:
    p = tmp_path / "n.md"
    p.write_text("---\ndate: 123\n---\nx\n", encoding="utf-8")
    with pytest.raises(PostError, match="invalid date"):
        load_post(p)
