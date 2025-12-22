import pytest
from fastmcp import Client

from osler.mcp_server import mcp


class TestMCPTools:
    """Test MCP tools functionality. Note that this uses real data for now, will refactor
    with fake data later on.
    """

    @pytest.mark.asyncio
    async def test_tools_via_client(self):
        """Test MCP tools through the FastMCP client."""

        # Test via FastMCP client
        async with Client(mcp) as client:
            # Test execute_query tool
            result = await client.call_tool(
                "execute_query",
                {
                    "sql_query": """
                 SELECT COUNT(*) as count FROM 
                    (SELECT * FROM chronic_conditions.tuva_chronic_conditions_long LIMIT 10)
                 """
                },
            )
            result_text = str(result)
            assert "count" in result_text.lower()
            assert "10" in result_text
