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
            result_text = str(result.structured_content)
            assert "count" in result_text.lower()
            assert "10" in result_text

            # Test get_table_info
            result = await client.call_tool(
                "get_table_info",
                {
                    "table_name": "chronic_conditions.tuva_chronic_conditions_long",
                    "show_sample": False,
                },
            )
            result_text = str(result.structured_content)
            assert "person_id" in result_text
            assert "condition" in result_text
            assert "first_diagnosis_date" in result_text
            assert "last_diagnosis_date" in result_text
            assert "tuva_last_run" in result_text

            # Test get_model_lineage tool
            result = await client.call_tool(
                "get_model_lineage",
                {
                    "table_name": "chronic_conditions__tuva_chronic_conditions_long",
                    "direction": "parent",
                    "depth": 1,
                },
            )
            result_text = str(result.structured_content)
            assert "tuva_chronic_conditions__stg_core__condition" in result_text
