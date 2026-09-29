"""Configuration management for AI-Coop platform."""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _HAS_PYDANTIC_SETTINGS = True
except ImportError:
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = None
    _HAS_PYDANTIC_SETTINGS = False


class Settings(BaseSettings):
    """Global configuration settings for AI-Coop."""

    # Project Paths
    workspace_root: Path = Field(
        default_factory=lambda: Path(os.getenv("TARGET_REPO_PATH", str(Path.cwd()))).resolve(),
        description="Target git repository path to operate on"
    )

    # Git & GitHub Configuration
    github_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN"),
        description="GitHub Personal Access Token"
    )
    github_repo: Optional[str] = Field(
        default_factory=lambda: os.getenv("GITHUB_REPO"),
        description="Target GitHub repository in 'owner/repo' format"
    )
    base_branch: str = Field(
        default="main",
        description="Base branch to fork from and target PRs against"
    )

    # Agent Engine Configuration
    agent_type: Literal["antigravity", "aider", "gemini-cli"] = Field(
        default="antigravity",
        description="Coding agent backend engine to use"
    )
    antigravity_enabled: bool = Field(
        default=True,
        description="Whether Antigravity Python SDK / CLI is enabled"
    )

    # Aider Configuration
    aider_model: str = Field(
        default="gemini/gemini-1.5-pro-latest",
        description="Model identifier when using Aider runner"
    )
    aider_timeout_seconds: int = Field(
        default=300,
        description="Timeout for agent execution in seconds"
    )

    # Pipeline Safety & Quality Gates
    max_iterations: int = Field(
        default=3,
        description="Maximum attempts to fix failing tests"
    )
    test_command: str = Field(
        default="pytest",
        description="Command to run automated tests for verification"
    )
    auto_push: bool = Field(
        default=False,
        description="Whether to automatically push feature branch to remote git"
    )
    auto_create_pr: bool = Field(
        default=False,
        description="Whether to automatically create a Pull Request on GitHub"
    )

    if _HAS_PYDANTIC_SETTINGS:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )


def get_settings() -> Settings:
    """Load and return singleton settings instance."""
    return Settings()
