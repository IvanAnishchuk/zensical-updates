"""Parse YAML front matter out of a Markdown post.

A post opens with a ``---`` fence, a YAML mapping, and a closing ``---`` fence,
then the Markdown body. The authoring convention requires block-style lists
(``categories:\\n  - weekly-update``); a flow list (``[weekly-update]``) breaks
zensical's strict build, so we never emit one, and posts must not carry one.
"""

from __future__ import annotations

from typing import Any

import yaml

_FENCE = "---"


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split a document into its front-matter mapping and the body.

    Returns ``({}, text)`` when there is no opening fence. Raises ``ValueError``
    on an unterminated fence or front matter that is not a mapping.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != _FENCE:
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == _FENCE:
            block = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            meta = yaml.safe_load(block) or {}
            if not isinstance(meta, dict):
                msg = "front matter must be a mapping"
                raise ValueError(msg)
            return meta, body
    msg = "unterminated front matter (missing closing '---')"
    raise ValueError(msg)
