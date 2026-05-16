from modules.sql_executor import (
    SQLExecutor
)

query = """

SELECT *
FROM company_metrics

"""

results = SQLExecutor.execute_query(
    query
)

print(results)