import duckdb

conn = duckdb.connect("osler_data/databases/tuva_project_demo.duckdb")

# Check schemas
schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
print("Available schemas:")
for schema in schemas:
    print(f"  - {schema[0]}")

# Check tables in each schema
print("\nTables by schema:")
for schema in schemas:
    schema_name = schema[0]
    tables = conn.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}'"
    ).fetchall()
    if tables:
        print(f"\n{schema_name}:")
        for table in tables:
            print(f"  - {table[0]}")

conn.close()
