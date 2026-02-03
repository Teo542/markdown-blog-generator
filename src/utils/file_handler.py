import shutil
from pathlib import Path


def validate_path(path: Path, base: Path) -> bool:
    """Check if path is within the base directory (prevents traversal)."""
    try:
        resolved = path.resolve()
        base_resolved = base.resolve()
        return resolved.is_relative_to(base_resolved)
    except (ValueError, OSError):
        return False


def clean_directory(path: Path) -> None:
    """Remove all contents of a directory."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_static_assets(src: Path, dest: Path) -> None:
    """Copy static assets from source to destination (skips symlinks)."""
    if not src.exists():
        return

    for item in src.iterdir():
        if item.is_symlink():
            continue
        if not validate_path(item, src):
            continue

        dest_path = dest / item.name
        if item.is_dir():
            shutil.copytree(item, dest_path, symlinks=False)
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)


def write_file(path: Path, content: str) -> None:
    """Write content to a file, creating directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def read_file(path: Path) -> str:
    """Read content from a file."""
    return path.read_text(encoding='utf-8')


def list_markdown_files(path: Path) -> list[Path]:
    """List all markdown files in a directory."""
    if not path.exists():
        return []
    return sorted(path.glob('*.md'))
