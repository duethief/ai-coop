"""Aider CLI subprocess agent runner implementation."""

import asyncio
import time
from pathlib import Path
from typing import Optional, List
from aicoop.core.task import Task
from aicoop.runners.base import BaseAgentRunner, AgentRunResult
from aicoop.utils.logger import logger


class AiderRunner(BaseAgentRunner):
    """Coding agent runner backed by Aider CLI."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro-latest", timeout_seconds: int = 300):
        super().__init__(name="aider")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def run_task(
        self,
        task: Task,
        workspace: Path,
        error_feedback: Optional[str] = None
    ) -> AgentRunResult:
        """Execute Aider CLI in headless batch mode."""
        start_time = time.time()
        logger.info(f"Starting Aider runner for task: [bold]{task.id}[/bold] using model {self.model}")

        prompt = f"{task.title}\n{task.prompt}"
        if error_feedback:
            prompt += (
                f"\n\n[PREVIOUS TEST FAILED]\nPlease fix the following errors:\n"
                f"```\n{error_feedback}\n```"
            )

        cmd = [
            "aider",
            "--yes",
            "--no-auto-commits",
            "--model", self.model,
            "--message", prompt
        ]

        if task.target_files:
            cmd.extend(task.target_files)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(workspace),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                proc.kill()
                elapsed = time.time() - start_time
                return AgentRunResult(
                    success=False,
                    error_message=f"Aider execution timed out after {self.timeout_seconds} seconds.",
                    execution_time_seconds=elapsed
                )

            elapsed = time.time() - start_time
            success = (proc.returncode == 0)
            return AgentRunResult(
                success=success,
                output_log=stdout.decode("utf-8", errors="replace"),
                error_message=stderr.decode("utf-8", errors="replace") if not success else None,
                execution_time_seconds=elapsed
            )
        except FileNotFoundError:
            elapsed = time.time() - start_time
            err = "Aider executable not found. Please install via: pip install aider-chat"
            logger.warning(err)
            return AgentRunResult(
                success=False,
                error_message=err,
                execution_time_seconds=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return AgentRunResult(
                success=False,
                error_message=str(e),
                execution_time_seconds=elapsed
            )
