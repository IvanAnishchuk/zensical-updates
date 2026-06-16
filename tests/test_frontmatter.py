"""Tests for front-matter parsing."""

import pytest

from zensical_updates.frontmatter import split_front_matter


def test_splits_block_list_front_matter_from_body() -> None:
    text = (
        "---\n"
        "title: Hello World\n"
        "date: 2026-06-11\n"
        "categories:\n"
        "  - weekly-update\n"
        "---\n"
        "\n"
        "Body paragraph.\n"
    )
    meta, body = split_front_matter(text)
    assert meta["title"] == "Hello World"
    assert meta["categories"] == ["weekly-update"]
    assert body.strip() == "Body paragraph."


def test_no_front_matter_returns_empty_meta_and_full_body() -> None:
    text = "Just a body, no fence.\n"
    meta, body = split_front_matter(text)
    assert meta == {}
    assert body == text


def test_unterminated_front_matter_raises() -> None:
    with pytest.raises(ValueError, match="unterminated"):
        split_front_matter("---\ntitle: X\n")


def test_non_mapping_front_matter_raises() -> None:
    with pytest.raises(ValueError, match="mapping"):
        split_front_matter("---\n- a\n- b\n---\nbody\n")
