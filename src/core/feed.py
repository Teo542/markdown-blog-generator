from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

from src.models.post import Post


def generate_rss(posts: list[Post], config: dict) -> str:
    """Generate RSS 2.0 feed XML."""
    site_name = config.get('site_name', 'My Blog')
    base_url = config.get('base_url', '/')
    site_description = config.get('site_description', 'A blog')

    rss = Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = site_name
    SubElement(channel, 'link').text = base_url
    SubElement(channel, 'description').text = site_description
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = _format_rfc822(datetime.now())

    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', f"{base_url}feed.xml")
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    for post in posts[:20]:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post.title
        SubElement(item, 'link').text = f"{base_url}{post.slug}.html"
        SubElement(item, 'guid').text = f"{base_url}{post.slug}.html"
        SubElement(item, 'pubDate').text = _format_rfc822_date(post.date)
        SubElement(item, 'description').text = _get_excerpt(post.content)

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return xml_declaration + tostring(rss, encoding='unicode')


def _format_rfc822(dt: datetime) -> str:
    """Format datetime as RFC 822 string."""
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')


def _format_rfc822_date(d) -> str:
    """Format date as RFC 822 string."""
    dt = datetime.combine(d, datetime.min.time())
    return _format_rfc822(dt)


def _get_excerpt(content: str, max_length: int = 200) -> str:
    """Get excerpt from markdown content."""
    text = content.replace('#', '').replace('*', '').replace('`', '')
    text = ' '.join(text.split())
    if len(text) > max_length:
        return text[:max_length].rsplit(' ', 1)[0] + '...'
    return text
