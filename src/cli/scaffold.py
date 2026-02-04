"""Scaffold command for creating new posts."""
import re
from datetime import date
from pathlib import Path


def slugify(title: str) -> str:
    """Convert title to URL-friendly slug."""
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def create_post(title: str, content_dir: Path) -> Path:
    """Create a new post file with frontmatter template."""
    slug = slugify(title)
    today = date.today().isoformat()
    filepath = content_dir / f"{slug}.md"

    if filepath.exists():
        raise FileExistsError(f"Post already exists: {filepath}")

    frontmatter = f"""---
title: {title}
date: {today}
slug: {slug}
tags: []
publish: false
---

Write your content here.
"""

    filepath.write_text(frontmatter, encoding='utf-8')
    return filepath
