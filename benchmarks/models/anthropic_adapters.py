import os
import time

import httpx
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from benchmarks.schema import FastMCPToolSchema, ModelResponse, ToolCallEvent
from benchmarks.utils import call_tool

load_dotenv()


class BaseAsyncClaudeAdapter:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def convert_fastmcp_tools_schema_to_adapter(self, mcp_tools: list[FastMCPToolSchema]) -> list:
        claude_tools = []

        for tool in mcp_tools:
            claude_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
            )
        return claude_tools

    async def run(self, prompt: str, tools: list):
        start_time = time.perf_counter()
        tool_calls = []
        messages = [{"role": "user", "content": prompt}]

        adapter_mcp_tools = self.convert_fastmcp_tools_schema_to_adapter(tools)

        try:
            response = await self.client.messages.create(
                model=self.model, max_tokens=4096, messages=messages, tools=adapter_mcp_tools
            )

            # Handle multi-turn tool use
            while response.stop_reason == "tool_use":
                # Extract tool uses from content blocks
                tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

                # Add assistant message to conversation
                messages.append({"role": "assistant", "content": response.content})

                # Process tool calls
                tool_results = []
                for tool_use in tool_use_blocks:
                    tool_start = time.perf_counter()

                    # Execute tool via MCP
                    try:
                        result = await call_tool(tool_name=tool_use.name, arguments=tool_use.input)
                        tool_latency = int((time.perf_counter() - tool_start) * 1000)

                        # Track successful tool call
                        tool_calls.append(
                            ToolCallEvent(
                                tool_name=tool_use.name,
                                arguments=tool_use.input,
                                model=self.model,
                                latency_ms=tool_latency,
                            )
                        )

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": str(result),
                            }
                        )
                    except Exception as e:
                        # Track failed tool call
                        tool_latency = int((time.perf_counter() - tool_start) * 1000)
                        tool_calls.append(
                            ToolCallEvent(
                                tool_name=tool_use.name,
                                arguments=tool_use.input,
                                model=self.model,
                                latency_ms=tool_latency,
                            )
                        )
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True,
                            }
                        )

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})

                # Continue conversation
                response = await self.client.messages.create(
                    model=self.model, max_tokens=32768, messages=messages, tools=adapter_mcp_tools
                )

            # Extract final response text
            text_blocks = [block.text for block in response.content if hasattr(block, "text")]
            response_text = " ".join(text_blocks)
            total_latency = int((time.perf_counter() - start_time) * 1000)

            return ModelResponse(
                model=self.model,
                session_id=response.id,
                query=prompt,
                response_text=response_text,
                tool_calls=tool_calls,
                total_latency_ms=total_latency,
                error=None,
            )

        except Exception as e:
            print(e)
            return False


class AsyncClaudeAdapter(BaseAsyncClaudeAdapter):
    def __init__(self, model):
        # Anthropic client has a default 10-minute timeout, so we need to force
        # the time limit to be 10 minutes. If longer responses are needed, streaming
        # is required. See: https://github.com/anthropics/anthropic-sdk-python#long-requests
        timeout = httpx.Timeout(600.0, read=None, write=60.0, connect=10.0)

        client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=timeout)
        super().__init__(client, model)
