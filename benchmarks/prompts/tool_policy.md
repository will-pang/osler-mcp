Tool dependency order:
1. get_database_schema must be called before any other tool if schema is unknown
2. get_table_info must be called before execute_query when columns are uncertain
3. execute_query is only allowed after schema and table details are confirmed

Workflow:
- Identify missing information
- Call the appropriate tool
- Validate assumptions
- Then proceed