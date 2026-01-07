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


# def model_response_to_csv(responses: list[ModelResponse], csv_path: str, output_path: str):
#     """
#     Append model responses to the original CSV and save to output_ORIGINALNAME.

#     Args:
#         responses: List of ModelResponse objects
#         csv_path: Path to the original CSV file
#     """

#     # Read original CSV and write to new CSV with appended columns
#     with (
#         open(csv_path, "r", encoding="utf-8") as infile,
#         open(output_path, "w", encoding="utf-8", newline="") as outfile,
#     ):
#         reader = csv.DictReader(infile)
#         fieldnames = list(reader.fieldnames) + [
#             "model",
#             "session_id",
#             "tool_calls",
#             "tool_arguments",
#             "response_text",
#             "total_runtime_s",
#         ]
#         writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#         writer.writeheader()

#         # Read and append simultaneously
#         for row, response in zip(reader, responses):
#             row["model"] = response.model
#             row["session_id"] = response.session_id
#             row["tool_calls"] = response.tool_names
#             row["tool_arguments"] = response.tool_arguments
#             row["response_text"] = response.response_text
#             row["total_runtime_s"] = response.total_runtime_ms / 1000

#             writer.writerow(row)

#     print(f"Results saved to: {output_path}")
#     return output_path


# TODO: Make the csv fields a class/schema
def init_streaming_csv(csv_path: str, output_path: str):
    """
    Initialize CSV for streaming writes. Returns original rows and fieldnames.

    Args:
        csv_path: Path to the original CSV file
        output_path: Path to the output CSV file

    Returns:
        tuple: (original_rows, output_fieldnames)
    """
    # Read original CSV
    with open(csv_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fieldnames = list(reader.fieldnames)
        original_rows = list(reader)

    # Define output fieldnames
    output_fieldnames = original_fieldnames + [
        "model",
        "session_id",
        "tool_calls",
        "tool_arguments",
        "response_text",
        "total_runtime_s",
    ]

    # Initialize output CSV with headers
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()

    return original_rows, output_fieldnames


def append_response_to_csv(
    response: ModelResponse, original_row: dict, output_path: str, fieldnames: list[str]
):
    """
    Append a single model response to the CSV file.

    Args:
        response: ModelResponse object
        original_row: Original row from the input CSV
        output_path: Path to the output CSV file
        fieldnames: List of fieldnames for the CSV
    """
    with open(output_path, "a", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        row = original_row.copy()
        row["model"] = response.model
        row["session_id"] = response.session_id
        row["tool_calls"] = response.tool_names
        row["tool_arguments"] = response.tool_arguments
        row["response_text"] = response.response_text
        row["total_runtime_s"] = response.total_runtime_ms / 1000
        writer.writerow(row)
