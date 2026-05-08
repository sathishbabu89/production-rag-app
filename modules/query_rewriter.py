from langsmith import traceable

import logging


class QueryRewriter:

    def __init__(self, llm):

        self.llm = llm

    @traceable(name="Query Rewriting")
    def rewrite(
        self,
        query: str
    ) -> str:
        """
        Rewrite user query to improve retrieval quality
        """

        logging.info(
            f"Original Query: {query}"
        )

        prompt = f"""
        You are a query rewriting assistant for a RAG system.

        Your task is to rewrite the user query
        to improve semantic retrieval quality.

        Rules:
        - Preserve original intent
        - Add missing semantic clarity
        - Make query retrieval-friendly
        - Keep it concise
        - Do NOT answer the query

        User Query:
        {query}

        Rewritten Query:
        """

        rewritten_query = self.llm.generate(
            prompt
        )

        rewritten_query = rewritten_query.strip()

        logging.info(
            f"Rewritten Query: {rewritten_query}"
        )

        return rewritten_query