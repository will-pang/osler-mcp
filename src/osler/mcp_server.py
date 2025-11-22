import os

import sqlparse
from fastmcp import FastMCP

from osler.config import get_default_database_path
from osler.database.duckdb_client import DuckDB

# ---------------------------------------------------------
# Initialize backend
# ---------------------------------------------------------
_backend_name = os.getenv("OSLER_BACKEND", "duckdb")

if _backend_name == "duckdb":
    _db_path = os.getenv("OSLER_DB_PATH") or get_default_database_path("tuva-project-demo")
    backend = DuckDB(_db_path)
else:
    raise ValueError(f"Unsupported backend: {_backend_name}")

mcp = FastMCP("osler")

# ---------------------------------------------------------
# Security validation
# ---------------------------------------------------------


def _is_safe_query(sql_query: str, internal_tool: bool = False) -> tuple[bool, str]:
    """Secure SQL validation - blocks injection attacks, allows legitimate queries."""
    try:
        if not sql_query or not sql_query.strip():
            return False, "Empty query"

        # Parse SQL to validate structure
        parsed = sqlparse.parse(sql_query.strip())
        if not parsed:
            return False, "Invalid SQL syntax"

        # Block multiple statements (main injection vector)
        if len(parsed) > 1:
            return False, "Multiple statements not allowed"

        statement = parsed[0]
        statement_type = statement.get_type()

        # Allow SELECT and PRAGMA (PRAGMA is needed for schema exploration)
        if statement_type not in ("SELECT"):
            return False, "Only SELECT queries allowed"

        sql_upper = sql_query.strip().upper()

        # For SELECT statements, block dangerous injection patterns
        if statement_type == "SELECT":
            # Block dangerous write operations within SELECT
            dangerous_keywords = {
                "INSERT",
                "UPDATE",
                "DELETE",
                "DROP",
                "CREATE",
                "ALTER",
                "TRUNCATE",
                "REPLACE",
                "MERGE",
                "EXEC",
                "EXECUTE",
            }

            for keyword in dangerous_keywords:
                if f" {keyword} " in f" {sql_upper} ":
                    return False, f"Write operation not allowed: {keyword}"

            # Block common injection patterns that are rarely used in legitimate analytics
            injection_patterns = [
                # Classic SQL injection patterns
                ("1=1", "Classic injection pattern"),
                ("OR 1=1", "Boolean injection pattern"),
                ("AND 1=1", "Boolean injection pattern"),
                ("OR '1'='1'", "String injection pattern"),
                ("AND '1'='1'", "String injection pattern"),
                ("WAITFOR", "Time-based injection"),
                ("SLEEP(", "Time-based injection"),
                ("BENCHMARK(", "Time-based injection"),
                ("LOAD_FILE(", "File access injection"),
                ("INTO OUTFILE", "File write injection"),
                ("INTO DUMPFILE", "File write injection"),
            ]

            for pattern, description in injection_patterns:
                if pattern in sql_upper:
                    return False, f"Injection pattern detected: {description}"

            # Context-aware protection: Block suspicious table/column names not in medical databases
            suspicious_names = [
                "PASSWORD",
                "ADMIN",
                "USER",
                "LOGIN",
                "AUTH",
                "TOKEN",
                "CREDENTIAL",
                "SECRET",
                "KEY",
                "HASH",
                "SALT",
                "SESSION",
                "COOKIE",
            ]

            for name in suspicious_names:
                if name in sql_upper:
                    return (
                        False,
                        f"Suspicious identifier detected: {name} (not medical data)",
                    )

        return True, "Safe"

    except Exception as e:
        return False, f"Validation error: {e}"


# ==========================================
# INTERNAL QUERY EXECUTION FUNCTIONS
# ==========================================
# These functions perform the actual database operations
# and are called by the MCP tools. This prevents MCP tools
# from calling other MCP tools, which violates the MCP protocol.


def _execute_query_internal(sql_query: str) -> str:
    """Internal query execution function that handles backend routing."""
    # Security check
    is_safe, message = _is_safe_query(sql_query)
    if not is_safe:
        if "describe" in sql_query.lower() or "show" in sql_query.lower():
            return f"""❌ **Security Error:** {message}

        🔍 **For table structure:** Use `get_table_info('table_name')` instead of DESCRIBE
        📋 **Why this is better:** Shows columns, types, AND sample data to understand the actual data

        💡 **Recommended workflow:**
        1. `get_database_schema()` ← See available tables
        2. `get_table_info('table_name')` ← Explore structure
        3. `execute_mimic_query('SELECT ...')` ← Run your analysis"""

        return f"❌ **Security Error:** {message}\n\n💡 **Tip:** Only SELECT statements are allowed for data analysis."

    try:
        return backend.execute_query(sql_query)
    except Exception as e:
        error_msg = str(e).lower()

        suggestions = []

        if "no such table" in error_msg or "table not found" in error_msg:
            suggestions.append(
                "🔍 **Table name issue:** Use `get_database_schema()` to see exact table names"
            )
            suggestions.append(
                f"📋 **Backend-specific naming:** {_backend_name} has specific table naming conventions"
            )
            suggestions.append(
                "💡 **Quick fix:** Check if the table name matches exactly (case-sensitive)"
            )

        if "no such column" in error_msg or "column not found" in error_msg:
            suggestions.append(
                "🔍 **Column name issue:** Use `get_table_info('table_name')` to see available columns"
            )
            suggestions.append(
                "📝 **Common issue:** Column might be named differently (e.g., 'anchor_age' not 'age')"
            )
            suggestions.append(
                "👀 **Check sample data:** `get_table_info()` shows actual column names and sample values"
            )

        if "syntax error" in error_msg:
            suggestions.append("📝 **SQL syntax issue:** Check quotes, commas, and parentheses")
            suggestions.append(f"🎯 **Backend syntax:** Verify your SQL works with {_backend_name}")
            suggestions.append("💭 **Try simpler:** Start with `SELECT * FROM table_name LIMIT 5`")

        if "describe" in error_msg.lower() or "show" in error_msg.lower():
            suggestions.append(
                "🔍 **Schema exploration:** Use `get_table_info('table_name')` instead of DESCRIBE"
            )
            suggestions.append(
                "📋 **Better approach:** `get_table_info()` shows columns AND sample data"
            )

        if not suggestions:
            suggestions.append(
                "🔍 **Start exploration:** Use `get_database_schema()` to see available tables"
            )
            suggestions.append(
                "📋 **Check structure:** Use `get_table_info('table_name')` to understand the data"
            )

        suggestion_text = "\n".join(f"   {s}" for s in suggestions)

        return f"""❌ **Query Failed:** {e}

🛠️ **How to fix this:**
{suggestion_text}

🎯 **Quick Recovery Steps:**
1. `get_database_schema()` ← See what tables exist
2. `get_table_info('your_table')` ← Check exact column names
3. Retry your query with correct names

📚 **Current Backend:** {_backend_name} - table names and syntax are backend-specific"""


# ==========================================
# MCP TOOLS - PUBLIC API
# ==========================================
# These are the tools exposed via MCP protocol.
# They should NEVER call other MCP tools - only internal functions.


@mcp.tool()
def get_database_schema() -> str:
    tables = backend.get_schema()

    return f"{_backend_name}\n📋 **Available Tables (query-ready names):**\n{'\n'.join(tables)}\n\n💡 **Copy-paste ready:** These table names can be used directly in your SQL queries!"


@mcp.tool()
def get_table_info(table_name: str, show_sample: bool = True) -> str:
    return backend.get_table_info(table_name, show_sample=show_sample)


@mcp.tool()
def execute_query(sql_query: str) -> str:
    """🚀 Execute SQL queries to analyze data.

    **💡 Pro tip:** For best results, explore the database structure first!

    **Recommended workflow (especially for smaller models):**
    1. **See available tables:** Use `get_database_schema()` to list all tables
    2. **Examine table structure:** Use `get_table_info('table_name')` to see columns and sample data
    3. **Write your SQL query:** Use exact table/column names from exploration

    **Why exploration helps:**
    - Column names may be unexpected (e.g., age might be 'anchor_age')
    - Sample data shows actual formats and constraints

    Args:
        sql_query: Your SQL SELECT query (must be SELECT only)

    Returns:
        Query results or helpful error messages with next steps
    """
    return _execute_query_internal(sql_query)


@mcp.tool()
def get_average_cms_hcc_risk_score() -> str:
    """Get Average CMS-HCC Risk Scores

    **For reliable queries:** Use `get_database_schema()` → `get_table_info()` → `execute_duckdb_query()` workflow.

    Args:

    Returns:
        Average CMS-HCC Risk Scores
    """
    if _backend_name == "duckdb":
        query = """
        select
            count(distinct person_id) as patient_count
            , avg(blended_risk_score) as average_blended_risk_score
            , avg(normalized_risk_score) as average_normalized_risk_score
            , avg(payment_risk_score) as average_payment_risk_score
        from cms_hcc.patient_risk_scores
        """

    # Execute with error handling that suggests proper workflow
    result = _execute_query_internal(query)
    if "error" in result.lower() or "not found" in result.lower():
        return f"""❌ **Convenience function failed:** {result}

💡 **For reliable results, use the proper workflow:**
1. `get_database_schema()` ← See actual table names
2. `get_table_info('table_name')` ← Understand structure
3. `execute_duckdb_query('your_sql')` ← Use exact names

This ensures compatibility across different MIMIC-IV setups."""

    return result


@mcp.tool()
def get_overall_readmission_rate() -> str:
    """🏥 Get overall readmission rate

    **For reliable queries:** Use `get_database_schema()` → `get_table_info()` → `execute_duckdb_query()` workflow.

    Args:

    Returns:
        Overall readmission rate
    """
    if _backend_name == "duckdb":
        query = """
        select 
            (select count(*)
            from readmissions.readmission_summary
            where index_admission_flag = 1 and unplanned_readmit_30_flag = 1) * 100
            /
            (select count(*)
            from readmissions.readmission_summary
            where index_admission_flag = 1) as overall_readmission_rate
        """

    # Execute with error handling that suggests proper workflow
    result = _execute_query_internal(query)
    if "error" in result.lower() or "not found" in result.lower():
        return f"""❌ **Convenience function failed:** {result}

💡 **For reliable results, use the proper workflow:**
1. `get_database_schema()` ← See actual table names
2. `get_table_info('table_name')` ← Understand structure
3. `execute_query('your_sql')` ← Use exact names

"""
    return result


def main():
    """Main entry point for MCP server."""
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
