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


def model_response_to_csv(responses: list[ModelResponse], csv_path: str, output_path: str):
    """
    Append model responses to the original CSV and save to output_ORIGINALNAME.

    Args:
        responses: List of ModelResponse objects
        csv_path: Path to the original CSV file
    """

    # Read original CSV and write to new CSV with appended columns
    with (
        open(csv_path, "r", encoding="utf-8") as infile,
        open(output_path, "w", encoding="utf-8", newline="") as outfile,
    ):
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames) + [
            "model",
            "session_id",
            "tool_calls",
            "tool_arguments",
            "response_text",
            "total_latency_s",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Read and append simultaneously
        for row, response in zip(reader, responses):
            row["model"] = response.model
            row["session_id"] = response.session_id
            row["tool_calls"] = response.tool_names
            row["tool_arguments"] = response.tool_arguments
            row["response_text"] = response.response_text
            row["total_latency_s"] = response.total_latency_ms / 1000

            writer.writerow(row)

    print(f"Results saved to: {output_path}")
    return output_path
