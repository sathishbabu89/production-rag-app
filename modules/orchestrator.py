import logging

from modules.llm_provider import (
    LLMProvider
)

from modules.query_decomposer import (
    QueryDecomposer
)

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

        self.llm = LLMProvider()

        self.decomposer = (
            QueryDecomposer()
        )

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

            logging.info(
                "Executing HYBRID route..."
            )

            try:

                # -----------------------------
                # Query Decomposition
                # -----------------------------

                decomposed = (
                    self.decomposer
                    .decompose_query(query)
                )

                rag_query = (
                    decomposed["rag_query"]
                )

                sql_query_text = (
                    decomposed["sql_query"]
                )

                # -----------------------------
                # Fallback Safety
                # -----------------------------

                if not rag_query:

                    rag_query = query

                if not sql_query_text:

                    sql_query_text = query

                logging.info(
                    f"RAG Query: {rag_query}"
                )

                logging.info(
                    f"SQL Query: {sql_query_text}"
                )

                # -----------------------------
                # RAG Retrieval
                # -----------------------------

                request = RAGRequest(
                    query=rag_query
                )

                rag_response = (
                    self.pipeline.run(
                        request
                    )
                )

                # -----------------------------
                # SQL Retrieval
                # -----------------------------

                sql_query = (
                    self.sql_generator.generate_sql(                        
                        sql_query_text
                    )
                )

                is_valid = (
                    SQLValidator.validate_query(
                        sql_query
                    )
                )

                sql_results = []

                if is_valid:

                    sql_results = (
                        SQLExecutor.execute_query(
                            sql_query
                        )
                    )

                else:

                    logging.warning(
                        "SQL validation failed "
                        "inside HYBRID route."
                    )

                # -----------------------------
                # Build Combined Prompt
                # -----------------------------

                synthesis_prompt = f"""

        You are an enterprise AI assistant.

        Combine the following:

        RAG Narrative:
        {rag_response.answer}

        SQL Results:
        {sql_results}

        Generate a single unified response.

        IMPORTANT:
        - Use the RAG narrative for explanations
        - Use SQL results for exact metrics
        - Do not hallucinate missing data
        - Clearly combine both information sources

        """

                # -----------------------------
                # Final LLM Synthesis
                # -----------------------------

                final_answer = (
                    self.llm.generate(
                        synthesis_prompt
                    )
                )

                return {

                    "route": route,

                    "rag_answer": (
                        rag_response.answer
                    ),

                    "sql_results": sql_results,

                    "final_answer": final_answer
                }

            except Exception as e:

                logging.error(
                    f"HYBRID Route Error: {e}"
                )

                return {

                    "route": route,

                    "error": str(e)
                }

        # -----------------------------
        # Unknown Route
        # -----------------------------

        return {

            "error": "Unknown route"
        }