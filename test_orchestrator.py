from modules.orchestrator import (
    Orchestrator
)

assistant = Orchestrator()

assistant.pipeline.ingest(

    "evaluation_docs/"
    "Top_10_Indian_Business_Success_Stories_Expanded_5_Pages.pdf"
)

queries = [

    "Which company has highest revenue?",

    "Explain Zoho story",

    "Explain Zoho story and show employee count"
]

for query in queries:

    print("\n===================")

    print(f"\nQuery: {query}")

    response = (
        assistant.process_query(
            query
        )
    )

    print("\nFINAL RESPONSE:\n")

    print(response)