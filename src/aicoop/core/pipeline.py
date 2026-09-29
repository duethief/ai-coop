"""Core autonomous engineering pipeline orchestrator."""

import time
from pathlib import Path
from typing import Optional, List
from aicoop.config import Settings, get_settings
from aicoop.core.task import Task, TaskStatus
from aicoop.core.git_manager import GitManager
from aicoop.core.quality_gate import QualityGate
from aicoop.core.github_client import GitHubClient
from aicoop.runners.base import BaseAgentRunner
from aicoop.runners import create_agent_runner
from aicoop.utils.logger import logger


class CorePipeline:
    """End-to-End Orchestrator: Issue -> Branch -> Agent -> Quality Gate -> Commit -> PR."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        runner: Optional[BaseAgentRunner] = None,
        git_manager: Optional[GitManager] = None,
        quality_gate: Optional[QualityGate] = None,
        github_client: Optional[GitHubClient] = None
    ):
        self.settings = settings or get_settings()
        self.git = git_manager or GitManager(self.settings.workspace_root)
        self.quality = quality_gate or QualityGate(self.settings.test_command)
        self.github = github_client or GitHubClient(
            token=self.settings.github_token,
            repo_name=self.settings.github_repo
        )
        self.runner = runner or create_agent_runner(
            agent_type=self.settings.agent_type,
            model=self.settings.aider_model
        )

    async def execute_task(self, task: Task) -> Task:
        """Run the full development lifecycle for a given task."""
        logger.info(f"============================================================")
        logger.info(f"Starting AI-Coop Pipeline for Task: [bold]{task.id}[/bold]")
        logger.info(f"Task Title: {task.title}")
        logger.info(f"Agent Engine: [bold cyan]{self.runner.name}[/bold cyan]")
        logger.info(f"============================================================")

        # Step 1: Ensure Git workspace is clean
        try:
            self.git.ensure_clean_repo()
        except Exception as e:
            logger.error(f"Workspace check failed: {e}")
            task.mark_failed(str(e))
            return task

        # Step 2: Create feature branch
        branch_name = self.git.create_feature_branch(
            task_id=task.id,
            base_branch=self.settings.base_branch
        )
        task.mark_in_progress(branch_name)

        # Step 3: Feedback execution loop
        error_feedback: Optional[str] = None
        tests_passed = False

        for attempt in range(1, self.settings.max_iterations + 1):
            task.attempts = attempt
            logger.info(f"[Iteration {attempt}/{self.settings.max_iterations}] Invoking {self.runner.name} agent...")

            # Run agent
            agent_result = await self.runner.run_task(
                task=task,
                workspace=self.settings.workspace_root,
                error_feedback=error_feedback
            )

            if not agent_result.success:
                logger.warning(f"Agent reported failure on attempt {attempt}: {agent_result.error_message}")
                error_feedback = agent_result.error_message or "Agent execution failed."
                continue

            # Check modified files
            modified = self.git.get_modified_files()
            logger.info(f"Detected {len(modified)} modified file(s): {', '.join(modified) if modified else 'None'}")

            # Run Quality Gate
            task.mark_testing()
            quality_result = self.quality.run_checks(self.settings.workspace_root)

            if quality_result.passed:
                logger.info("[bold green]✔ All Quality Gate checks passed![/bold green]")
                tests_passed = True
                break
            else:
                logger.warning(f"[bold red]✘ Quality Gate failed on attempt {attempt}.[/bold red]")
                error_feedback = quality_result.error_summary
                logger.info(f"Feedback prepared for agent retry: {len(error_feedback or '')} chars")

        # Step 4: Handle completion or failure
        if tests_passed:
            commit_msg = self._build_commit_message(task)
            commit_sha = self.git.commit_changes(commit_msg)
            task.commit_sha = commit_sha
            task.status = TaskStatus.COMMITTED

            # Optional remote push & PR
            pr_url = None
            if self.settings.auto_push:
                self.git.push_branch(branch_name)
                if self.settings.auto_create_pr:
                    pr_title = f"[AI] {task.title}"
                    pr_body = self._build_pr_body(task)
                    pr_data = self.github.create_pull_request(
                        branch=branch_name,
                        title=pr_title,
                        body=pr_body,
                        base=self.settings.base_branch
                    )
                    pr_url = pr_data.get("url")
                    task.pr_number = pr_data.get("number")

            task.mark_completed(pr_url=pr_url)
            logger.info(f"[bold green]✔ Task {task.id} successfully completed![/bold green]")
        else:
            logger.error(f"[bold red]✘ Task {task.id} failed after {self.settings.max_iterations} attempts.[/bold red]")
            self.git.rollback_changes(target_branch=self.settings.base_branch)
            task.mark_failed("Max retry iterations exceeded without passing quality gate.")

        return task

    def _build_commit_message(self, task: Task) -> str:
        """Compose clear structured git commit message."""
        msg = f"feat(ai): {task.title}\n\n"
        msg += f"Task ID: {task.id}\n"
        msg += f"Automated resolution by AI-Coop ({self.runner.name} agent)\n\n"
        if task.issue_number:
            msg += f"Resolves #{task.issue_number}\n"
        return msg

    def _build_pr_body(self, task: Task) -> str:
        """Compose detailed Pull Request markdown description."""
        body = f"## 🤖 AI-Generated Pull Request\n\n"
        body += f"### 📌 Task Overview\n"
        body += f"- **Task ID**: `{task.id}`\n"
        body += f"- **Agent Engine**: `{self.runner.name}`\n"
        body += f"- **Iterations Required**: {task.attempts}\n\n"
        body += f"### 📝 Requirements\n"
        body += f"{task.prompt}\n\n"
        if task.issue_number:
            body += f"Closes #{task.issue_number}\n\n"
        body += f"### 🛡 Quality Gate Status\n"
        body += f"- Automated tests: **PASSED** (`{self.settings.test_command}`)\n\n"
        body += f"---\n*Generated by AI-Coop Core Pipeline*"
        return body
