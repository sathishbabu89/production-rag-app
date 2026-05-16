from modules.query_classifier import (
    QueryClassifier
)

queries = [

    "Explain Zoho story",

    "Which company has highest revenue?",

    "Explain Infosys story and employee count"
]

for query in queries:

    route = (
        QueryClassifier.classify_query(
            query
        )
    )

    print("\nQuery:")

    print(query)

    print("Route:")

    print(route)