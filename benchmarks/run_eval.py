import asyncio

from benchmarks.models.openai_adapters import AsyncOpenAIOSSAdapter
from benchmarks.utils import (
    append_response_to_csv,
    csv_to_benchmark_queries,
    get_mcp_tools,
    initialize_response_to_csv,
)
from src.osler.config import get_project_root

EVAL_FILE_PATH = "benchmarks/evals/tuva_project_demo/"
OUTPUT_FOLDER = "2026-01-06"

MODEL_NAME = "gpt-oss-20b-ctx32k:latest"
# MODEL_NAME = "gpt-4-turbo"
# MODEL_NAME = "claude-sonnet-4-5-20250929"
# MODEL_NAME = "qwen2.5:7b-ctx32k"


async def main():
    # Step 1: Get MCP tools using utils
    all_tools = await get_mcp_tools()

    # Step 2: Load benchmark queries from CSV
    csv_path = get_project_root() / EVAL_FILE_PATH / "qsheet.csv"
    output_path = get_project_root() / EVAL_FILE_PATH / OUTPUT_FOLDER / f"output_{MODEL_NAME}.csv"
    benchmark_queries = csv_to_benchmark_queries(csv_path)

    # Step 3: Load tool policy
    tool_policy_path = get_project_root() / "benchmarks/prompts/tool_policy.md"
    with open(tool_policy_path, "r") as f:
        tool_policy = f.read()

    # Step 4: Choose Model
    # adapter = AsyncOpenAIAdapter(model=MODEL_NAME)
    adapter = AsyncOpenAIOSSAdapter(model=MODEL_NAME)
    # adapter = AsyncClaudeAdapter(model=MODEL_NAME)
    # adapter = AsyncQwenAdapter(model=MODEL_NAME)

    # Step 5: Initialize streaming CSV and iterate over queries
    original_rows, fieldnames = initialize_response_to_csv(csv_path, output_path)

    for idx, (benchmark_query, original_row) in enumerate(
        zip(benchmark_queries, original_rows), start=1
    ):
        # Inject tool policy into the prompt
        full_prompt = f"{tool_policy}\n\n{benchmark_query.query}"
        print(f"Processing query {idx}/{len(benchmark_queries)}")
        print(f"Full prompt: {full_prompt}")

        response = await adapter.run(prompt=full_prompt, tools=all_tools)

        # Write response to CSV immediately after receiving it
        append_response_to_csv(response, original_row, output_path, fieldnames)

    print(f"All results saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
