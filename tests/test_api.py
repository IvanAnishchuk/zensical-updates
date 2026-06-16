"""Tests for the public API."""

from __future__ import annotations

import zensical_updates as lib
from zensical_updates import Greeter, greet


def test_version_exported() -> None:
    assert lib.__version__ == "0.1.0"


def test_public_api_surface() -> None:
    assert set(lib.__all__) == {"Greeter", "greet"}
    for name in lib.__all__:
        assert hasattr(lib, name)


def test_greet_default() -> None:
    assert greet() == "Hello, world!"


def test_greet_named() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_shout() -> None:
    assert greet("Ada", shout=True) == "HELLO, ADA!"


def test_greeter_default() -> None:
    assert Greeter().greet("Ada") == "Hello, Ada!"


def test_greeter_shout() -> None:
    assert Greeter(shout=True).greet("Ada") == "HELLO, ADA!"
