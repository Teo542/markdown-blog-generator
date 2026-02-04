# Markdown Blog Generator - Project Rules

## Project Status: 95% Complete (Feature Complete)

### Completed
- [x] Core SSG engine (Markdown → HTML)
- [x] Security (XSS, path traversal, URL filtering)
- [x] Dark theme CSS with mobile responsive
- [x] Tags system with individual tag pages
- [x] Archive page (posts grouped by year)
- [x] Pagination
- [x] Reading time estimates
- [x] Draft support (publish: true/false)
- [x] RSS feed generation
- [x] Sitemap.xml generation
- [x] Meta tags (Open Graph, Twitter Cards)
- [x] Client-side search
- [x] About page & 404 page
- [x] Syntax highlighting (Prism.js)
- [x] Social links footer
- [x] README documentation
- [x] CLI commands (build, new, watch, deploy)
- [x] Admin panel (web UI)
- [x] Image upload support

### Not Done (Optional Polish)
- [ ] Test suite
- [ ] Related posts
- [ ] Comments system
- [ ] Analytics placeholder

---

## Quick Reference

### Commands
```bash
python main.py              # Build site
python main.py new "Title"  # Create new post (draft)
python main.py watch        # Auto-rebuild on changes
python main.py deploy       # Push to GitHub Pages
python main.py admin        # Web admin panel (localhost:5000)
```

### Content Format
```yaml
---
title: Post Title
date: 2026-01-01
slug: url-slug
tags: [python, tutorial]
publish: true
---
Markdown content...
```

### Directory Structure
```
content/           # Markdown posts + images/
templates/         # Jinja2 templates
static/css/        # Stylesheets
dist/              # Output (git-ignored)
src/
  core/            # Generator, parser, feed, sitemap
  models/          # Post dataclass
  utils/           # File handling
  cli/             # CLI commands (scaffold, watch, deploy)
  admin/           # Flask admin panel
```

---

## Architecture

```
Input (content/*.md)
    ↓
Parser (YAML frontmatter + Markdown)
    ↓
Generator (Jinja2 templates)
    ↓
Output (dist/*.html + RSS + sitemap + search.json)
```

### Key Files
| File | Purpose |
|------|---------|
| `main.py` | CLI entry point |
| `src/core/generator.py` | Build pipeline |
| `src/core/parser.py` | Markdown + frontmatter parsing |
| `src/admin/app.py` | Flask admin panel |
| `config.yaml` | Site configuration |

---

## Security Reminders
- Slugs: only `a-z0-9` and hyphens (validated)
- HTML: sanitized with bleach whitelist
- URLs: only http/https/mailto protocols
- Server: localhost by default
- No user input goes directly to filesystem paths

---

## Lessons Learned

1. **Users need GUIs** - CLI-only tools feel incomplete; admin panel made it usable
2. **Phased development works** - Core → Features → UX → Polish prevents scope creep
3. **Ship working software** - 90% done and usable beats 100% done never
4. **Windows file locking** - Can't modify files while servers run from them
5. **Static sites are powerful** - No database, no hacking risk, free hosting
