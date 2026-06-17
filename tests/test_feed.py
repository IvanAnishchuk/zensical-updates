"""Tests for the RSS feed builder."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, cast

import feedparser
import pytest

from zensical_updates.config import Config, load_config
from zensical_updates.feed import FeedError, absolutize_html, build_feed, make_renderer
from zensical_updates.model import Post


def _post(slug: str, date: str, *, title: str = "", body: str = "") -> Post:
    return Post(
        slug=slug,
        title=title or slug,
        date=datetime.date.fromisoformat(date),
        categories=(),
        tags=(),
        body=body,
        excerpt="",
        source_path=Path(f"{slug}.md"),
    )


def _cfg() -> Config:
    return Config(
        base="updates",
        site_url="https://example.github.io/repo/",
        site_name="EPF Updates",
        site_description="Project news",
        language="en",
    )


def _stub_render(post: Post) -> str:
    return f"<p>Body of {post.slug}.</p>"


def test_absolutize_resolves_relative_links() -> None:
    base = "https://example.github.io/repo/updates/hello/"
    out = absolutize_html('<p><a href="../other/">x</a></p>', base)
    assert 'href="https://example.github.io/repo/updates/other/"' in out


def test_absolutize_resolves_root_relative_against_origin() -> None:
    base = "https://example.github.io/repo/updates/hello/"
    out = absolutize_html('<p><a href="/at-root/">x</a></p>', base)
    assert 'href="https://example.github.io/at-root/"' in out


def test_absolutize_strips_a_leading_h1() -> None:
    out = absolutize_html('<h1 id="t">Title</h1>\n<p>Body.</p>', "https://example.com/u/h/")
    assert "<h1" not in out
    assert "<p>Body.</p>" in out


def test_absolutize_keeps_text_after_a_stripped_h1() -> None:
    out = absolutize_html("<h1>T</h1>tail text<p>Body.</p>", "https://example.com/u/h/")
    assert "<h1" not in out
    assert "tail text" in out
    assert "<p>Body.</p>" in out


def test_absolutize_empty_returns_empty() -> None:
    assert absolutize_html("", "https://example.com/") == ""


def test_build_feed_parses_clean_with_feedparser() -> None:
    posts = [_post("b", "2026-06-11", title="B"), _post("a", "2026-05-01", title="A")]
    xml = build_feed(_cfg(), posts, _stub_render)
    parsed = cast("Any", feedparser.parse(xml))
    assert not parsed.bozo
    assert parsed.feed.title == "EPF Updates"
    # The channel <link> points at the updates index, not the feed file itself.
    assert parsed.feed.link == "https://example.github.io/repo/updates/"
    assert len(parsed.entries) == len(posts)
    assert parsed.entries[0].id == "https://example.github.io/repo/updates/b/"
    assert parsed.entries[0].id.startswith("https://")
    assert "<p>Body of b.</p>" in parsed.entries[0].summary


def test_build_feed_has_atom_self_and_absolute_feed_url() -> None:
    xml = build_feed(_cfg(), [_post("a", "2026-05-01")], _stub_render)
    assert 'rel="self"' in xml
    assert "https://example.github.io/repo/updates/feed.xml" in xml


def test_build_feed_is_byte_deterministic() -> None:
    posts = [_post("a", "2026-05-01")]
    xml = build_feed(_cfg(), posts, _stub_render)
    # Dates come from the post, not the wall clock: a fixed pubDate, reproducible bytes.
    assert "01 May 2026 00:00:00 +0000" in xml
    assert build_feed(_cfg(), posts, _stub_render) == xml


def test_build_feed_zero_posts_is_valid() -> None:
    parsed = cast("Any", feedparser.parse(build_feed(_cfg(), [], _stub_render)))
    assert not parsed.bozo
    assert parsed.entries == []


pytest.importorskip("zensical")


def test_make_renderer_returns_absolutized_html(tmp_path: Path) -> None:
    (tmp_path / "docs" / "updates").mkdir(parents=True)
    (tmp_path / "zensical.toml").write_text(
        "[project]\n"
        'site_name = "S"\n'
        'site_url = "https://example.github.io/repo/"\n'
        'docs_dir = "docs"\n'
        'site_dir = "site"\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_path / "zensical.toml")
    render = make_renderer(tmp_path, cfg)
    html = render(_post("hello", "2026-06-11", body="See [other](other.md) for more."))
    assert "https://example.github.io/repo/updates/other/" in html


def test_make_renderer_raises_a_feed_error_when_zensical_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("zensical_updates.feed._zensical_render", None)
    with pytest.raises(FeedError, match="needs"):
        make_renderer(tmp_path, _cfg())


def test_make_renderer_raises_when_zensical_toml_is_missing(tmp_path: Path) -> None:
    # build_site can be called programmatically with a Config that has site_url
    # set but no zensical.toml on disk; fail with a clear message, not a stray error.
    with pytest.raises(FeedError, match=r"zensical\.toml"):
        make_renderer(tmp_path, _cfg())


def test_renderer_wraps_a_zensical_render_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "docs" / "updates").mkdir(parents=True)
    (tmp_path / "zensical.toml").write_text(
        "[project]\n"
        'site_name = "S"\n'
        'site_url = "https://example.github.io/repo/"\n'
        'docs_dir = "docs"\n'
        'site_dir = "site"\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_path / "zensical.toml")

    def boom(*_args: object, **_kwargs: object) -> dict[str, str]:
        msg = "api moved"
        raise RuntimeError(msg)

    # Patch before make_renderer captures the render function from the module.
    monkeypatch.setattr("zensical_updates.feed._zensical_render", boom)
    render = make_renderer(tmp_path, cfg)
    with pytest.raises(FeedError, match="zensical render failed"):
        render(_post("hello", "2026-06-11", body="x"))
