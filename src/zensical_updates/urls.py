"""Build site-absolute URLs for generated pages.

zensical renders a page at its on-disk path under ``docs/`` (``use_directory_urls``
defaults on), so a page at ``docs/<base>/<slug>.md`` lives at ``/<base>/<slug>/``.
Every link the generator emits is one of these directory URLs. They are
site-absolute, which zensical does not validate, so they must be exactly right.
"""

import re
from urllib.parse import urlparse

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Lowercase, collapse runs of non-alphanumerics to ``-``, trim the ends."""
    return _NON_SLUG.sub("-", value.lower()).strip("-")


def post_url(base: str, slug: str) -> str:
    return f"/{base}/{slug}/"


def tag_url(base: str, tag: str) -> str:
    return f"/{base}/tags/{slugify(tag)}/"


def category_url(base: str, category: str) -> str:
    return f"/{base}/categories/{slugify(category)}/"


def index_url(base: str) -> str:
    return f"/{base}/"


def tag_index_url(base: str) -> str:
    return f"/{base}/tags/"


def category_index_url(base: str) -> str:
    return f"/{base}/categories/"


def archive_url(base: str) -> str:
    return f"/{base}/archive/"


def year_url(base: str, year: int) -> str:
    return f"/{base}/archive/{year}/"


def absolute_url(site_url: str, path: str) -> str:
    """Join the scheme and host of ``site_url`` to a site-absolute ``path``.

    Feed links are consumed off-site, so they must be fully qualified. ``path`` is
    a site-absolute path (leading ``/``); only the scheme and host come from
    ``site_url``.
    """
    parts = urlparse(site_url)
    return f"{parts.scheme}://{parts.netloc}{path}"
