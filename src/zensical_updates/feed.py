"""Build a standards-compliant RSS 2.0 feed for the Updates section.

The feed reuses zensical's own renderer so item HTML matches the rendered site,
then absolutizes in-body links because the feed is read off-site. feedgen
assembles the XML. Output is deterministic: every date is set explicitly, so no
wall-clock value leaks in.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import lxml.html

from zensical_updates.urls import absolute_url, post_url

_zensical_parse_config: Any | None = None
_zensical_render: Any | None = None
try:
    from zensical.config import parse_config as _zensical_parse_config
    from zensical.markdown.render import render as _zensical_render
except ImportError:  # pragma: no cover - zensical is a pinned dep; this guards an API move
    pass

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from zensical_updates.config import Config
    from zensical_updates.model import Post


class FeedError(RuntimeError):
    """The feed could not be generated (e.g. the zensical render API moved)."""


def _inner_html(element: Any) -> str:
    parts = [element.text or ""]
    parts += [lxml.html.tostring(child, encoding="unicode") for child in element]
    return "".join(parts)


def absolutize_html(html: str, base_url: str) -> str:
    """Resolve every in-body link and image against ``base_url``.

    zensical renders page-relative links (``../other/``); a feed read off-site
    needs absolute ones. A leading ``<h1>`` is dropped so the body does not repeat
    the item title.
    """
    if not html.strip():
        return ""
    fragment = lxml.html.fragment_fromstring(html, create_parent=True)
    if len(fragment) and fragment[0].tag == "h1" and not (fragment.text or "").strip():
        heading = fragment[0]
        if heading.tail:  # keep any text that followed the heading
            fragment.text = (fragment.text or "") + heading.tail
        fragment.remove(heading)
    fragment.make_links_absolute(base_url, resolve_base_href=False)
    return _inner_html(fragment).strip()


def _to_datetime(day: datetime.date) -> datetime.datetime:
    return datetime.datetime(day.year, day.month, day.day, tzinfo=datetime.UTC)


def build_feed(config: Config, posts: Sequence[Post], render: Callable[[Post], str]) -> str:
    """Assemble the RSS 2.0 feed XML from ``posts``, newest first.

    ``render`` turns a post into absolutized HTML; it is injected so tests can
    stub it without driving zensical. ``posts`` is already capped and ordered by
    the caller.
    """
    from feedgen.feed import FeedGenerator  # noqa: PLC0415

    generator = FeedGenerator()
    index_url = absolute_url(config.site_url, f"/{config.url_base}/")
    feed_url = absolute_url(config.site_url, f"/{config.url_base}/feed.xml")
    generator.title(config.site_name or config.base)
    # feedgen renders the RSS channel <link> from the last link() call, so the
    # self link goes first and the index (alternate) last, leaving <link> on the
    # index. The self link still emits its <atom:link rel="self">.
    generator.link(href=feed_url, rel="self")
    generator.link(href=index_url, rel="alternate")
    generator.description(config.site_description or config.site_name or config.base)
    generator.language(config.language or "en")
    generator.generator("zensical-updates")
    if posts:
        generator.lastBuildDate(_to_datetime(posts[0].date))

    for post in reversed(list(posts)):
        post_abs = absolute_url(config.site_url, post_url(config.url_base, post.slug))
        entry = generator.add_entry()
        entry.guid(post_abs, permalink=True)
        entry.title(post.title)
        entry.link(href=post_abs)
        entry.pubDate(_to_datetime(post.date))
        # The short excerpt goes in <description>; the full rendered HTML goes in
        # <content:encoded>. feedgen emits both elements when description and content
        # are set, and declares xmlns:content on the channel. lxml splits any literal
        # "]]>" in the content so the CDATA stays well-formed. Without a non-blank
        # excerpt there is no summary, so feedgen carries the full HTML in
        # <description> instead.
        if post.excerpt and post.excerpt.strip():
            entry.description(post.excerpt.strip())
        entry.content(render(post), type="CDATA")

    return str(generator.rss_str(pretty=True).decode("utf-8"))


_SUPPORTED_ZENSICAL = "zensical >=0.0.45,<0.1.0"


def make_renderer(root: Path, config: Config) -> Callable[[Post], str]:
    """Return a callable that renders a post to absolutized HTML via zensical.

    Initializes zensical's config once, then renders each post the same way the
    site does. The render API is internal to zensical, so failures raise a clear
    ``FeedError`` naming the supported version range.
    """
    if _zensical_render is None or _zensical_parse_config is None:
        msg = f"the RSS feed needs {_SUPPORTED_ZENSICAL} installed"
        raise FeedError(msg)
    toml_path = root / "zensical.toml"
    if not toml_path.exists():
        msg = f"the RSS feed needs {toml_path} (zensical reads it to render posts)"
        raise FeedError(msg)
    parse_config = _zensical_parse_config
    render_markdown = _zensical_render
    parse_config(str(toml_path))

    def render(post: Post) -> str:
        url = f"{config.base}/{post.slug}/"
        path = f"{config.base}/{post.slug}.md"
        try:
            html = render_markdown(post.body, path, url)["content"]
        except Exception as exc:  # broad except: wrap any internal-API failure
            msg = f"zensical render failed (supported: {_SUPPORTED_ZENSICAL}): {exc}"
            raise FeedError(msg) from exc
        post_abs = absolute_url(config.site_url, post_url(config.url_base, post.slug))
        return absolutize_html(html, post_abs)

    return render
