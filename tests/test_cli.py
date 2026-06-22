"""Tests for the command-line interface."""

from pathlib import Path

from typer.testing import CliRunner

import zensical_updates as lib
from zensical_updates.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert lib.__version__ in result.output


def test_info() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "build_site" in result.output


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert "Usage" in result.output or "Generate" in result.output


def test_build_then_clean(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "p.md").write_text("---\ndate: 2026-06-01\n---\nBody.\n", encoding="utf-8")

    built = runner.invoke(app, ["build", "--root", str(tmp_path)])
    assert built.exit_code == 0, built.output
    assert (tmp_path / "docs" / "updates" / "p.md").exists()
    assert (tmp_path / "docs" / "updates" / "index.md").exists()

    cleaned = runner.invoke(app, ["clean", "--root", str(tmp_path)])
    assert cleaned.exit_code == 0, cleaned.output
    assert not (tmp_path / "docs" / "updates").exists()


def test_build_reports_an_invalid_post(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "bad.md").write_text("---\ntitle: No Date\n---\nx\n", encoding="utf-8")
    result = runner.invoke(app, ["build", "--root", str(tmp_path)])
    assert result.exit_code == 1
    assert "date" in result.output


def test_build_warns_when_site_url_missing(tmp_path: Path) -> None:
    (tmp_path / "zensical.toml").write_text('[project]\nsite_name = "S"\n', encoding="utf-8")
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n", encoding="utf-8")
    result = runner.invoke(app, ["build", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "feed skipped" in result.stdout.lower()


def test_build_warns_when_sitemap_skipped(tmp_path: Path) -> None:
    (tmp_path / "zensical.toml").write_text('[project]\nsite_name = "S"\n', encoding="utf-8")
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n", encoding="utf-8")
    result = runner.invoke(app, ["build", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "sitemap skipped" in result.stdout.lower()
