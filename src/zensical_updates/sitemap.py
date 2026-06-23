"""Build a sitemap for the generated Updates section.

zensical writes a sitemap for the pages in its ``nav`` only, so the generated
posts and taxonomy pages are absent from it. This emits a sitemap covering every
page the build writes, so the section's content is discoverable. The build
records each page's URL as it writes it (``BuildResult.page_urls``) and hands that
list here, so the sitemap lists exactly what was produced. Locations are fully
qualified, because a sitemap is read off-site: each site-absolute path is joined
to the scheme and host of ``site_url``. Output is deterministic, the order follows
the caller and no wall-clock value is written.
"""

from collections.abc import Sequence

import lxml.etree

from zensical_updates.config import Config
from zensical_updates.urls import absolute_url

_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
_SM = f"{{{_NS}}}"


def render_sitemap(site_url: str, paths: Sequence[str]) -> str:
    """Assemble sitemap XML: one ``<url><loc>`` per site-absolute path.

    The schema namespace is the default, so elements carry no prefix. lxml
    assembles and pretty-prints the tree, matching the feed's use of lxml.
    """
    urlset = lxml.etree.Element(_SM + "urlset", nsmap={None: _NS})
    for path in paths:
        url = lxml.etree.SubElement(urlset, _SM + "url")
        loc = lxml.etree.SubElement(url, _SM + "loc")
        loc.text = absolute_url(site_url, path)
    document = lxml.etree.tostring(
        urlset, xml_declaration=True, encoding="utf-8", pretty_print=True
    )
    return document.decode("utf-8")


def build_sitemap(config: Config, page_urls: Sequence[str]) -> str:
    """Render the sitemap XML for the pages the build recorded in ``page_urls``.

    The locations are absolute, so it needs ``config.site_url``; the build calls it
    only when that is set.
    """
    return render_sitemap(config.site_url, page_urls)
