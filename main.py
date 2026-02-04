"""CLI entry point for the Markdown Blog Generator."""
import argparse
import sys
from pathlib import Path

import yaml

from src.core.generator import Generator
from src.core.parser import parse_post
from src.cli.scaffold import create_post
from src.cli.watch import start_watch
from src.cli.deploy import deploy_to_github_pages
from src.admin.app import run_admin


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def cmd_build(config: dict) -> None:
    """Build the static site."""
    generator = Generator(config=config, parse_post=parse_post)
    generator.build()


def cmd_new(config: dict, title: str) -> None:
    """Create a new post."""
    content_dir = Path(config['content_dir'])
    filepath = create_post(title, content_dir)
    print(f"Created: {filepath}")


def cmd_watch(config: dict) -> None:
    """Watch for changes and auto-rebuild."""
    def build_fn():
        generator = Generator(config=config, parse_post=parse_post)
        generator.build()

    print("Initial build...")
    build_fn()
    start_watch(config, build_fn)


def cmd_deploy(config: dict) -> None:
    """Deploy to GitHub Pages."""
    def build_fn():
        generator = Generator(config=config, parse_post=parse_post)
        generator.build()

    output_dir = Path(config['output_dir'])
    deploy_to_github_pages(output_dir, build_fn)


def cmd_admin(config: dict) -> None:
    """Start the admin panel."""
    def build_fn():
        generator = Generator(config=config, parse_post=parse_post)
        generator.build()

    def deploy_fn():
        output_dir = Path(config['output_dir'])
        deploy_to_github_pages(output_dir, build_fn)

    run_admin(config, build_fn, deploy_fn)


def main() -> None:
    """Entry point for the blog generator."""
    parser = argparse.ArgumentParser(
        description='Markdown Blog Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command')

    # Build command (default)
    subparsers.add_parser('build', help='Build the static site')

    # New post command
    new_parser = subparsers.add_parser('new', help='Create a new post')
    new_parser.add_argument('title', help='Post title')

    # Watch command
    subparsers.add_parser('watch', help='Watch for changes and auto-rebuild')

    # Deploy command
    subparsers.add_parser('deploy', help='Deploy to GitHub Pages')

    # Admin command
    subparsers.add_parser('admin', help='Start the admin panel')

    args = parser.parse_args()

    try:
        config = load_config(Path('config.yaml'))

        if args.command == 'new':
            cmd_new(config, args.title)
        elif args.command == 'watch':
            cmd_watch(config)
        elif args.command == 'deploy':
            cmd_deploy(config)
        elif args.command == 'admin':
            cmd_admin(config)
        else:
            cmd_build(config)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
