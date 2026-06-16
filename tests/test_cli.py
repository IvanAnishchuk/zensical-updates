"""Tests for the command-line interface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

from zensical_updates.cli import app

if TYPE_CHECKING:
    from pathlib import Path

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


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
