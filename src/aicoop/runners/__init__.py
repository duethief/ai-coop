"""Runners package and factory function."""

from aicoop.runners.base import BaseAgentRunner, AgentRunResult
from aicoop.runners.antigravity_runner import AntigravityRunner
from aicoop.runners.aider_runner import AiderRunner
from aicoop.runners.gemini_runner import GeminiCliRunner


def create_agent_runner(agent_type: str = "antigravity", **kwargs) -> BaseAgentRunner:
    """Factory to instantiate the appropriate agent runner."""
    agent_type = agent_type.lower()
    if agent_type == "antigravity":
        return AntigravityRunner(**kwargs)
    elif agent_type == "aider":
        return AiderRunner(**kwargs)
    elif agent_type == "gemini-cli":
        return GeminiCliRunner(**kwargs)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Choose from 'antigravity', 'aider', 'gemini-cli'.")
