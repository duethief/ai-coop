"""Task data model and lifecycle states for AI-Coop."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Lifecycle status of an AI-assigned development task."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    AGENT_WORKING = "agent_working"
    TESTING = "testing"
    COMMITTED = "committed"
    PR_CREATED = "pr_created"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """Representation of an engineering task to be resolved by an AI Agent."""
    id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:8]}")
    title: str = Field(..., description="Short summary of the task")
    prompt: str = Field(..., description="Detailed instructions and requirements for the agent")
    issue_number: Optional[int] = Field(None, description="Linked GitHub Issue number if any")
    target_files: List[str] = Field(default_factory=list, description="Target files or directories to touch")
    
    # Git & Branch info
    branch_name: Optional[str] = Field(None, description="Feature branch created for this task")
    commit_sha: Optional[str] = Field(None, description="Git commit hash produced by the agent")
    pr_number: Optional[int] = Field(None, description="Created Pull Request number")
    pr_url: Optional[str] = Field(None, description="URL of the created Pull Request")

    # Execution telemetry
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    attempts: int = Field(default=0, description="Number of feedback retry attempts")
    error_message: Optional[str] = Field(None, description="Error detail if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary engine metadata")

    def mark_in_progress(self, branch_name: str) -> None:
        """Mark task as actively being worked on by an agent."""
        self.status = TaskStatus.AGENT_WORKING
        self.branch_name = branch_name
        self.updated_at = datetime.utcnow()

    def mark_testing(self) -> None:
        """Mark task as undergoing quality gate checks."""
        self.status = TaskStatus.TESTING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, pr_url: Optional[str] = None) -> None:
        """Mark task as successfully resolved."""
        self.status = TaskStatus.COMPLETED
        if pr_url:
            self.pr_url = pr_url
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.utcnow()
