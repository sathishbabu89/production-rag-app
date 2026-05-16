import logging

from modules.pipeline import (
    RAGPipeline
)

from modules.schema import (
    RAGRequest
)

from modules.query_classifier import (
    QueryClassifier
)

from modules.text_to_sql import (
    TextToSQL
)

from modules.sql_validator import (
    SQLValidator
)

from modules.sql_executor import (
    SQLExecutor
)


class Orchestrator:

    def __init__(self):

        self.sql_generator = (
            TextToSQL()
        )

        self.pipeline = RAGPipeline()

    def process_query(
        self,
        query: str
    ):

        logging.info(
            f"Processing Query: {query}"
        )

        # -----------------------------
        # Query Classification
        # -----------------------------

        route = (
            QueryClassifier.classify_query(
                query
            )
        )

        logging.info(
            f"Selected Route: {route}"
        )

        # -----------------------------
        # SQL Route
        # -----------------------------

        if route == "SQL":

            logging.info(
                "Executing SQL route..."
            )

            # -----------------------------
            # Generate SQL
            # -----------------------------

            sql_query = (
                self.sql_generator.generate_sql(
                    query
                )
            )

            # -----------------------------
            # Validate SQL
            # -----------------------------

            is_valid = (
                SQLValidator.validate_query(
                    sql_query
                )
            )

            if not is_valid:

                return {

                    "route": route,

                    "error": (
                        "Unsafe SQL query blocked."
                    )
                }

            # -----------------------------
            # Execute SQL
            # -----------------------------

            results = (
                SQLExecutor.execute_query(
                    sql_query
                )
            )

            return {

                "route": route,

                "sql_query": sql_query,

                "results": results
            }

        # -----------------------------
        # Placeholder Routes
        # -----------------------------

        elif route == "RAG":

            logging.info(
                "Executing RAG route..."
            )

            try:

                request = RAGRequest(
                    query=query
                )

                response = (
                    self.pipeline.run(
                        request
                    )
                )

                return {

                    "route": route,

                    "response": response
                }

            except Exception as e:

                logging.error(
                    f"RAG Route Error: {e}"
                )

                return {

                    "route": route,

                    "error": str(e)
                }

        elif route == "HYBRID":

            return {

                "route": route,

                "message": (
                    "HYBRID route "
                    "not implemented yet."
                )
            }

        # -----------------------------
        # Unknown Route
        # -----------------------------

        return {

            "error": "Unknown route"
        }