import sys
from pathlib import Path

import yaml

from src.core.generator import Generator
from src.core.parser import parse_post


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main() -> None:
    """Entry point for the blog generator."""
    try:
        config = load_config(Path('config.yaml'))
        generator = Generator(config=config, parse_post=parse_post)
        generator.build()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
