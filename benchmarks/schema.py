import json
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional


@dataclass
class FastMCPToolSchema:
    """Represents a single MCP tool definition as exposed by a FastMCP server"""

    name: str
    inputSchema: Dict[str, Any]
    title: Optional[str] = None
    description: Optional[str] = None
    outputSchema: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


@dataclass
class ToolCallEvent:
    """Tool call details"""

    tool_name: str
    arguments: dict
    model: str
    latency_ms: int


@dataclass
class ModelResponse:
    """Complete result from a model run"""

    model: str
    session_id: str
    query: str
    response_text: str
    tool_calls: list[ToolCallEvent]
    total_runtime_ms: int
    error: str | None = None

    CSV_FIELDS: ClassVar[list[str]] = [
        "model",
        "session_id",
        "tool_calls",
        "tool_arguments",
        "response_text",
        "total_runtime_s",
    ]

    @property
    def tool_names(self) -> str:
        return "; ".join(tc.tool_name for tc in self.tool_calls) if self.tool_calls else ""

    @property
    def tool_arguments(self) -> str:
        return (
            "; ".join(f"{tc.tool_name}: {json.dumps(tc.arguments)}" for tc in self.tool_calls)
            if self.tool_calls
            else ""
        )

    def to_csv_row(self) -> dict:
        return {
            "model": self.model,
            "session_id": self.session_id,
            "tool_calls": self.tool_names,
            "tool_arguments": self.tool_arguments,
            "response_text": self.response_text,
            "total_runtime_s": self.total_runtime_ms / 1000,
        }


@dataclass
class BenchmarkQueries:
    query: str
