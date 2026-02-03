import re
from datetime import datetime
from pathlib import Path

import bleach
import markdown
import yaml

from src.models.post import Post

ALLOWED_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'strong', 'em', 'code', 'pre',
    'blockquote', 'img', 'br', 'hr', 'table', 'thead',
    'tbody', 'tr', 'th', 'td'
]
ALLOWED_ATTRS = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'pre': ['class']
}


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

    slug = frontmatter.get('slug', filepath.stem)
    html_content = convert_markdown(content)

    return Post(
        title=title,
        date=post_date,
        slug=slug,
        content=content,
        html_content=html_content
    )
