"""Flask admin panel for managing blog posts."""
import os
import re
from datetime import date
from pathlib import Path

import markdown
import yaml
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename


def create_app(config: dict, build_fn, deploy_fn):
    """Create and configure the Flask admin app."""
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / 'templates'),
        static_folder=str(Path(__file__).parent / 'static')
    )
    app.secret_key = 'dev-secret-key'

    content_dir = Path(config['content_dir'])
    images_dir = content_dir / 'images'

    def get_all_posts():
        """Load all posts from content directory."""
        posts = []
        for filepath in sorted(content_dir.glob('*.md'), reverse=True):
            if filepath.name == 'about.md':
                continue
            try:
                text = filepath.read_text(encoding='utf-8')
                if text.startswith('---'):
                    parts = text.split('---', 2)
                    if len(parts) >= 3:
                        fm = yaml.safe_load(parts[1])
                        posts.append({
                            'title': fm.get('title', 'Untitled'),
                            'slug': fm.get('slug', filepath.stem),
                            'date': fm.get('date', date.today()),
                            'tags': fm.get('tags', []),
                            'draft': not fm.get('publish', True),
                            'filename': filepath.name
                        })
            except Exception:
                continue
        return sorted(posts, key=lambda p: p['date'], reverse=True)

    def get_post(slug: str):
        """Load a single post by slug."""
        for filepath in content_dir.glob('*.md'):
            text = filepath.read_text(encoding='utf-8')
            if text.startswith('---'):
                parts = text.split('---', 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if fm.get('slug') == slug:
                        return {
                            'title': fm.get('title', ''),
                            'slug': fm.get('slug', ''),
                            'date': fm.get('date', date.today()),
                            'tags': fm.get('tags', []),
                            'publish': fm.get('publish', True),
                            'content': parts[2].strip(),
                            'filepath': filepath
                        }
        return None

    def slugify(title: str) -> str:
        """Convert title to URL-friendly slug."""
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')

    def save_post(title, slug, post_date, tags, content, publish):
        """Save post to markdown file."""
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        frontmatter = {
            'title': title,
            'date': post_date,
            'slug': slug,
            'tags': tags,
            'publish': publish
        }

        md_content = f"""---
title: {title}
date: {post_date}
slug: {slug}
tags: {tags}
publish: {str(publish).lower()}
---

{content}
"""
        filepath = content_dir / f"{slug}.md"
        filepath.write_text(md_content, encoding='utf-8')
        return filepath

    @app.route('/')
    def dashboard():
        """Show all posts."""
        posts = get_all_posts()
        return render_template('dashboard.html', posts=posts)

    @app.route('/new', methods=['GET', 'POST'])
    def new_post():
        """Create a new post."""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip() or slugify(title)
            post_date = request.form.get('date', str(date.today()))
            tags = request.form.get('tags', '')
            content = request.form.get('content', '')
            publish = request.form.get('publish') == 'on'

            save_post(title, slug, post_date, tags, content, publish)
            return redirect(url_for('dashboard'))

        return render_template('editor.html', post=None, today=str(date.today()))

    @app.route('/edit/<slug>', methods=['GET', 'POST'])
    def edit_post(slug):
        """Edit an existing post."""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            new_slug = request.form.get('slug', '').strip() or slug
            post_date = request.form.get('date', str(date.today()))
            tags = request.form.get('tags', '')
            content = request.form.get('content', '')
            publish = request.form.get('publish') == 'on'

            old_post = get_post(slug)
            if old_post and old_post['filepath'].exists():
                if new_slug != slug:
                    old_post['filepath'].unlink()

            save_post(title, new_slug, post_date, tags, content, publish)
            return redirect(url_for('dashboard'))

        post = get_post(slug)
        if not post:
            return redirect(url_for('dashboard'))

        if isinstance(post['tags'], list):
            post['tags_str'] = ', '.join(post['tags'])
        else:
            post['tags_str'] = post['tags']

        return render_template('editor.html', post=post, today=str(date.today()))

    @app.route('/delete/<slug>', methods=['POST'])
    def delete_post(slug):
        """Delete a post."""
        post = get_post(slug)
        if post and post['filepath'].exists():
            post['filepath'].unlink()
        return redirect(url_for('dashboard'))

    @app.route('/upload', methods=['POST'])
    def upload_image():
        """Handle image upload."""
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        images_dir.mkdir(parents=True, exist_ok=True)
        filename = secure_filename(file.filename)
        filepath = images_dir / filename
        file.save(str(filepath))

        markdown_syntax = f'![{filename}](/images/{filename})'
        return jsonify({'markdown': markdown_syntax, 'path': f'/images/{filename}'})

    @app.route('/preview', methods=['POST'])
    def preview():
        """Render markdown preview."""
        content = request.form.get('content', '')
        html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        return html

    @app.route('/build', methods=['POST'])
    def build():
        """Trigger site build."""
        try:
            build_fn()
            return jsonify({'success': True, 'message': 'Build complete!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/deploy', methods=['POST'])
    def deploy():
        """Trigger deployment."""
        try:
            deploy_fn()
            return jsonify({'success': True, 'message': 'Deployed!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    return app


def run_admin(config: dict, build_fn, deploy_fn):
    """Start the admin server."""
    app = create_app(config, build_fn, deploy_fn)
    print("Admin panel running at http://localhost:5000")
    print("Press Ctrl+C to stop.")
    app.run(host='127.0.0.1', port=5000, debug=False)
