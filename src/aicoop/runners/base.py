"""Base abstract class for coding agent runners."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from aicoop.core.task import Task


class AgentRunResult(BaseModel):
    """Result emitted by an agent execution run."""
    success: bool
    modified_files: List[str] = []
    output_log: str = ""
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    telemetry: Dict[str, Any] = {}


class BaseAgentRunner(ABC):
    """Abstract interface for all coding agent execution backends."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run_task(
        self,
        task: Task,
        workspace: Path,
        error_feedback: Optional[str] = None
    ) -> AgentRunResult:
        """
        Execute the coding agent to resolve the task in the given workspace.

        Args:
            task: The Task model containing instructions and target files.
            workspace: The local directory containing the repository workspace.
            error_feedback: Optional error log from a previous failed quality gate run.
        """
        pass
