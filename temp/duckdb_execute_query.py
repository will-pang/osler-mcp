from pathlib import Path

import duckdb

conn = duckdb.connect("osler_data/databases/tuva_project_demo.duckdb")

query = Path(
    "benchmarks/evals/tuva_project_demo/golden_query/exclusion_reason_breakdown.sql"
).read_text()

# query = """
# select
#       hcc_code
#     , hcc_description
#     , count(*) as gap_count
# from hcc_suspecting.list
# group by
#       hcc_code
#     , hcc_description
# order by
#       hcc_code
#     , hcc_description
# """

df = conn.execute(query).df()

print(df)
