"""Tests for the maintenance CLI."""

from __future__ import annotations

from typer.testing import CliRunner

from zensical_updates.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_info() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_hello() -> None:
    result = runner.invoke(app, ["hello", "Ada"])
    assert result.exit_code == 0
    assert "Hello, Ada!" in result.output


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert "Usage" in result.output or "Maintenance" in result.output
