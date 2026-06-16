"""Generate a dated Updates (blog) section for zensical sites as plain Markdown.

The public API is re-exported here from the private `_core` module and listed in
`__all__` — listing names in `__all__` is what marks them as the supported,
explicitly re-exported surface for type checkers (mypy `strict` / basedpyright)
and the autodoc tooling.
"""

from __future__ import annotations

from zensical_updates._core import Greeter, greet

__version__ = "0.1.0"

__all__ = ["Greeter", "greet"]
