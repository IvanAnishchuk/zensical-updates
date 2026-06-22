"""Tests for the Updates section sitemap."""

import lxml.etree  # ty: ignore[unresolved-import]

from zensical_updates.config import Config
from zensical_updates.sitemap import build_sitemap, render_sitemap

_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def test_render_sitemap_emits_absolute_locs() -> None:
    xml = render_sitemap(
        "https://example.github.io/repo/",
        ["/repo/updates/", "/repo/updates/hello/"],
    )
    root = lxml.etree.fromstring(xml.encode("utf-8"))
    assert root.tag == f"{{{_NS}}}urlset"
    locs = [el.text for el in root.iter(f"{{{_NS}}}loc")]
    assert locs == [
        "https://example.github.io/repo/updates/",
        "https://example.github.io/repo/updates/hello/",
    ]


def test_render_sitemap_with_no_paths_is_an_empty_urlset() -> None:
    xml = render_sitemap("https://example.github.io/repo/", [])
    root = lxml.etree.fromstring(xml.encode("utf-8"))
    assert root.tag == f"{{{_NS}}}urlset"
    assert list(root) == []


def test_build_sitemap_renders_the_given_page_urls() -> None:
    cfg = Config(site_url="https://example.github.io/repo/")
    xml = build_sitemap(cfg, ["/repo/updates/", "/repo/updates/hello/"])
    root = lxml.etree.fromstring(xml.encode("utf-8"))
    locs = [el.text for el in root.iter(f"{{{_NS}}}loc")]
    assert locs == [
        "https://example.github.io/repo/updates/",
        "https://example.github.io/repo/updates/hello/",
    ]
