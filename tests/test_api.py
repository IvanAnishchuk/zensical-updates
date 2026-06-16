"""Tests for the public API surface."""

from __future__ import annotations

import zensical_updates as lib


def test_version_exported() -> None:
    assert isinstance(lib.__version__, str)
    assert lib.__version__  # non-empty; sourced from package metadata


def test_public_api_is_importable() -> None:
    for name in lib.__all__:
        assert hasattr(lib, name), name


def test_key_symbols_are_exported() -> None:
    assert {"build_site", "clean_site", "Config", "Post"} <= set(lib.__all__)
