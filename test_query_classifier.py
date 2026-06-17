from modules.query_classifier import QueryClassifier


test_cases = [

    {
        "query": "Explain Zoho story",
        "expected": "RAG"
    },

    {
        "query": "Which company has highest revenue?",
        "expected": "SQL"
    },

    {
        "query": "Explain Infosys story and employee count",
        "expected": "HYBRID"
    },

    {
        "query": "Show employee count",
        "expected": "SQL"
    },

    {
        "query": "Explain UPI settlement process",
        "expected": "RAG"
    },

    {
        "query": "What is the revenue and explain business model",
        "expected": "HYBRID"
    }
]


passed = 0
failed = 0


for test in test_cases:

    query = test["query"]

    expected = test["expected"]

    actual = QueryClassifier.classify_query(query)

    print("\n========================")

    print("Query   :", query)
    print("Expected:", expected)
    print("Actual  :", actual)

    if actual == expected:

        print("Result  : PASS ✅")
        passed += 1

    else:

        print("Result  : FAIL ❌")
        failed += 1


print("\n========================")
print("TOTAL PASSED:", passed)
print("TOTAL FAILED:", failed)
print("========================")