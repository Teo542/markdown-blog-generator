from pathlib import Path
from typing import Callable

from jinja2 import Environment, FileSystemLoader

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

        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )

    def build(self) -> None:
        """Main build pipeline: read -> parse -> sort -> render."""
        self.file_ops.clean_directory(self.output_dir)

        posts = self._load_posts()
        posts = sorted(posts, key=lambda p: p.date, reverse=True)

        self._render_posts(posts)
        self._render_index(posts)
        self._copy_assets()

        print(f"Built {len(posts)} posts to {self.output_dir}/")

    def _load_posts(self) -> list[Post]:
        """Load and parse all markdown files."""
        posts = []
        md_files = self.file_ops.list_markdown_files(self.content_dir)

        for filepath in md_files:
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
            html = template.render(
                post=post,
                site_name=self.config['site_name']
            )
            output_path = self.output_dir / f"{post.slug}.html"
            self.file_ops.write_file(output_path, html)

    def _render_index(self, posts: list[Post]) -> None:
        """Render the homepage with post listing."""
        template = self.env.get_template('index.html')
        html = template.render(
            posts=posts,
            site_name=self.config['site_name']
        )
        output_path = self.output_dir / 'index.html'
        self.file_ops.write_file(output_path, html)

    def _copy_assets(self) -> None:
        """Copy static assets to output directory."""
        self.file_ops.copy_static_assets(self.static_dir, self.output_dir)
