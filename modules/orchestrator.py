import logging
import time

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

        start_time = time.time()

        diagnostics = {

            "original_query": query,

            "route": None,

            "decomposed_queries": {},

            "generated_sql": None,

            "sql_results": None,

            "rag_query": None,

            "sql_query_text": None,

            "latency_seconds": None
        }

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

        diagnostics["route"] = route

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

                end_time = time.time()

                diagnostics["latency_seconds"] = round(

                    end_time - start_time,

                    2
                )

                return {

                    "route": route,

                    "error": (
                        "Unsafe SQL query blocked."
                    ),

                    "diagnostics": diagnostics
                }

            # -----------------------------
            # Execute SQL
            # -----------------------------

            results = (
                SQLExecutor.execute_query(
                    sql_query
                )
            )

            end_time = time.time()

            diagnostics["latency_seconds"] = round(

                end_time - start_time,

                2
            )

            return {

                "route": route,

                "sql_query": sql_query,

                "results": results,

                "diagnostics": diagnostics
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

                diagnostics["rag_query"] = (
                    query
                )

                response = (
                    self.pipeline.run(
                        request
                    )
                )

                end_time = time.time()

                diagnostics["latency_seconds"] = round(

                    end_time - start_time,

                    2
                )

                return {

                    "route": route,

                    "response": response,

                    "diagnostics": diagnostics
                }

            except Exception as e:

                logging.error(
                    f"RAG Route Error: {e}"
                )

                end_time = time.time()

                diagnostics["latency_seconds"] = round(

                    end_time - start_time,

                    2
                )

                return {

                    "route": route,

                    "error": str(e),

                    "diagnostics": diagnostics
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

                diagnostics["decomposed_queries"] = {

                    "rag_query": rag_query,

                    "sql_query": sql_query_text
                }

                diagnostics["rag_query"] = (
                    rag_query
                )

                diagnostics["sql_query_text"] = (
                    sql_query_text
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

                diagnostics["rag_query"] = (
                    query
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

                diagnostics["generated_sql"] = (
                    sql_query
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

                    diagnostics["sql_results"] = (
                        sql_results
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

                end_time = time.time()

                diagnostics["latency_seconds"] = round(

                    end_time - start_time,

                    2
                )

                return {

                    "route": route,

                    "rag_answer": (
                        rag_response.answer
                    ),

                    "sql_results": sql_results,

                    "final_answer": final_answer,

                    "diagnostics": diagnostics
                }

            except Exception as e:

                logging.error(
                    f"HYBRID Route Error: {e}"
                )

                end_time = time.time()

                diagnostics["latency_seconds"] = round(

                    end_time - start_time,

                    2
                )

                return {

                    "route": route,

                    "error": str(e),

                    "diagnostics": diagnostics
                }

        # -----------------------------
        # Unknown Route
        # -----------------------------

        end_time = time.time()

        diagnostics["latency_seconds"] = round(

            end_time - start_time,

            2
        )

        return {

            "error": "Unknown route"
        }