"""Quality gate module for automated test execution and error summary extraction."""

import subprocess
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from aicoop.utils.logger import logger


class QualityCheckResult(BaseModel):
    """Result of automated quality checks."""
    passed: bool
    command: str
    exit_code: int
    stdout: str
    stderr: str
    error_summary: Optional[str] = None


class QualityGate:
    """Executes automated tests and formats feedback for coding agents."""

    def __init__(self, test_command: str = "pytest"):
        self.test_command = test_command

    def run_checks(self, workspace_path: Path, custom_command: Optional[str] = None) -> QualityCheckResult:
        """Run tests in the workspace and return parsed result."""
        cmd_str = custom_command or self.test_command
        logger.info(f"Running quality gate check: [bold cyan]{cmd_str}[/bold cyan]")

        try:
            res = subprocess.run(
                cmd_str,
                shell=True,
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=180
            )
            passed = (res.returncode == 0)
            error_summary = None
            if not passed:
                error_summary = self._extract_error_summary(res.stdout, res.stderr)
                logger.warning(f"Quality gate check failed with exit code {res.returncode}")
            else:
                logger.info("Quality gate check passed successfully!")

            return QualityCheckResult(
                passed=passed,
                command=cmd_str,
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
                error_summary=error_summary
            )
        except subprocess.TimeoutExpired:
            logger.error("Quality check timed out after 180 seconds.")
            return QualityCheckResult(
                passed=False,
                command=cmd_str,
                exit_code=-1,
                stdout="",
                stderr="Execution timed out after 180 seconds",
                error_summary="Test execution timed out."
            )
        except Exception as e:
            logger.error(f"Error executing quality gate: {e}")
            return QualityCheckResult(
                passed=False,
                command=cmd_str,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                error_summary=f"Failed to execute test command: {e}"
            )

    def _extract_error_summary(self, stdout: str, stderr: str, max_lines: int = 40) -> str:
        """Extract actionable error lines to avoid blowing up LLM context window."""
        output = stdout + "\n" + stderr
        lines = [line.strip() for line in output.splitlines() if line.strip()]

        # Filter lines with typical test failure keywords
        relevant_lines = []
        for line in lines:
            lower = line.lower()
            if any(k in lower for k in ["failed", "error", "traceback", "assertionerror", "exception", "failures"]):
                relevant_lines.append(line)

        if not relevant_lines:
            # Fallback to the tail of output
            relevant_lines = lines[-max_lines:]
        else:
            relevant_lines = relevant_lines[-max_lines:]

        return "\n".join(relevant_lines)
