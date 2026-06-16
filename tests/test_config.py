"""Tests for the zensical.toml config loader."""

from pathlib import Path

from zensical_updates.config import Config, load_config


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
