from __future__ import annotations

import markdown
import nh3

_ALLOWED_TAGS = {
    'p',
    'br',
    'strong',
    'em',
    'a',
    'ul',
    'ol',
    'li',
    'blockquote',
    'code',
    'pre',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'hr',
    'img',
}
_ALLOWED_ATTRIBUTES = {
    'a': {'href', 'title'},
    'img': {'src', 'alt', 'title'},
}


def render_markdown_to_html(markdown_text: str) -> str:
    """Render Markdown to sanitized HTML safe for template |safe rendering."""
    raw_html = markdown.markdown(
        markdown_text or '', extensions=['fenced_code', 'tables']
    )
    return nh3.clean(
        raw_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        link_rel='nofollow noopener noreferrer',
    )
