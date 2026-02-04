import re
from datetime import datetime
from pathlib import Path

import bleach
import markdown
import yaml

from src.models.post import Post

SLUG_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

ALLOWED_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'strong', 'em', 'code', 'pre',
    'blockquote', 'img', 'br', 'hr', 'table', 'thead',
    'tbody', 'tr', 'th', 'td'
]
def filter_url(tag: str, name: str, value: str) -> bool:
    """Only allow safe URL protocols."""
    if name in ('href', 'src'):
        if not value or value.startswith('/') or value.startswith('#'):
            return True
        protocol = value.split(':')[0].lower() if ':' in value else ''
        return protocol in ALLOWED_PROTOCOLS
    return True


ALLOWED_ATTRS = {
    'a': filter_url,
    'img': filter_url,
    'code': ['class'],
    'pre': ['class']
}


def validate_slug(slug: str) -> str:
    """Validate slug contains only safe characters."""
    if not slug or not SLUG_PATTERN.match(slug):
        raise ValueError(f"Invalid slug '{slug}': must be lowercase alphanumeric with hyphens")
    return slug


def estimate_reading_time(content: str, wpm: int = 200) -> int:
    """Estimate reading time in minutes based on word count."""
    words = len(content.split())
    minutes = max(1, round(words / wpm))
    return minutes


def normalize_tags(tags: list) -> list[str]:
    """Normalize tags to lowercase strings."""
    if not tags:
        return []
    return [str(tag).lower().strip() for tag in tags if tag]


def extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and content from markdown text."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, text, re.DOTALL)

    if not match:
        raise ValueError("Invalid frontmatter format")

    frontmatter = yaml.safe_load(match.group(1))
    content = match.group(2)
    return frontmatter, content


def convert_markdown(content: str) -> str:
    """Convert markdown content to sanitized HTML."""
    html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)


def parse_post(filepath: Path) -> Post:
    """Parse a markdown file into a Post object."""
    text = filepath.read_text(encoding='utf-8')
    frontmatter, content = extract_frontmatter(text)

    title = frontmatter.get('title', 'Untitled')
    date_value = frontmatter.get('date')

    if isinstance(date_value, str):
        post_date = datetime.strptime(date_value, '%Y-%m-%d').date()
    else:
        post_date = date_value

    raw_slug = frontmatter.get('slug', filepath.stem)
    slug = validate_slug(raw_slug)
    html_content = convert_markdown(content)

    tags = normalize_tags(frontmatter.get('tags', []))
    draft = not frontmatter.get('publish', True)
    reading_time = estimate_reading_time(content)

    return Post(
        title=title,
        date=post_date,
        slug=slug,
        content=content,
        html_content=html_content,
        tags=tags,
        draft=draft,
        reading_time=reading_time
    )
