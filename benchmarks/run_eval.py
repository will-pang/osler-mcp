import asyncio

from benchmarks.models.qwen_adapters import AsyncQwenAdapter
from benchmarks.utils import csv_to_benchmark_queries, get_mcp_tools, model_response_to_csv
from src.osler.config import get_project_root

EVAL_FILE_PATH = "benchmarks/evals/tuva_project_demo/"
# MODEL_NAME = "gpt-oss-20b-ctx32k:latest"
# MODEL_NAME = "gpt-4-turbo"
# MODEL_NAME = "claude-sonnet-4-5-20250929"
MODEL_NAME = "qwen2.5:7b-ctx32k"


async def main():
    # Step 1: Get MCP tools using utils
    all_tools = await get_mcp_tools()

    # Step 2: Load benchmark queries from CSV
    csv_path = get_project_root() / EVAL_FILE_PATH / "input_small.csv"
    output_path = get_project_root() / EVAL_FILE_PATH / f"output_{MODEL_NAME}.csv"
    benchmark_queries = csv_to_benchmark_queries(csv_path)

    # Step 3: Load tool policy
    tool_policy_path = get_project_root() / "benchmarks/prompts/tool_policy.md"
    with open(tool_policy_path, "r") as f:
        tool_policy = f.read()

    # Step 4: Choose Model
    # adapter = AsyncOpenAIAdapter(model=MODEL_NAME)
    # adapter = AsyncOpenAIOSSAdapter(model=MODEL_NAME)
    # adapter = AsyncClaudeAdapter(model=MODEL_NAME)
    adapter = AsyncQwenAdapter(model=MODEL_NAME)

    # Step 5: Iterate over each benchmark query and collect responses
    responses = []
    for idx, benchmark_query in enumerate(benchmark_queries, start=1):
        # Inject tool policy into the prompt
        full_prompt = f"{tool_policy}\n\n{benchmark_query.query}"
        print(f"Printing full prompt: {full_prompt}")
        response = await adapter.run(prompt=full_prompt, tools=all_tools)

        responses.append(response)

    # Step 5: Save responses to CSV
    model_response_to_csv(responses, csv_path, output_path)


if __name__ == "__main__":
    asyncio.run(main())
