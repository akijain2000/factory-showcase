"""
Skeleton pipeline for api-test-generator agent.
Each function mirrors a tool; host wires LLM function calling.
"""

from __future__ import annotations

from typing import Any


def parse_openapi(source: str, format: str | None = None) -> dict[str, Any]:
    raise NotImplementedError


def generate_test_case(
    operation_id: str,
    framework: str,
    base_url_var: str | None = None,
    fixtures: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raise NotImplementedError


def validate_response_schema(test_id: str, status_code: str, schema_ref: str) -> dict[str, Any]:
    raise NotImplementedError


def run_test(test_ids: list[str], env: dict[str, str] | None = None, timeout_seconds: int = 300) -> dict[str, Any]:
    raise NotImplementedError


def generate_report(run_id: str, format: str) -> dict[str, Any]:
    raise NotImplementedError


def mock_endpoint(
    name: str,
    method: str,
    path_pattern: str,
    response: dict[str, Any],
    priority: int | None = None,
) -> dict[str, Any]:
    raise NotImplementedError


def generate_suite(spec_path: str, framework: str) -> list[str]:
    """Skeleton: parse → generate all operations → validate → return test_ids."""
    raise NotImplementedError
