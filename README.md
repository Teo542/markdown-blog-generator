# Markdown Blog Generator

A static site generator that transforms Markdown files into a professional blog.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Build the site
python main.py

# Preview locally
python -m http.server 8000 -d dist
```

Visit `http://localhost:8000` to view your blog.

## CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py` | Build the site |
| `python main.py new "Post Title"` | Create a new draft post |
| `python main.py watch` | Watch files and auto-rebuild |
| `python main.py deploy` | Deploy to GitHub Pages |

## Configuration

Edit `config.yaml` to customize your blog:

```yaml
site_name: "My Blog"           # Blog title
site_description: "..."        # Meta description for SEO
base_url: "/"                  # Base URL for links
author: "Your Name"            # Author name
twitter_handle: ""             # Twitter username (without @)
github_handle: ""              # GitHub username

content_dir: "content"         # Markdown files location
output_dir: "dist"             # Generated HTML output
static_dir: "static"           # CSS, images, etc.
templates_dir: "templates"     # Jinja2 templates

posts_per_page: 10             # Posts shown per page
reading_time_wpm: 200          # Words per minute for reading time
```

## Creating Posts

Create a new `.md` file in the `content/` directory:

```markdown
---
title: My First Post
date: 2026-02-03
slug: my-first-post
tags: [python, tutorial]
publish: true
---

Your content here in Markdown format.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Post title |
| `date` | Yes | Publication date (YYYY-MM-DD) |
| `slug` | Yes | URL-friendly identifier |
| `tags` | No | List of tags |
| `publish` | No | Set to `false` to make it a draft |

## Adding Images

Place images in `content/images/` and reference them in posts:

```markdown
![Alt text](/images/my-photo.jpg)
```

Images are automatically copied to `dist/images/` during build.

## Project Structure

```
├── content/           # Markdown posts and pages
│   ├── about.md       # About page
│   ├── images/        # Your images (copied to dist/)
│   └── *.md           # Blog posts
├── static/
│   └── css/style.css  # Stylesheet
├── templates/         # Jinja2 templates
│   ├── base.html      # Base layout
│   ├── index.html     # Home page
│   ├── post.html      # Single post
│   ├── archive.html   # Post archive
│   ├── tags.html      # Tags listing
│   ├── tag.html       # Single tag page
│   ├── about.html     # About page
│   └── 404.html       # Error page
├── dist/              # Generated output (gitignored)
├── config.yaml        # Site configuration
├── main.py            # CLI entry point
└── src/               # Source code
    ├── core/          # Generator, parser, feed, sitemap
    ├── models/        # Post dataclass
    └── utils/         # File handling utilities
```

## Features

- Dark theme with responsive design
- Paginated index with reading time
- Archive page grouped by year
- Tag system with individual tag pages
- RSS feed (`/feed.xml`)
- Sitemap for SEO (`/sitemap.xml`)
- Client-side search
- Syntax highlighting with Prism.js
- Draft support (`publish: false`)

## Requirements

- Python 3.10+
- See requirements.txt for dependencies

## License

MIT
