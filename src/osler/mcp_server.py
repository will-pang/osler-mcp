import os
from pathlib import Path

import pandas as pd
import sqlparse
from fastmcp import FastMCP

import duckdb

from osler.config import get_default_database_path

# Create FastMCP server instance
mcp = FastMCP("osler")

# Global variables for backend configuration
_backend = None
_db_path = None
_bq_client = None
_project_id = None

def _validate_limit(limit: int) -> bool:
    """Validate limit parameter to prevent resource exhaustion."""
    return isinstance(limit, int) and 0 < limit <= 1000

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
        if statement_type not in (
            "SELECT"
        ):  
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
    
def _init_backend():
    """Initialize the backend based on environment variables."""
    global _backend, _db_path, _bq_client, _project_id

    _backend = os.getenv("OSLER_BACKEND", "duckdb")

    if _backend == "duckdb":
        _db_path = os.getenv("OSLER_DB_PATH")
        if not _db_path:
            # Use default database path
            _db_path = get_default_database_path("tuva-project-demo")

        # Ensure the database exists
        if not Path(_db_path).exists():
            raise FileNotFoundError(f"DuckDB database not found: {_db_path}")
    
_init_backend()

def _get_backend_info() -> str:
    """Get current backend information for display in responses."""
    if _backend == "duckdb":
        return f"🔧 **Current Backend:** DuckDB (local database)\n📁 **Database Path:** {_db_path}\n"
    
# ==========================================
# INTERNAL QUERY EXECUTION FUNCTIONS
# ==========================================
# These functions perform the actual database operations
# and are called by the MCP tools. This prevents MCP tools
# from calling other MCP tools, which violates the MCP protocol.

def _execute_duckdb_query(sql_query: str) -> str:
    """Execute SQLite query - internal function."""
    try:
        conn = duckdb.connect("osler_data/databases/tuva_project_demo.duckdb")
        try:
            df = conn.execute(sql_query).df()

            if df.empty:
                return "No results found"

            # Limit output size
            if len(df) > 50:
                result = df.head(50).to_string(index=False)
                result += f"\n... ({len(df)} total rows, showing first 50)"
            else:
                result = df.to_string(index=False)

            return result
        finally:
            conn.close()
    except Exception as e:
        # Re-raise the exception so the calling function can handle it with enhanced guidance
        raise e
    
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
        if _backend == "duckdb":
            return _execute_duckdb_query(sql_query)
        else:  # bigquery
            return _execute_duckdb_query(sql_query)
    except Exception as e:
        error_msg = str(e).lower()

        # Provide specific, actionable error guidance
        suggestions = []

        if "no such table" in error_msg or "table not found" in error_msg:
            suggestions.append(
                "🔍 **Table name issue:** Use `get_database_schema()` to see exact table names"
            )
            suggestions.append(
                f"📋 **Backend-specific naming:** {_backend} has specific table naming conventions"
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
            suggestions.append(
                "📝 **SQL syntax issue:** Check quotes, commas, and parentheses"
            )
            suggestions.append(
                f"🎯 **Backend syntax:** Verify your SQL works with {_backend}"
            )
            suggestions.append(
                "💭 **Try simpler:** Start with `SELECT * FROM table_name LIMIT 5`"
            )

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

📚 **Current Backend:** {_backend} - table names and syntax are backend-specific"""
    
# ==========================================
# MCP TOOLS - PUBLIC API
# ==========================================
# These are the tools exposed via MCP protocol.
# They should NEVER call other MCP tools - only internal functions.

@mcp.tool()
def get_database_schema() -> str:
    """🔍 Discover what data is available in the MIMIC-IV database.

    **When to use:** Start here when you need to understand what tables exist, or when someone asks about data that might be in multiple tables.

    **What this does:** Shows all available tables so you can identify which ones contain the data you need.

    **Next steps after using this:**
    - If you see relevant tables, use `get_table_info(table_name)` to explore their structure
    - Common tables: `patients` (demographics), `admissions` (hospital stays), `icustays` (ICU data), `labevents` (lab results)

    Returns:
        List of all available tables in the database with current backend info
    """
    if _backend == "duckdb":
        result_lst = []
        conn = duckdb.connect("osler_data/databases/tuva_project_demo.duckdb")
        schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchall()

        for schema in schemas:
            schema_name = schema[0]
            tables = conn.execute(
                f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}'"
            ).fetchall()

            if tables:
                for table in tables:
                    full_qualified_table_name = f"{schema_name}.{table[0]}"
                    result_lst.append(full_qualified_table_name)

        return f"{_get_backend_info()}\n📋 **Available Tables (query-ready names):**\n{'\n'.join(result_lst)}\n\n💡 **Copy-paste ready:** These table names can be used directly in your SQL queries!"
    
@mcp.tool()
def get_table_info(table_name: str, show_sample: bool = True) -> str:
    """📋 Explore a specific table's structure and see sample data.

    **When to use:** After you know which table you need (from `get_database_schema()`), use this to understand the columns and data format.

    **What this does:**
    - Shows column names, types, and constraints
    - Displays sample rows so you understand the actual data format
    - Helps you write accurate SQL queries

    **Pro tip:** Always look at sample data! It shows you the actual values, date formats, and data patterns.

    Args:
        table_name: Exact table name from the schema (case-sensitive). Can be simple name or fully qualified BigQuery name.
        show_sample: Whether to include sample rows (default: True, recommended)

    Returns:
        Complete table structure with sample data to help you write queries
    """
    backend_info = _get_backend_info()

    if _backend == "duckdb":
        # Get column information
        pragma_query = f"PRAGMA table_info({table_name})"
        try:
            result = _execute_duckdb_query(pragma_query)
            if "error" in result.lower():
                return f"{backend_info}❌ Table '{table_name}' not found. Use get_database_schema() to see available tables."

            info_result = f"{backend_info}📋 **Table:** {table_name}\n\n**Column Information:**\n{result}"

            if show_sample:
                sample_query = f"SELECT * FROM {table_name} LIMIT 3"
                sample_result = _execute_duckdb_query(sample_query)
                info_result += (
                    f"\n\n📊 **Sample Data (first 3 rows):**\n{sample_result}"
                )

            return info_result
        except Exception as e:
            return f"{backend_info}❌ Error examining table '{table_name}': {e}\n\n💡 Use get_database_schema() to see available tables."

@mcp.tool()
def execute_duckdb_query(sql_query: str) -> str:
    """🚀 Execute SQL queries to analyze MIMIC-IV data.

    **💡 Pro tip:** For best results, explore the database structure first!

    **Recommended workflow (especially for smaller models):**
    1. **See available tables:** Use `get_database_schema()` to list all tables
    2. **Examine table structure:** Use `get_table_info('table_name')` to see columns and sample data
    3. **Write your SQL query:** Use exact table/column names from exploration

    **Why exploration helps:**
    - Table names vary between backends (SQLite vs BigQuery)
    - Column names may be unexpected (e.g., age might be 'anchor_age')
    - Sample data shows actual formats and constraints

    Args:
        sql_query: Your SQL SELECT query (must be SELECT only)

    Returns:
        Query results or helpful error messages with next steps
    """
    return _execute_query_internal(sql_query)

@mcp.tool()
def get_average_cms_hcc_risk_score(patient_id: int | None = None, limit: int = 10) -> str:
    """🏥 Get ICU stay information and length of stay data.

    **⚠️ Note:** This is a convenience function that assumes standard MIMIC-IV table structure.
    **For reliable queries:** Use `get_database_schema()` → `get_table_info()` → `execute_mimic_query()` workflow.

    **What you'll get:** Patient IDs, admission times, length of stay, and ICU details.

    Args:
        patient_id: Specific patient ID to query (optional)
        limit: Maximum number of records to return (default: 10)

    Returns:
        ICU stay data as formatted text or guidance if table not found
    """
    # Security validation
    if not _validate_limit(limit):
        return "Error: Invalid limit. Must be a positive integer between 1 and 10000."

    # Try common ICU table names based on backend
    if _backend == "duckdb":
        query = f"""
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
3. `execute_mimic_query('your_sql')` ← Use exact names

This ensures compatibility across different MIMIC-IV setups."""

    return result

@mcp.tool()
def get_overall_readmission_rate(patient_id: int | None = None, limit: int = 10) -> str:
    """🏥 Get ICU stay information and length of stay data.

    **⚠️ Note:** This is a convenience function that assumes standard MIMIC-IV table structure.
    **For reliable queries:** Use `get_database_schema()` → `get_table_info()` → `execute_mimic_query()` workflow.

    **What you'll get:** Patient IDs, admission times, length of stay, and ICU details.

    Args:
        patient_id: Specific patient ID to query (optional)
        limit: Maximum number of records to return (default: 10)

    Returns:
        ICU stay data as formatted text or guidance if table not found
    """
    # Security validation
    if not _validate_limit(limit):
        return "Error: Invalid limit. Must be a positive integer between 1 and 10000."

    # Try common ICU table names based on backend
    if _backend == "duckdb":
        query = f"""
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
3. `execute_mimic_query('your_sql')` ← Use exact names

This ensures compatibility across different MIMIC-IV setups."""

    return result

def main():
    """Main entry point for MCP server."""
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()