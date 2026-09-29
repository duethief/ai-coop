"""Gemini CLI agent runner implementation."""

import asyncio
import time
from pathlib import Path
from typing import Optional
from aicoop.core.task import Task
from aicoop.runners.base import BaseAgentRunner, AgentRunResult
from aicoop.utils.logger import logger


class GeminiCliRunner(BaseAgentRunner):
    """Coding agent runner backed by Gemini CLI."""

    def __init__(self, cli_command: str = "gemini", timeout_seconds: int = 300):
        super().__init__(name="gemini-cli")
        self.cli_command = cli_command
        self.timeout_seconds = timeout_seconds

    async def run_task(
        self,
        task: Task,
        workspace: Path,
        error_feedback: Optional[str] = None
    ) -> AgentRunResult:
        """Execute Gemini CLI command in batch mode."""
        start_time = time.time()
        logger.info(f"Starting Gemini CLI runner for task: [bold]{task.id}[/bold]")

        prompt = f"# Task: {task.title}\n{task.prompt}"
        if error_feedback:
            prompt += f"\n\n[Fix Failure]:\n{error_feedback}"

        cmd = [self.cli_command, "--prompt", prompt]

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
                    error_message=f"Gemini CLI timed out after {self.timeout_seconds}s",
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
            err = f"Gemini CLI command '{self.cli_command}' was not found in PATH."
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
