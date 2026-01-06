import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


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

    @property
    def tool_names(self) -> str:
        return "; ".join([f"{tc.tool_name}" for tc in self.tool_calls]) if self.tool_calls else ""

    @property
    def tool_arguments(self) -> str:
        return (
            "; ".join([f"{tc.tool_name}: {json.dumps(tc.arguments)}" for tc in self.tool_calls])
            if self.tool_calls
            else ""
        )


@dataclass
class BenchmarkQueries:
    query: str
