from modules.query_decomposer import (
    QueryDecomposer
)

decomposer = QueryDecomposer()

query = (
    "Explain Zoho story "
    "and show employee count"
)

result = (
    decomposer.decompose_query(
        query
    )
)

print("\nDECOMPOSED QUERY:\n")

print(result)