# Markdown Blog Generator

A clean code static site generator that converts Markdown files with YAML frontmatter into a static HTML website.

## Project Structure

```
/src
  /core       - Parser and generator engine
  /models     - Data models (Post)
  /utils      - File handling utilities
/templates    - Jinja2 HTML templates
/content      - Markdown source files
/static       - CSS, images, assets
/dist         - Generated output (git-ignored)
```

## Usage

```bash
python main.py
```

## Requirements

- Python 3.10+
- See requirements.txt for dependencies
