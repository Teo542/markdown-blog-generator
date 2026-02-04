"""Watch mode for auto-rebuilding on content changes."""
import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object


class RebuildHandler(FileSystemEventHandler):
    """Handler that triggers rebuild on file changes."""

    def __init__(self, build_fn, extensions: tuple = ('.md', '.html', '.css')):
        self.build_fn = build_fn
        self.extensions = extensions
        self.last_build = 0
        self.debounce_seconds = 1

    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(self.extensions):
            return
        self._trigger_build(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(self.extensions):
            return
        self._trigger_build(event.src_path)

    def _trigger_build(self, path: str):
        now = time.time()
        if now - self.last_build < self.debounce_seconds:
            return
        self.last_build = now
        print(f"\nChange detected: {path}")
        try:
            self.build_fn()
        except Exception as e:
            print(f"Build error: {e}")


def start_watch(config: dict, build_fn) -> None:
    """Start watching for file changes."""
    if not WATCHDOG_AVAILABLE:
        print("Watch mode requires 'watchdog' package.")
        print("Install it with: pip install watchdog")
        sys.exit(1)

    content_dir = Path(config['content_dir'])
    templates_dir = Path(config['templates_dir'])
    static_dir = Path(config['static_dir'])

    handler = RebuildHandler(build_fn)
    observer = Observer()

    for watch_dir in [content_dir, templates_dir, static_dir]:
        if watch_dir.exists():
            observer.schedule(handler, str(watch_dir), recursive=True)
            print(f"Watching: {watch_dir}/")

    print("\nPress Ctrl+C to stop.\n")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")

    observer.join()
