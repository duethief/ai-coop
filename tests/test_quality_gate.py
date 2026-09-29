"""Tests for QualityGate execution and error parsing."""

import sys
from pathlib import Path
from aicoop.core.quality_gate import QualityGate


def test_quality_gate_success(tmp_path: Path):
    # Run a command that always succeeds
    cmd = f'"{sys.executable}" -c "print(\'tests passed\'); exit(0)"'
    gate = QualityGate(test_command=cmd)
    res = gate.run_checks(tmp_path)

    assert res.passed is True
    assert res.exit_code == 0
    assert "tests passed" in res.stdout
    assert res.error_summary is None


def test_quality_gate_failure_extraction(tmp_path: Path):
    # Run a command that fails with an assertion error
    script = "import sys; print('AssertionError: expected 200 got 500', file=sys.stderr); sys.exit(1)"
    cmd = f'"{sys.executable}" -c "{script}"'
    gate = QualityGate(test_command=cmd)
    res = gate.run_checks(tmp_path)

    assert res.passed is False
    assert res.exit_code == 1
    assert res.error_summary is not None
    assert "AssertionError" in res.error_summary
