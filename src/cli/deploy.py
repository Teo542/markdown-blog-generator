"""Deploy command for publishing to GitHub Pages."""
import subprocess
import sys
from pathlib import Path


def run_git(args: list[str], cwd: Path) -> bool:
    """Run a git command and return success status."""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: git is not installed or not in PATH")
        return False


def get_remote_url() -> str | None:
    """Get the remote URL from the main repo."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def deploy_to_github_pages(output_dir: Path, build_fn) -> None:
    """Deploy dist/ folder to GitHub Pages (gh-pages branch)."""
    if not output_dir.exists():
        print("Error: Output directory does not exist. Run build first.")
        sys.exit(1)

    remote_url = get_remote_url()
    if not remote_url:
        print("Error: No git remote found. Set up a GitHub repository first.")
        print("  git remote add origin https://github.com/USER/REPO.git")
        sys.exit(1)

    print(f"Deploying to: {remote_url}")
    print("Building site...")
    build_fn()

    git_dir = output_dir / '.git'
    if not git_dir.exists():
        print("Initializing git in dist/...")
        run_git(['init'], output_dir)
        run_git(['checkout', '-b', 'gh-pages'], output_dir)
        run_git(['remote', 'add', 'origin', remote_url], output_dir)

    print("Staging files...")
    run_git(['add', '-A'], output_dir)

    print("Committing...")
    run_git(['commit', '-m', 'Deploy to GitHub Pages'], output_dir)

    print("Pushing to gh-pages branch...")
    success = run_git(['push', '-f', 'origin', 'gh-pages'], output_dir)

    if success:
        repo_name = remote_url.split('/')[-1].replace('.git', '')
        user = remote_url.split('/')[-2]
        if 'github.com' in remote_url:
            print(f"\nDeployed! Your site will be available at:")
            print(f"  https://{user}.github.io/{repo_name}/")
            print("\nNote: Enable GitHub Pages in repo Settings > Pages > gh-pages branch")
    else:
        print("\nPush failed. Check your git credentials and try again.")
        sys.exit(1)
