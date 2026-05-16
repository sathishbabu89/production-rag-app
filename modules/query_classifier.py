import logging


class QueryClassifier:

    @staticmethod
    def classify_query(
        query: str
    ):

        """
        Classify query into:
        - RAG
        - SQL
        - HYBRID
        """

        query_lower = query.lower()

        # -----------------------------
        # SQL keywords
        # -----------------------------

        sql_keywords = [

            "highest",
            "lowest",
            "revenue",
            "employee",
            "employees",
            "count",
            "average",
            "founded",
            "top",
            "list",
            "show"
        ]

        # -----------------------------
        # RAG keywords
        # -----------------------------

        rag_keywords = [

            "explain",
            "story",
            "journey",
            "philosophy",
            "vision",
            "background",
            "innovation"
        ]

        # -----------------------------
        # Detect intents
        # -----------------------------

        has_sql = any(

            keyword in query_lower

            for keyword in sql_keywords
        )

        has_rag = any(

            keyword in query_lower

            for keyword in rag_keywords
        )

        # -----------------------------
        # Classification
        # -----------------------------

        if has_sql and has_rag:

            route = "HYBRID"

        elif has_sql:

            route = "SQL"

        else:

            route = "RAG"

        logging.info(
            f"Query classified as: "
            f"{route}"
        )

        return route