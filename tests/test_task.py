"""Tests for Task model and state transitions."""

from aicoop.core.task import Task, TaskStatus


def test_task_creation_and_defaults():
    task = Task(title="Test Task", prompt="Do something")
    assert task.id.startswith("task-")
    assert task.status == TaskStatus.PENDING
    assert task.attempts == 0
    assert task.branch_name is None


def test_task_lifecycle_transitions():
    task = Task(title="Add Healthcheck", prompt="Create /health endpoint")
    
    # In Progress
    task.mark_in_progress("feature/ai-task-001")
    assert task.status == TaskStatus.AGENT_WORKING
    assert task.branch_name == "feature/ai-task-001"

    # Testing
    task.mark_testing()
    assert task.status == TaskStatus.TESTING

    # Completed
    task.mark_completed(pr_url="https://github.com/test/repo/pull/1")
    assert task.status == TaskStatus.COMPLETED
    assert task.pr_url == "https://github.com/test/repo/pull/1"


def test_task_failure_transition():
    task = Task(title="Failing Task", prompt="Break things")
    task.mark_failed("Max retry limit exceeded")
    assert task.status == TaskStatus.FAILED
    assert task.error_message == "Max retry limit exceeded"
