"""Tests for the build orchestration."""

from pathlib import Path

from zensical_updates.build import build_site, clean_site
from zensical_updates.config import Config


def _write_post(
    dir_path: Path,
    slug: str,
    date: str,
    *,
    categories: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
) -> None:
    text = f"---\ndate: {date}\n"
    if categories:
        text += "categories:\n" + "".join(f"  - {c}\n" for c in categories)
    if tags:
        text += "tags:\n" + "".join(f"  - {t}\n" for t in tags)
    text += f"---\n\nBody of {slug}.\n"
    (dir_path / f"{slug}.md").write_text(text, encoding="utf-8")


def test_build_copies_posts_and_writes_pages(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome.\n", encoding="utf-8")
    _write_post(src, "hello", "2026-06-11", categories=("weekly-update",), tags=("epf",))

    result = build_site(Config(), tmp_path)
    out = tmp_path / "docs" / "updates"

    assert (out / "hello.md").exists()  # post copied verbatim
    index = (out / "index.md").read_text(encoding="utf-8")
    assert "Welcome." in index  # intro carried through
    assert "[hello](/updates/hello/)" in index  # listing links the post
    assert (out / "archive" / "2026" / "index.md").exists()
    assert (out / "tags" / "epf" / "index.md").exists()
    assert (out / "categories" / "weekly-update" / "index.md").exists()
    assert "/updates/hello/" in result.post_urls


def test_build_does_not_mutate_the_source(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    _write_post(src, "hello", "2026-06-11")
    before = (src / "hello.md").read_text(encoding="utf-8")
    build_site(Config(), tmp_path)
    assert (src / "hello.md").read_text(encoding="utf-8") == before


def test_clean_removes_the_output_tree(tmp_path: Path) -> None:
    out = tmp_path / "docs" / "updates"
    out.mkdir(parents=True)
    (out / "index.md").write_text("x", encoding="utf-8")
    clean_site(Config(), tmp_path)
    assert not out.exists()


def test_build_can_disable_taxonomies_and_archive(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    _write_post(src, "hello", "2026-06-11", categories=("news",), tags=("epf",))
    cfg = Config(emit_archive=False, emit_tags=False, emit_categories=False)
    build_site(cfg, tmp_path)
    out = tmp_path / "docs" / "updates"
    assert (out / "index.md").exists()
    assert not (out / "archive").exists()
    assert not (out / "tags").exists()
    assert not (out / "categories").exists()
