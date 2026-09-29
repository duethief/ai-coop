"""Tests for CorePipeline workflow and feedback retry loops."""

import asyncio
from pathlib import Path
import pytest
from aicoop.config import Settings
from aicoop.core.task import Task, TaskStatus
from aicoop.core.git_manager import GitManager
from aicoop.core.quality_gate import QualityGate, QualityCheckResult
from aicoop.core.github_client import GitHubClient
from aicoop.core.pipeline import CorePipeline
from aicoop.runners.base import BaseAgentRunner, AgentRunResult


class MockSuccessAgentRunner(BaseAgentRunner):
    """Mock agent that modifies a file successfully."""
    def __init__(self):
        super().__init__(name="mock-success")

    async def run_task(self, task: Task, workspace: Path, error_feedback=None) -> AgentRunResult:
        app_file = workspace / "app.py"
        app_file.write_text("def run(): return True\n")
        return AgentRunResult(success=True, modified_files=["app.py"])


class MockRetryAgentRunner(BaseAgentRunner):
    """Mock agent that fails on attempt 1 and succeeds on attempt 2."""
    def __init__(self):
        super().__init__(name="mock-retry")
        self.call_count = 0

    async def run_task(self, task: Task, workspace: Path, error_feedback=None) -> AgentRunResult:
        self.call_count += 1
        app_file = workspace / "app.py"
        if self.call_count == 1:
            app_file.write_text("def run(): return False\n")
        else:
            app_file.write_text("def run(): return True\n")
        return AgentRunResult(success=True, modified_files=["app.py"])


class MockQualityGate(QualityGate):
    """Quality gate that checks whether app.py returns True."""
    def run_checks(self, workspace_path: Path, custom_command=None) -> QualityCheckResult:
        app_file = workspace_path / "app.py"
        if app_file.exists() and "return True" in app_file.read_text():
            return QualityCheckResult(passed=True, command="mock_test", exit_code=0, stdout="OK", stderr="")
        else:
            return QualityCheckResult(
                passed=False,
                command="mock_test",
                exit_code=1,
                stdout="",
                stderr="FAIL: app.py returned False",
                error_summary="FAIL: app.py returned False"
            )


@pytest.fixture
def initialized_git_repo(tmp_path: Path) -> Path:
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "tester@example.com"], cwd=tmp_path, check=True)
    init_file = tmp_path / "README.md"
    init_file.write_text("# Initial Repo")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True)
    return tmp_path


def test_pipeline_first_try_success(initialized_git_repo: Path):
    settings = Settings(
        workspace_root=initialized_git_repo,
        max_iterations=3,
        auto_push=False,
        auto_create_pr=False
    )
    git_mgr = GitManager(initialized_git_repo)
    quality_gate = MockQualityGate()
    runner = MockSuccessAgentRunner()
    github_client = GitHubClient()

    pipeline = CorePipeline(
        settings=settings,
        runner=runner,
        git_manager=git_mgr,
        quality_gate=quality_gate,
        github_client=github_client
    )

    task = Task(title="Add app function", prompt="Implement app.py")
    res_task = asyncio.run(pipeline.execute_task(task))

    assert res_task.status == TaskStatus.COMPLETED
    assert res_task.attempts == 1
    assert res_task.commit_sha is not None
    assert (initialized_git_repo / "app.py").exists()


def test_pipeline_retry_loop_success(initialized_git_repo: Path):
    settings = Settings(
        workspace_root=initialized_git_repo,
        max_iterations=3,
        auto_push=False,
        auto_create_pr=False
    )
    git_mgr = GitManager(initialized_git_repo)
    quality_gate = MockQualityGate()
    runner = MockRetryAgentRunner()
    github_client = GitHubClient()

    pipeline = CorePipeline(
        settings=settings,
        runner=runner,
        git_manager=git_mgr,
        quality_gate=quality_gate,
        github_client=github_client
    )

    task = Task(title="Add app function with retry", prompt="Fix app.py")
    res_task = asyncio.run(pipeline.execute_task(task))

    assert res_task.status == TaskStatus.COMPLETED
    assert res_task.attempts == 2
    assert runner.call_count == 2
    assert res_task.commit_sha is not None
