"""Git workspace manager for branch creation, committing, and push operations."""

import subprocess
from pathlib import Path
from typing import List, Optional
from aicoop.utils.logger import logger


class GitError(Exception):
    """Base exception for Git operations."""
    pass


class GitManager:
    """Manages Git operations on a local repository."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
        if not (self.repo_path / ".git").exists():
            raise GitError(f"Target directory is not a Git repository: {self.repo_path}")

    def _run_git(self, args: List[str], check: bool = True) -> str:
        """Run a git command in the repository workspace."""
        cmd = ["git"] + args
        try:
            res = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip() or e.stdout.strip()
            logger.error(f"Git command failed: {' '.join(cmd)} -> {err_msg}")
            raise GitError(f"Git command failed: {' '.join(cmd)}: {err_msg}") from e

    def get_current_branch(self) -> str:
        """Get the current active git branch name."""
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def is_clean(self) -> bool:
        """Check if working tree has any uncommitted changes."""
        status = self._run_git(["status", "--porcelain"])
        return len(status) == 0

    def ensure_clean_repo(self) -> None:
        """Verify repository has no unstaged/uncommitted changes."""
        if not self.is_clean():
            raise GitError("Git working directory has uncommitted changes. Please commit or stash first.")

    def create_feature_branch(self, task_id: str, base_branch: str = "main") -> str:
        """Create and checkout a new feature branch for the task."""
        branch_name = f"feature/ai-{task_id}"
        logger.info(f"Creating feature branch: {branch_name} from {base_branch}")

        # Fetch base branch if remote exists (non-fatal if offline/no remote)
        try:
            self._run_git(["fetch", "origin", base_branch], check=False)
        except Exception:
            pass

        # Checkout or create branch
        self._run_git(["checkout", "-B", branch_name])
        return branch_name

    def checkout_branch(self, branch_name: str) -> None:
        """Checkout an existing branch."""
        self._run_git(["checkout", branch_name])

    def get_modified_files(self) -> List[str]:
        """Return list of modified, added, or deleted files."""
        status = self._run_git(["status", "--porcelain"])
        files = []
        for line in status.splitlines():
            line = line.strip()
            if line:
                # Extract file path after status flags (e.g. ' M src/main.py' -> 'src/main.py')
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    files.append(parts[1])
        return files

    def get_diff(self, cached: bool = False) -> str:
        """Get git diff output."""
        args = ["diff"]
        if cached:
            args.append("--cached")
        return self._run_git(args)

    def commit_changes(self, message: str) -> Optional[str]:
        """Stage all changes and create a git commit. Returns commit hash."""
        modified = self.get_modified_files()
        if not modified:
            logger.warning("No changes detected to commit.")
            return None

        logger.info(f"Staging {len(modified)} files and committing...")
        self._run_git(["add", "-A"])
        self._run_git(["commit", "-m", message])
        commit_sha = self._run_git(["rev-parse", "HEAD"])
        logger.info(f"Commit created: {commit_sha[:7]} - {message.splitlines()[0]}")
        return commit_sha

    def push_branch(self, branch_name: str, remote: str = "origin") -> None:
        """Push the feature branch to remote origin."""
        logger.info(f"Pushing branch {branch_name} to {remote}...")
        self._run_git(["push", "-u", remote, branch_name])

    def rollback_changes(self, target_branch: Optional[str] = None) -> None:
        """Discard uncommitted changes and optionally return to target branch."""
        logger.warning("Rolling back uncommitted changes...")
        self._run_git(["reset", "--hard", "HEAD"], check=False)
        self._run_git(["clean", "-fd"], check=False)
        if target_branch:
            self.checkout_branch(target_branch)
