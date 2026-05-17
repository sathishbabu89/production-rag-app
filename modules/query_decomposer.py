import logging

from modules.llm_provider import (
    LLMProvider
)


class QueryDecomposer:

    def __init__(self):

        self.llm = LLMProvider()

    def decompose_query(
        self,
        query: str
    ):

        """
        Decompose hybrid query into:
        - RAG query
        - SQL query
        """

        logging.info(
            f"Decomposing query: {query}"
        )

        prompt = f"""

You are an expert enterprise AI planner.

Split the user query into:

1. RAG_QUERY
- narrative/explanation part

2. SQL_QUERY
- structured analytics/data part

IMPORTANT:
- Return BOTH fields
- Keep them concise
- Preserve original intent

User Query:
{query}

Output Format:

RAG_QUERY: <text>

SQL_QUERY: <text>

"""

        response = self.llm.generate(
            prompt
        )

        logging.info(
            f"Decomposition Output: "
            f"{response}"
        )

        # -----------------------------
        # Simple Parsing
        # -----------------------------

        rag_query = ""
        sql_query = ""

        for line in response.splitlines():

            if line.startswith(
                "RAG_QUERY:"
            ):

                rag_query = (
                    line.replace(
                        "RAG_QUERY:",
                        ""
                    )
                    .strip()
                )

            elif line.startswith(
                "SQL_QUERY:"
            ):

                sql_query = (
                    line.replace(
                        "SQL_QUERY:",
                        ""
                    )
                    .strip()
                )

        return {

            "rag_query": rag_query,

            "sql_query": sql_query
        }