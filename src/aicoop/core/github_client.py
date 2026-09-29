"""GitHub API integration client for Issues and Pull Requests."""

from typing import Optional, Dict, Any, List
from aicoop.utils.logger import logger

try:
    from github import Github, GithubException
    _HAS_PYGITHUB = True
except ImportError:
    _HAS_PYGITHUB = False


class GitHubClient:
    """Client for interacting with GitHub REST API."""

    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        self.token = token
        self.repo_name = repo_name
        self._gh = None
        self._repo = None

        if token and repo_name and _HAS_PYGITHUB:
            try:
                self._gh = Github(token)
                self._repo = self._gh.get_repo(repo_name)
                logger.info(f"Connected to GitHub repository: [bold green]{repo_name}[/bold green]")
            except Exception as e:
                logger.warning(f"Could not connect to GitHub repository: {e}")
        else:
            logger.info("GitHubClient running in local-only / offline mode (No token or repo configured).")

    @property
    def is_connected(self) -> bool:
        """Check if authenticated connection to GitHub repo is available."""
        return self._repo is not None

    def get_issue(self, issue_number: int) -> Dict[str, Any]:
        """Fetch issue title and body from GitHub."""
        if not self.is_connected:
            raise RuntimeError("GitHubClient is not connected to a remote repository.")

        try:
            issue = self._repo.get_issue(issue_number)
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body or "",
                "labels": [label.name for label in issue.labels],
                "url": issue.html_url
            }
        except GithubException as e:
            logger.error(f"Failed to fetch issue #{issue_number}: {e}")
            raise

    def create_pull_request(
        self,
        branch: str,
        title: str,
        body: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a new Pull Request on GitHub."""
        if not self.is_connected:
            logger.warning("GitHub not connected. Returning dummy PR response.")
            return {
                "number": 999,
                "url": f"https://github.com/local-offline-mode/pull/999",
                "title": title
            }

        try:
            pr = self._repo.create_pull(
                title=title,
                body=body,
                head=branch,
                base=base
            )
            logger.info(f"Successfully created Pull Request #{pr.number}: {pr.html_url}")
            return {
                "number": pr.number,
                "url": pr.html_url,
                "title": pr.title
            }
        except GithubException as e:
            logger.error(f"Failed to create Pull Request: {e}")
            raise

    def add_comment(self, issue_or_pr_number: int, comment: str) -> None:
        """Post a comment to an issue or pull request."""
        if not self.is_connected:
            return
        try:
            issue = self._repo.get_issue(issue_or_pr_number)
            issue.create_comment(comment)
        except Exception as e:
            logger.warning(f"Failed to post comment to #{issue_or_pr_number}: {e}")
