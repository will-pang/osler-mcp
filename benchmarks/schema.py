from dataclasses import dataclass


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
    query: str
    response_text: str
    tool_calls: list[ToolCallEvent]
    total_latency_ms: int
    error: str | None = None

    @property
    def tool_calls_str(self) -> str:
        return "; ".join([f"{tc.tool_name}" for tc in self.tool_calls]) if self.tool_calls else ""


@dataclass
class BenchmarkQueries:
    query: str
