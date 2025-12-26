import asyncio

from benchmarks.models.openai_adapter import AsyncOpenAIAdapter
from benchmarks.utils import csv_to_benchmark_queries, get_mcp_tools, model_response_to_csv
from src.osler.config import get_project_root


async def main():
    # Step 1: Get MCP tools using utils
    all_tools = await get_mcp_tools()

    # Step 2: Load benchmark queries from CSV
    csv_path = get_project_root() / "benchmarks/evals/tuva_health_demo_questions.csv"
    output_path = get_project_root() / "benchmarks/evals/output_tuva_health_demo_questions.csv"
    benchmark_queries = csv_to_benchmark_queries(csv_path)

    # Step 3: Choose Model
    adapter = AsyncOpenAIAdapter(model="gpt-4-turbo")

    # Step 4: Iterate over each benchmark query and collect responses
    responses = []
    for idx, benchmark_query in enumerate(benchmark_queries, start=1):
        response = await adapter.run(prompt=benchmark_query.query, tools=all_tools)

        responses.append(response)
        print(f"Response ({idx}): {response.response_text}\n\n\n")

    # Step 5: Save responses to CSV
    model_response_to_csv(responses, csv_path, output_path)


if __name__ == "__main__":
    asyncio.run(main())
