"""Tests for the zensical.toml config loader."""

from typing import TYPE_CHECKING

from zensical_updates.config import Config, load_config

if TYPE_CHECKING:
    from pathlib import Path


def test_load_config_reads_the_extra_table(tmp_path: Path) -> None:
    (tmp_path / "zensical.toml").write_text(
        '[project.extra.zensical_updates]\nbase = "news"\nsource = "posts"\nemit_archive = false\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_path / "zensical.toml")
    assert cfg.base == "news"
    assert cfg.source == "posts"
    assert cfg.emit_archive is False


def test_load_config_defaults_when_table_absent(tmp_path: Path) -> None:
    (tmp_path / "zensical.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    cfg = load_config(tmp_path / "zensical.toml")
    assert cfg == Config()
    assert cfg.base == "updates"
    assert cfg.source == "updates"


def test_load_config_reads_the_project_site_url(tmp_path: Path) -> None:
    (tmp_path / "zensical.toml").write_text(
        '[project]\nsite_url = "https://example.github.io/repo/"\n'
        '[project.extra.zensical_updates]\nbase = "updates"\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_path / "zensical.toml")
    assert cfg.site_url == "https://example.github.io/repo/"


def test_url_base_carries_the_site_subpath() -> None:
    cfg = Config(base="updates", site_url="https://example.github.io/repo/")
    assert cfg.url_base == "repo/updates"


def test_url_base_is_just_base_without_a_site_url() -> None:
    assert Config(base="updates").url_base == "updates"


def test_url_base_is_just_base_for_a_root_served_site() -> None:
    # A site_url with no path component (served at the domain root) adds no
    # prefix and must not introduce an extra slash.
    assert Config(base="updates", site_url="https://example.com/").url_base == "updates"
    assert Config(base="updates", site_url="https://example.com").url_base == "updates"


def test_load_config_reads_feed_and_site_metadata(tmp_path: Path) -> None:
    (tmp_path / "zensical.toml").write_text(
        "[project]\n"
        'site_name = "My Site"\n'
        'site_description = "All the news"\n'
        'language = "fr"\n'
        "[project.extra.zensical_updates]\n"
        "emit_feed = false\n"
        "feed_limit = 10\n",
        encoding="utf-8",
    )
    cfg = load_config(tmp_path / "zensical.toml")
    assert cfg.site_name == "My Site"
    assert cfg.site_description == "All the news"
    assert cfg.language == "fr"
    assert cfg.emit_feed is False
    expected_feed_limit = 10
    assert cfg.feed_limit == expected_feed_limit


def test_feed_config_defaults() -> None:
    cfg = Config()
    assert cfg.emit_feed is True
    assert cfg.feed_limit == 0
    assert cfg.language == "en"
    assert cfg.site_name == ""
