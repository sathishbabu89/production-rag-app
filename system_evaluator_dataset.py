SYSTEM_EVAL_DATASET = [

    {
        "query": "Explain Nykaa story",
        "expected_route": "RAG",
        "expected_answer_contains": "Falguni"
    },

    {
        "query": "Show employee count",
        "expected_route": "SQL",
        "expected_sql": "employee_count"
    },

    {
        "query": "Explain Infosys story and employee count",
        "expected_route": "HYBRID",
        "expected_sql": "employee_count",
        "expected_answer_contains": "Infosys"
    },

    {
        "query": "What is revenue of Tata Group",
        "expected_route": "SQL",
        "expected_sql": "revenue"
    }
]