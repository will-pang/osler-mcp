import json
import os
import time

from dotenv import load_dotenv
from openai import AsyncOpenAI

from benchmarks.schema import ModelResponse, ToolCallEvent
from benchmarks.utils import call_tool

load_dotenv()


class BaseAsyncOpenAIAdapter:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def convert_mcp_tools_schema_to_adapter(self, mcp_tools: list) -> list:
        openai_tools = []

        for tool in mcp_tools:
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema
                        or {
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    },
                }
            )
        return openai_tools

    async def run(self, prompt: str, tools: list):
        start_time = time.perf_counter()
        tool_calls = []
        messages = [{"role": "user", "content": prompt}]

        adapter_mcp_tools = self.convert_mcp_tools_schema_to_adapter(tools)

        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages, tools=adapter_mcp_tools, tool_choice="auto"
            )

            # Handle multi-turn tool use
            while response.choices[0].finish_reason == "tool_calls":
                assistant_message = response.choices[0].message
                messages.append(assistant_message)

                # Process tool calls
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_start = time.perf_counter()

                        # Parse arguments
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}

                        # Execute tool via MCP
                        try:
                            result = await call_tool(
                                tool_name=tool_call.function.name, arguments=arguments
                            )
                            tool_latency = int((time.perf_counter() - tool_start) * 1000)

                            # Track successful tool call
                            tool_calls.append(
                                ToolCallEvent(
                                    tool_name=tool_call.function.name,
                                    arguments=arguments,
                                    model=self.model,
                                    latency_ms=tool_latency,
                                )
                            )

                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call.function.name,
                                    "content": str(result),
                                }
                            )
                        except Exception as e:
                            # Track failed tool call
                            tool_latency = int((time.perf_counter() - tool_start) * 1000)
                            tool_calls.append(
                                ToolCallEvent(
                                    tool_name=tool_call.function.name,
                                    arguments=arguments,
                                    model=self.model,
                                    latency_ms=tool_latency,
                                )
                            )
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call.function.name,
                                    "content": f"Error: {str(e)}",
                                }
                            )

                # Continue conversation
                response = await self.client.chat.completions.create(
                    model=self.model, messages=messages, tools=adapter_mcp_tools, tool_choice="auto"
                )

            # Extract final response text
            response_text = response.choices[0].message.content or ""
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


class AsyncOpenAIAdapter(BaseAsyncOpenAIAdapter):
    def __init__(self, model="gpt-4-turbo"):
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        super().__init__(client, model)


class AsyncOpenAIOSSAdapter(BaseAsyncOpenAIAdapter):
    def __init__(self, model="gpt-oss-20b-ctx32k:latest", base_url=None, api_key=None):
        base_url = base_url or "http://localhost:11434/v1"
        api_key = api_key or os.environ.get("GPT_OSS_API_KEY", "ollama")
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        super().__init__(client, model)
