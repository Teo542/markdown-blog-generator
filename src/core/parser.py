import re
from datetime import datetime
from pathlib import Path

import markdown
import yaml

from src.models.post import Post


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
    """Convert markdown content to HTML."""
    return markdown.markdown(content, extensions=['fenced_code', 'tables'])


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
