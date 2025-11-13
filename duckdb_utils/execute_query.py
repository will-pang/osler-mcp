import duckdb

conn = duckdb.connect("osler_data/databases/tuva_project_demo.duckdb")

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

df = conn.execute(query).df()

print(df)
