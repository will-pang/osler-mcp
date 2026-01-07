import csv

from fastmcp import Client

from benchmarks.schema import BenchmarkQueries, ModelResponse
from osler.mcp_server import mcp


async def get_mcp_tools():
    """Connect to MCP server and retrieve tools."""
    async with Client(mcp) as client:
        return await client.list_tools()


async def call_tool(tool_name: str, arguments: dict):
    """Connect to MCP server and retrieve tools."""
    async with Client(mcp) as client:
        return await client.call_tool(name=tool_name, arguments=arguments)


def csv_to_benchmark_queries(csv_path: str) -> list[BenchmarkQueries]:
    """
    Example: csv_to_json("/Users/wpang/Desktop/GitHub/osler-mcp/benchmarks/evals/tuva_health_demo_questions.csv")
    """
    queries = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = BenchmarkQueries(query=row["Query"])
            queries.append(query)

    return queries


def init_streaming_csv(csv_path: str, output_path: str):
    with open(csv_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fieldnames = list(reader.fieldnames)
        original_rows = list(reader)

    output_fieldnames = original_fieldnames + ModelResponse.CSV_FIELDS

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()

    return original_rows, output_fieldnames


def append_response_to_csv(
    response: ModelResponse,
    original_row: dict,
    output_path: str,
    fieldnames: list[str],
):
    with open(output_path, "a", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        row = {
            **original_row,
            **response.to_csv_row(),
        }

        writer.writerow(row)
