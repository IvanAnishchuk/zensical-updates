"""Generate a dated Updates (blog) section for zensical sites as plain Markdown.

The public API is re-exported here and listed in `__all__` — listing names in
`__all__` is what marks them as the supported, explicitly re-exported surface for
type checkers (mypy `strict` / basedpyright) and the autodoc tooling.
"""

from __future__ import annotations

from zensical_updates.build import BuildResult, build_site, clean_site
from zensical_updates.config import Config, load_config
from zensical_updates.model import Post, PostError, discover_posts, load_post

__version__ = "0.1.0"

__all__ = [
    "BuildResult",
    "Config",
    "Post",
    "PostError",
    "build_site",
    "clean_site",
    "discover_posts",
    "load_config",
    "load_post",
]
