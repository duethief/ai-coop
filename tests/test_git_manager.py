"""Tests for GitManager operations."""

import subprocess
from pathlib import Path
import pytest
from aicoop.core.git_manager import GitManager, GitError


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Initialize a clean Git repository fixture in a temp directory."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "tester@example.com"], cwd=tmp_path, check=True)
    
    # Create initial commit
    init_file = tmp_path / "README.md"
    init_file.write_text("# Initial Test Repo")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True)
    
    return tmp_path


def test_git_manager_initial_state(temp_git_repo: Path):
    gm = GitManager(temp_git_repo)
    assert gm.is_clean() is True
    assert gm.get_modified_files() == []


def test_git_manager_create_branch(temp_git_repo: Path):
    gm = GitManager(temp_git_repo)
    branch = gm.create_feature_branch("task-1234", base_branch="main")
    assert branch == "feature/ai-task-1234"
    assert gm.get_current_branch() == "feature/ai-task-1234"


def test_git_manager_detect_modifications_and_commit(temp_git_repo: Path):
    gm = GitManager(temp_git_repo)
    gm.create_feature_branch("task-5678")

    # Modify a file
    new_file = temp_git_repo / "main.py"
    new_file.write_text("print('hello world')")

    modified = gm.get_modified_files()
    assert "main.py" in modified

    commit_sha = gm.commit_changes("feat: add main.py")
    assert commit_sha is not None
    assert len(commit_sha) >= 7
    assert gm.is_clean() is True


def test_git_manager_rollback(temp_git_repo: Path):
    gm = GitManager(temp_git_repo)
    
    dirty_file = temp_git_repo / "dirty.txt"
    dirty_file.write_text("uncommitted garbage")
    assert gm.is_clean() is False

    gm.rollback_changes()
    assert gm.is_clean() is True
    assert not dirty_file.exists()
