"""CLI entrypoint for AI-Coop platform."""

import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from aicoop import __version__
from aicoop.config import get_settings
from aicoop.core.task import Task
from aicoop.core.pipeline import CorePipeline
from aicoop.core.github_client import GitHubClient
from aicoop.runners import create_agent_runner

app = typer.Typer(
    name="aicoop",
    help="AI Agent Collaborative Development Platform CLI",
    add_completion=False
)
console = Console()


@app.command("version")
def version():
    """Print AI-Coop version."""
    console.print(f"[bold cyan]AI-Coop Platform[/bold cyan] version [green]{__version__}[/green]")


@app.command("config-check")
def config_check():
    """Inspect current configuration settings and active environment."""
    settings = get_settings()
    table = Table(title="AI-Coop Configuration Check")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Workspace Root", str(settings.workspace_root))
    table.add_row("Agent Type", settings.agent_type)
    table.add_row("Antigravity Enabled", str(settings.antigravity_enabled))
    table.add_row("Aider Model", settings.aider_model)
    table.add_row("Test Command", settings.test_command)
    table.add_row("Max Iterations", str(settings.max_iterations))
    table.add_row("GitHub Token Set", "Yes" if settings.github_token else "No")
    table.add_row("GitHub Repo", settings.github_repo or "Not set")
    table.add_row("Auto Push", str(settings.auto_push))
    table.add_row("Auto Create PR", str(settings.auto_create_pr))

    console.print(table)


@app.command("run")
def run_task(
    prompt: str = typer.Option(..., "--task", "-t", help="Detailed prompt and requirements for the agent"),
    title: Optional[str] = typer.Option(None, "--title", help="Short title for the task (defaults to prompt snippet)"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent engine: antigravity, aider, gemini-cli"),
    test_cmd: Optional[str] = typer.Option(None, "--test-cmd", help="Override test command (e.g. pytest)"),
    push: bool = typer.Option(False, "--push", help="Push branch to remote upon success"),
    pr: bool = typer.Option(False, "--pr", help="Create GitHub Pull Request upon success"),
):
    """Execute an ad-hoc coding task via the autonomous pipeline."""
    settings = get_settings()
    if agent:
        settings.agent_type = agent
    if test_cmd:
        settings.test_command = test_cmd
    if push:
        settings.auto_push = True
    if pr:
        settings.auto_create_pr = True

    task_title = title or (prompt[:50] + "..." if len(prompt) > 50 else prompt)
    task = Task(title=task_title, prompt=prompt)

    pipeline = CorePipeline(settings=settings)
    result_task = asyncio.run(pipeline.execute_task(task))

    if result_task.status.value in ["completed", "committed"]:
        console.print(f"\n[bold green]✔ Task Finished Successfully![/bold green]")
        console.print(f"Branch: [cyan]{result_task.branch_name}[/cyan]")
        console.print(f"Commit: [yellow]{result_task.commit_sha[:7] if result_task.commit_sha else 'N/A'}[/yellow]")
        if result_task.pr_url:
            console.print(f"PR URL: [blue underline]{result_task.pr_url}[/blue underline]")
    else:
        console.print(f"\n[bold red]✘ Task Failed.[/bold red] Reason: {result_task.error_message}")
        raise typer.Exit(code=1)


@app.command("issue")
def run_issue(
    issue_number: int = typer.Argument(..., help="GitHub Issue number to resolve"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent engine: antigravity, aider, gemini-cli"),
    push: bool = typer.Option(True, "--push", help="Push branch to remote"),
    pr: bool = typer.Option(True, "--pr", help="Create Pull Request linked to issue"),
):
    """Fetch a GitHub issue and run the autonomous pipeline to resolve it."""
    settings = get_settings()
    if agent:
        settings.agent_type = agent
    settings.auto_push = push
    settings.auto_create_pr = pr

    gh_client = GitHubClient(token=settings.github_token, repo_name=settings.github_repo)
    if not gh_client.is_connected:
        console.print("[bold red]Error: GITHUB_TOKEN and GITHUB_REPO must be set in .env to use 'issue' command.[/bold red]")
        raise typer.Exit(code=1)

    issue_data = gh_client.get_issue(issue_number)
    console.print(f"Loaded Issue #{issue_number}: [bold]{issue_data['title']}[/bold]")

    task = Task(
        title=issue_data["title"],
        prompt=issue_data["body"] or issue_data["title"],
        issue_number=issue_number
    )

    pipeline = CorePipeline(settings=settings, github_client=gh_client)
    result_task = asyncio.run(pipeline.execute_task(task))

    if result_task.status.value in ["completed", "committed"]:
        console.print(f"[bold green]✔ Issue #{issue_number} resolved with PR![/bold green]")
        if result_task.pr_url:
            console.print(f"PR URL: [blue underline]{result_task.pr_url}[/blue underline]")
    else:
        console.print(f"[bold red]✘ Failed to resolve Issue #{issue_number}: {result_task.error_message}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
