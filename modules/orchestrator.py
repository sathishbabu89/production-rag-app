import logging
import time

from modules.llm_provider import LLMProvider
from modules.query_decomposer import QueryDecomposer
from modules.pipeline import RAGPipeline
from modules.schema import RAGRequest
from modules.query_classifier import QueryClassifier
from modules.text_to_sql import TextToSQL
from modules.sql_validator import SQLValidator
from modules.sql_executor import SQLExecutor

from modules.conversation_state import ConversationState
from modules.entity_extractor import EntityExtractor


class Orchestrator:

    def __init__(self):

        self.sql_generator = TextToSQL()
        self.pipeline = RAGPipeline()
        self.llm = LLMProvider()
        self.decomposer = QueryDecomposer()

        # -----------------------------
        # Conversation State
        # -----------------------------
        self.state = ConversationState()

    def update_conversation_entity(
        self,
        query: str
    ):
        """
        Update entity state only when
        a valid business entity is found.
        """

        entities = (
            EntityExtractor.extract_entities(
                query
            )
        )

        logging.info(
            f"Extracted Entities: {entities}"
        )

        if not entities:

            return

        INVALID_ENTITIES = {

            "Who",
            "What",
            "When",
            "Where",
            "Why",
            "How",
            "Explain",
            "Tell",
            "Show",
            "Describe"
        }

        for entity in entities:

            entity = entity.strip()

            if entity in INVALID_ENTITIES:

                continue

            self.state.update_entity(
                entity
            )

            logging.info(
                f"Conversation Entity Updated: "
                f"{entity}"
            )

            return

    # =================================================
    # Conversation Resolver
    # =================================================
    def resolve_query_context(
        self,
        query: str
    ):

        current_entity = (
            self.state.get_entity()
        )

        if not current_entity:

            return query

        query_lower = query.lower()

        # --------------------------------
        # Employee count
        # --------------------------------

        if (
            "employee count" in query_lower
            or "how many employees" in query_lower
        ):

            resolved = (
                f"Show employee count for "
                f"{current_entity}"
            )

            logging.info(
                f"Conversation Resolver: "
                f"{query} -> {resolved}"
            )

            return resolved

        # --------------------------------
        # Founder
        # --------------------------------

        if (
            "who founded" in query_lower
            or "founder" in query_lower
        ):

            resolved = (
                f"Who founded "
                f"{current_entity}"
            )

            logging.info(
                f"Conversation Resolver: "
                f"{query} -> {resolved}"
            )

            return resolved

        # --------------------------------
        # Founded year
        # --------------------------------

        if (
            "when was it founded" in query_lower
            or "when founded" in query_lower
        ):

            resolved = (
                f"When was "
                f"{current_entity} founded"
            )

            logging.info(
                f"Conversation Resolver: "
                f"{query} -> {resolved}"
            )

            return resolved

        # --------------------------------
        # Revenue
        # --------------------------------

        if "revenue" in query_lower:

            resolved = (
                f"Show revenue for "
                f"{current_entity}"
            )

            logging.info(
                f"Conversation Resolver: "
                f"{query} -> {resolved}"
            )

            return resolved

        # --------------------------------
        # Generic follow-up
        # --------------------------------

        FOLLOWUP_PHRASES = [

            "what about",
            "tell me more",
            "explain more",
            "more details",
            "can you elaborate"
        ]

        if any(
            phrase in query_lower
            for phrase in FOLLOWUP_PHRASES
        ):

            resolved = (
                f"{query} about "
                f"{current_entity}"
            )

            logging.info(
                f"Conversation Resolver: "
                f"{query} -> {resolved}"
            )

            return resolved

        return query

    # =================================================
    # Main Entry
    # =================================================
    def process_query(self, query: str):

        logging.info(f"Processing Query: {query}")

        start_time = time.time()

        diagnostics = {
            "original_query": query,
            "route": None,
            "decomposed_queries": {},
            "generated_sql": None,
            "sql_results": None,
            "rag_query": None,
            "sql_query_text": None,
            "latency_seconds": None,
            "entity": None
        }

        # =================================================
        # Step 1 — Entity Extraction (NEW FIXED FLOW)
        # =================================================
        # -----------------------------
        # Update Conversation State
        # -----------------------------

        self.update_conversation_entity(
            query
        )

        current_entity = (
            self.state.get_entity()
        )

        diagnostics["entity"] = (
            current_entity
        )

        logging.info(
            f"Current Entity State: "
            f"{current_entity}"
        )

        # =================================================
        # Step 2 — Resolve Conversation Context
        # =================================================
        resolved_query = self.resolve_query_context(query)

        # =================================================
        # Step 3 — Classification uses resolved query
        # =================================================
        route = QueryClassifier.classify_query(resolved_query)

        diagnostics["route"] = route
        logging.info(f"Selected Route: {route}")

        # =================================================
        # SQL ROUTE
        # =================================================
        if route == "SQL":

            logging.info("Executing SQL route...")

            sql_query = self.sql_generator.generate_sql(resolved_query)

            diagnostics["generated_sql"] = sql_query

            if not SQLValidator.validate_query(sql_query):

                diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

                return {
                    "route": route,
                    "error": "Unsafe SQL query blocked.",
                    "diagnostics": diagnostics
                }

            results = SQLExecutor.execute_query(sql_query)

            diagnostics["sql_results"] = results
            diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

            return {
                "route": route,
                "sql_query": sql_query,
                "results": results,
                "diagnostics": diagnostics
            }

        # =================================================
        # RAG ROUTE
        # =================================================
        elif route == "RAG":

            logging.info("Executing RAG route...")

            try:

                request = RAGRequest(query=resolved_query)

                diagnostics["rag_query"] = resolved_query

                response = self.pipeline.run(request)

                diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

                return {
                    "route": route,
                    "response": response,
                    "diagnostics": diagnostics
                }

            except Exception as e:

                logging.error(f"RAG Route Error: {e}")

                diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

                return {
                    "route": route,
                    "error": str(e),
                    "diagnostics": diagnostics
                }

        # =================================================
        # HYBRID ROUTE
        # =================================================
        elif route == "HYBRID":

            logging.info("Executing HYBRID route...")

            try:

                decomposed = self.decomposer.decompose_query(resolved_query)

                rag_query = decomposed.get("rag_query") or resolved_query
                sql_query_text = decomposed.get("sql_query") or resolved_query

                diagnostics["decomposed_queries"] = {
                    "rag_query": rag_query,
                    "sql_query": sql_query_text
                }

                diagnostics["rag_query"] = rag_query
                diagnostics["sql_query_text"] = sql_query_text

                # ---------------- RAG ----------------
                rag_response = self.pipeline.run(
                    RAGRequest(query=rag_query)
                )

                # ---------------- SQL ----------------
                sql_query = self.sql_generator.generate_sql(sql_query_text)

                diagnostics["generated_sql"] = sql_query

                sql_results = []

                if SQLValidator.validate_query(sql_query):

                    sql_results = SQLExecutor.execute_query(sql_query)

                diagnostics["sql_results"] = sql_results

                # ---------------- SYNTHESIS ----------------
                synthesis_prompt = f"""
You are an enterprise AI assistant.

RAG:
{rag_response.answer}

SQL:
{sql_results}

Combine both into a final response.
Do not hallucinate missing data.
"""

                final_answer = self.llm.generate(synthesis_prompt)

                diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

                return {
                    "route": route,
                    "rag_answer": rag_response.answer,
                    "sql_results": sql_results,
                    "final_answer": final_answer,
                    "diagnostics": diagnostics
                }

            except Exception as e:

                logging.error(f"HYBRID Route Error: {e}")

                diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

                return {
                    "route": route,
                    "error": str(e),
                    "diagnostics": diagnostics
                }

        # =================================================
        # fallback
        # =================================================
        diagnostics["latency_seconds"] = round(time.time() - start_time, 2)

        return {
            "error": "Unknown route",
            "diagnostics": diagnostics
        }