import json
from collections import defaultdict
from pathlib import Path
from typing import Callable

import markdown
from jinja2 import Environment, FileSystemLoader

from src.core.feed import generate_rss
from src.core.sitemap import generate_sitemap
from src.models.post import Post
from src.utils import file_handler


class Generator:
    def __init__(
        self,
        config: dict,
        parse_post: Callable[[Path], Post],
        file_ops: object = file_handler
    ):
        self.config = config
        self.parse_post = parse_post
        self.file_ops = file_ops

        self.content_dir = Path(config['content_dir'])
        self.output_dir = Path(config['output_dir'])
        self.static_dir = Path(config['static_dir'])
        self.templates_dir = Path(config['templates_dir'])
        self.posts_per_page = config.get('posts_per_page', 10)

        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )

    def _base_context(self) -> dict:
        """Return common template context."""
        return {
            'site_name': self.config.get('site_name', 'My Blog'),
            'site_description': self.config.get('site_description', ''),
            'base_url': self.config.get('base_url', '/'),
            'author': self.config.get('author', ''),
            'twitter_handle': self.config.get('twitter_handle', ''),
            'github_handle': self.config.get('github_handle', ''),
        }

    def build(self) -> None:
        """Main build pipeline."""
        self.file_ops.clean_directory(self.output_dir)

        all_posts = self._load_posts()
        posts = [p for p in all_posts if not p.draft]
        posts = sorted(posts, key=lambda p: p.date, reverse=True)

        self._render_posts(posts)
        self._render_paginated_index(posts)
        self._render_archive(posts)
        all_tags = self._render_tag_pages(posts)
        self._render_static_pages()
        self._generate_feed(posts)
        self._generate_sitemap(posts, all_tags)
        self._generate_search_index(posts)
        self._copy_assets()

        draft_count = len(all_posts) - len(posts)
        print(f"Built {len(posts)} posts to {self.output_dir}/")
        if draft_count:
            print(f"  ({draft_count} drafts skipped)")

    def _load_posts(self) -> list[Post]:
        """Load and parse all markdown files (excluding pages like about.md)."""
        posts = []
        md_files = self.file_ops.list_markdown_files(self.content_dir)
        page_files = {'about.md'}

        for filepath in md_files:
            if filepath.name in page_files:
                continue
            try:
                post = self.parse_post(filepath)
                posts.append(post)
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

        return posts

    def _render_posts(self, posts: list[Post]) -> None:
        """Render individual post pages."""
        template = self.env.get_template('post.html')

        for post in posts:
            context = self._base_context()
            context['post'] = post
            html = template.render(**context)
            output_path = self.output_dir / f"{post.slug}.html"
            self.file_ops.write_file(output_path, html)

    def _render_paginated_index(self, posts: list[Post]) -> None:
        """Render paginated index pages."""
        template = self.env.get_template('index.html')
        pages = self._paginate(posts, self.posts_per_page)

        for i, page_posts in enumerate(pages):
            page_num = i + 1
            context = self._base_context()
            context.update({
                'posts': page_posts,
                'current_page': page_num,
                'total_pages': len(pages),
                'has_previous': page_num > 1,
                'has_next': page_num < len(pages)
            })
            html = template.render(**context)
            if page_num == 1:
                output_path = self.output_dir / 'index.html'
            else:
                page_dir = self.output_dir / 'page'
                page_dir.mkdir(exist_ok=True)
                output_path = page_dir / f"{page_num}.html"
            self.file_ops.write_file(output_path, html)

    def _render_archive(self, posts: list[Post]) -> None:
        """Render archive page grouped by year."""
        template = self.env.get_template('archive.html')
        grouped = defaultdict(list)

        for post in posts:
            grouped[post.date.year].append(post)

        years = sorted(grouped.keys(), reverse=True)
        context = self._base_context()
        context.update({'years': years, 'posts_by_year': grouped})
        html = template.render(**context)
        output_path = self.output_dir / 'archive.html'
        self.file_ops.write_file(output_path, html)

    def _render_tag_pages(self, posts: list[Post]) -> list[str]:
        """Render tag listing and individual tag pages."""
        tag_posts = defaultdict(list)
        for post in posts:
            for tag in post.tags:
                tag_posts[tag].append(post)

        self._render_tags_index(tag_posts)
        self._render_individual_tags(tag_posts)
        return list(tag_posts.keys())

    def _render_tags_index(self, tag_posts: dict) -> None:
        """Render main tags page with counts."""
        template = self.env.get_template('tags.html')
        tags = sorted(tag_posts.keys())
        tag_counts = {tag: len(posts) for tag, posts in tag_posts.items()}

        context = self._base_context()
        context.update({'tags': tags, 'tag_counts': tag_counts})
        html = template.render(**context)
        output_path = self.output_dir / 'tags.html'
        self.file_ops.write_file(output_path, html)

    def _render_individual_tags(self, tag_posts: dict) -> None:
        """Render individual tag pages."""
        template = self.env.get_template('tag.html')
        tag_dir = self.output_dir / 'tag'
        tag_dir.mkdir(exist_ok=True)

        for tag, posts in tag_posts.items():
            context = self._base_context()
            context.update({'tag': tag, 'posts': posts})
            html = template.render(**context)
            output_path = tag_dir / f"{tag}.html"
            self.file_ops.write_file(output_path, html)

    def _paginate(self, items: list, per_page: int) -> list[list]:
        """Split items into pages."""
        if not items:
            return [[]]
        return [items[i:i + per_page] for i in range(0, len(items), per_page)]

    def _render_static_pages(self) -> None:
        """Render static pages like About and 404."""
        self._render_about()
        self._render_404()

    def _render_about(self) -> None:
        """Render about page from about.md."""
        about_path = self.content_dir / 'about.md'
        if not about_path.exists():
            return

        text = about_path.read_text(encoding='utf-8')
        parts = text.split('---', 2)
        content = parts[2].strip() if len(parts) > 2 else text
        html_content = markdown.markdown(content)

        template = self.env.get_template('about.html')
        context = self._base_context()
        context['content'] = html_content
        html = template.render(**context)
        output_path = self.output_dir / 'about.html'
        self.file_ops.write_file(output_path, html)

    def _render_404(self) -> None:
        """Render 404 error page."""
        template = self.env.get_template('404.html')
        context = self._base_context()
        html = template.render(**context)
        output_path = self.output_dir / '404.html'
        self.file_ops.write_file(output_path, html)

    def _generate_feed(self, posts: list[Post]) -> None:
        """Generate RSS feed and styled RSS page."""
        rss_content = generate_rss(posts, self.config)
        output_path = self.output_dir / 'feed.xml'
        self.file_ops.write_file(output_path, rss_content)

        template = self.env.get_template('rss.html')
        context = self._base_context()
        context['posts'] = posts
        html = template.render(**context)
        rss_page_path = self.output_dir / 'rss.html'
        self.file_ops.write_file(rss_page_path, html)

    def _generate_sitemap(self, posts: list[Post], tags: list[str]) -> None:
        """Generate sitemap.xml."""
        sitemap_content = generate_sitemap(posts, tags, self.config)
        output_path = self.output_dir / 'sitemap.xml'
        self.file_ops.write_file(output_path, sitemap_content)

    def _generate_search_index(self, posts: list[Post]) -> None:
        """Generate search index JSON for client-side search."""
        index = []
        for post in posts:
            index.append({
                'title': post.title,
                'slug': post.slug,
                'date': str(post.date),
                'tags': post.tags,
                'excerpt': post.content[:200].replace('\n', ' ')
            })
        output_path = self.output_dir / 'search.json'
        self.file_ops.write_file(output_path, json.dumps(index))

    def _copy_assets(self) -> None:
        """Copy static assets and images to output directory."""
        self.file_ops.copy_static_assets(self.static_dir, self.output_dir)
        self.file_ops.copy_images(self.content_dir, self.output_dir)
