# Markdown Blog Generator - Project Rules

## Project Status: ~50% Complete

### Done
- [x] Core SSG engine (Markdown → HTML)
- [x] Security (XSS, path traversal, URL filtering)
- [x] Dark theme CSS with mobile responsive
- [x] Development server

### Not Done
- [ ] Real blog features (see Roadmap below)

---

## Quick Reference

### Commands
```bash
python main.py          # Build site to dist/
python serve.py         # Dev server at localhost:8000
python serve.py --network  # Mobile testing
```

### Content Format
```yaml
---
title: Post Title
date: 2026-01-01
slug: url-slug
---
Markdown content...
```

### Directory Structure
```
content/        # Markdown posts
templates/      # Jinja2 (base, index, post)
static/css/     # Stylesheets
dist/           # Output (git-ignored)
src/core/       # Parser, Generator
src/models/     # Post dataclass
src/utils/      # File handling
```

---

## Roadmap

### Phase 1: Core Blog Features (High Priority)
- [ ] Categories/tags system
- [ ] Archive page (posts by date)
- [ ] Pagination
- [ ] Reading time estimate
- [ ] Draft support (publish: true/false)

### Phase 2: Discovery & SEO (High Priority)
- [ ] RSS/Atom feed
- [ ] sitemap.xml
- [ ] Meta tags (og:image, twitter:card)
- [ ] Search (client-side)

### Phase 3: Content & Templates (Medium Priority)
- [ ] About page
- [ ] 404 page
- [ ] Navigation menu
- [ ] Social links footer
- [ ] Code syntax highlighting

### Phase 4: User Workflow (Medium Priority)
- [ ] README documentation
- [ ] Post scaffold command
- [ ] Watch mode (auto-rebuild)

### Phase 5: Polish (Low Priority)
- [ ] Test suite
- [ ] Related posts
- [ ] Comments system
- [ ] Analytics placeholder

---

## Files to Create
- `src/core/feed.py` - RSS generation
- `src/core/sitemap.py` - Sitemap generation
- `templates/archive.html`
- `templates/category.html`
- `templates/404.html`

## Files to Modify
- `src/models/post.py` - Add tags, category, draft, reading_time
- `src/core/parser.py` - Parse new frontmatter
- `src/core/generator.py` - Generate feeds, sitemap, archives
- `templates/base.html` - Nav, meta tags
- `config.yaml` - Social links, posts_per_page

---

## Security Reminders
- Slugs: only `a-z0-9` and hyphens
- HTML: sanitized with bleach whitelist
- URLs: only http/https/mailto protocols
- Server: localhost by default
