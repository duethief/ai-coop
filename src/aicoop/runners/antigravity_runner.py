"""Antigravity Python SDK and CLI runner implementation."""

import asyncio
import time
import subprocess
from pathlib import Path
from typing import Optional, List
from aicoop.core.task import Task
from aicoop.runners.base import BaseAgentRunner, AgentRunResult
from aicoop.utils.logger import logger

# Try importing official Antigravity Python SDK
try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    _HAS_ANTIGRAVITY_SDK = True
except ImportError:
    _HAS_ANTIGRAVITY_SDK = False


class AntigravityRunner(BaseAgentRunner):
    """Coding agent runner backed by Google Antigravity SDK or CLI."""

    def __init__(self, system_instruction: Optional[str] = None):
        super().__init__(name="antigravity")
        self.system_instruction = system_instruction or (
            "You are an expert autonomous software engineer working on a Git repository. "
            "Analyze the instructions carefully, inspect the existing codebase, "
            "and edit the relevant files to fulfill the task requirements. "
            "Ensure the code is robust and passes all test suites."
        )

    async def run_task(
        self,
        task: Task,
        workspace: Path,
        error_feedback: Optional[str] = None
    ) -> AgentRunResult:
        """Execute task via Antigravity SDK (preferred) or Antigravity CLI fallback."""
        start_time = time.time()
        logger.info(f"Starting Antigravity agent run for task: [bold]{task.id}[/bold]")

        # Compose prompt including feedback if any
        full_prompt = self._compose_prompt(task, error_feedback)

        if _HAS_ANTIGRAVITY_SDK:
            return await self._run_via_sdk(task, workspace, full_prompt, start_time)
        else:
            return await self._run_via_cli(task, workspace, full_prompt, start_time)

    def _compose_prompt(self, task: Task, error_feedback: Optional[str]) -> str:
        """Build structured prompt for the agent."""
        prompt = f"# Task: {task.title}\n\n{task.prompt}\n"
        if task.target_files:
            prompt += f"\nTarget files to focus on: {', '.join(task.target_files)}\n"

        if error_feedback:
            prompt += (
                f"\n\n[IMPORTANT: PREVIOUS TEST EXECUTION FAILED]\n"
                f"Your previous changes caused the following test failure. "
                f"Please inspect the error log, identify the root cause, and fix the code:\n"
                f"```\n{error_feedback}\n```\n"
            )
        return prompt

    async def _run_via_sdk(
        self,
        task: Task,
        workspace: Path,
        prompt: str,
        start_time: float
    ) -> AgentRunResult:
        """Run agent natively via Google Antigravity Python SDK."""
        logger.info("Executing agent using native [bold green]Antigravity Python SDK[/bold green]...")
        output_logs = []
        thoughts = []
        tool_calls = []

        try:
            # Enable write tools (file editing, command execution)
            config = LocalAgentConfig(
                system_instructions=self.system_instruction,
                capabilities=CapabilitiesConfig()
            )

            async with Agent(config) as agent:
                response = await agent.chat(prompt)

                # Collect response tokens
                async for token in response:
                    output_logs.append(token)

                # Collect thoughts if available
                if hasattr(response, "thoughts"):
                    async for thought in response.thoughts:
                        thoughts.append(thought)
                        logger.debug(f"[Agent Thought] {thought}")

                # Collect tool calls if available
                if hasattr(response, "tool_calls"):
                    async for call in response.tool_calls:
                        tool_calls.append({"name": call.name, "args": getattr(call, "args", {})})
                        logger.info(f"[Tool Executed] {call.name}")

            elapsed = time.time() - start_time
            full_log = "".join(output_logs)
            return AgentRunResult(
                success=True,
                output_log=full_log,
                execution_time_seconds=elapsed,
                telemetry={"thoughts_count": len(thoughts), "tool_calls": tool_calls}
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Antigravity SDK execution error: {e}")
            return AgentRunResult(
                success=False,
                error_message=str(e),
                execution_time_seconds=elapsed
            )

    async def _run_via_cli(
        self,
        task: Task,
        workspace: Path,
        prompt: str,
        start_time: float
    ) -> AgentRunResult:
        """Fallback execution via Antigravity CLI (agy) subprocess."""
        logger.info("Executing agent using [bold yellow]Antigravity CLI (agy)[/bold yellow] fallback...")
        cmd = ["agy", "--prompt", prompt]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(workspace),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
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
            err = (
                "Neither 'google-antigravity' Python package nor 'agy' CLI command was found on the system. "
                "Please run: pip install google-antigravity"
            )
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
