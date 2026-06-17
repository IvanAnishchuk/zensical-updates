"""Tests for site-absolute URL construction."""

from zensical_updates.urls import (
    absolute_url,
    archive_url,
    category_url,
    post_url,
    slugify,
    tag_url,
    year_url,
)


def test_post_url_is_a_directory_path() -> None:
    assert post_url("updates", "hello-world") == "/updates/hello-world/"


def test_slugify_lowercases_and_hyphenates() -> None:
    assert slugify("Weekly Update") == "weekly-update"


def test_slugify_strips_leading_and_trailing_separators() -> None:
    assert slugify("  EPF & News!  ") == "epf-news"


def test_tag_and_category_urls_use_the_slug() -> None:
    assert tag_url("updates", "EPF News") == "/updates/tags/epf-news/"
    assert category_url("updates", "weekly-update") == "/updates/categories/weekly-update/"


def test_archive_urls() -> None:
    assert archive_url("updates") == "/updates/archive/"
    assert year_url("updates", 2026) == "/updates/archive/2026/"


def test_absolute_url_prepends_scheme_and_host() -> None:
    out = absolute_url("https://example.github.io/repo/", "/repo/updates/hello/")
    assert out == "https://example.github.io/repo/updates/hello/"


def test_absolute_url_takes_only_scheme_and_host_from_site_url() -> None:
    # The path argument is authoritative; site_url contributes scheme + host only.
    assert (
        absolute_url("https://example.com/anything/", "/updates/") == "https://example.com/updates/"
    )
