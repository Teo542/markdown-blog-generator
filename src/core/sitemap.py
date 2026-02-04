from xml.etree.ElementTree import Element, SubElement, tostring

from src.models.post import Post


def generate_sitemap(posts: list[Post], tags: list[str], config: dict) -> str:
    """Generate sitemap.xml for search engines."""
    base_url = config.get('base_url', '/')

    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

    _add_url(urlset, base_url, 'index.html', '1.0', 'daily')
    _add_url(urlset, base_url, 'archive.html', '0.8', 'weekly')
    _add_url(urlset, base_url, 'tags.html', '0.7', 'weekly')

    for post in posts:
        _add_url(urlset, base_url, f"{post.slug}.html", '0.9', 'monthly')

    for tag in tags:
        _add_url(urlset, base_url, f"tag/{tag}.html", '0.6', 'weekly')

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return xml_declaration + tostring(urlset, encoding='unicode')


def _add_url(parent: Element, base: str, path: str, priority: str, freq: str):
    """Add a URL entry to the sitemap."""
    url = SubElement(parent, 'url')
    SubElement(url, 'loc').text = f"{base}{path}"
    SubElement(url, 'changefreq').text = freq
    SubElement(url, 'priority').text = priority
