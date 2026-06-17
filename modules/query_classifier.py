import logging


class QueryClassifier:

    """
    Query Classification

    Routes queries to:

    - RAG
    - SQL
    - HYBRID

    Classification is based on
    user intent rather than
    dataset-specific keywords.
    """

    # ---------------------------------
    # Structured / Metric Queries
    # ---------------------------------

    METRIC_KEYWORDS = {

        "count",
        "total",
        "average",
        "avg",
        "sum",
        "highest",
        "lowest",
        "maximum",
        "minimum",
        "max",
        "min",
        "top",
        "bottom",
        "revenue",
        "profit",
        "sales",
        "employee",
        "employees",
        "salary",
        "users",
        "transactions",
        "amount",
        "volume",
        "founded year",
        "year",
        "date",
        "number of",
        "how many",
        "founder",
        "founded"
    }

    # ---------------------------------
    # Narrative / Context Queries
    # ---------------------------------

    NARRATIVE_KEYWORDS = {

        "explain",
        "describe",
        "summarize",
        "summary",
        "story",
        "journey",
        "background",
        "history",
        "overview",
        "vision",
        "philosophy",
        "innovation",
        "why",
        "architecture",
        "workflow",
        "process",
        "flow",
        "approach",
        "strategy",
        "benefits",
        "advantages",
        "disadvantages",
        "comparison",
        "analysis",
        "how does",
        "how do",
        "how is"
    }

    # ---------------------------------
    # Action Words
    # ---------------------------------

    ACTION_KEYWORDS = {

        "show",
        "list",
        "display",
        "give"
    }

    @staticmethod
    def classify_query(
        query: str
    ):

        """
        Returns:
        - SQL
        - RAG
        - HYBRID
        """

        query_lower = query.lower().strip()

        # ---------------------------------
        # Detect metric intent
        # ---------------------------------

        has_metric = any(

            keyword in query_lower

            for keyword in (
                QueryClassifier
                .METRIC_KEYWORDS
            )
        )

        # ---------------------------------
        # Detect narrative intent
        # ---------------------------------

        has_narrative = any(

            keyword in query_lower

            for keyword in (
                QueryClassifier
                .NARRATIVE_KEYWORDS
            )
        )

        # ---------------------------------
        # Action words
        # ---------------------------------

        has_action = any(

            keyword in query_lower

            for keyword in (
                QueryClassifier
                .ACTION_KEYWORDS
            )
        )

        # ---------------------------------
        # Special Cases
        # ---------------------------------

        # Example:
        # Show employee count
        # List revenue
        # Give founder details

        if has_action and has_metric:

            route = "SQL"

        elif has_metric and has_narrative:

            route = "HYBRID"

        elif has_metric:

            route = "SQL"

        elif has_narrative:

            route = "RAG"

        else:

            # Safe default
            route = "RAG"

        logging.info(
            f"Query classified as: "
            f"{route}"
        )

        return route