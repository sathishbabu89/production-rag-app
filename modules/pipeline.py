from modules.schema import RAGRequest, RAGResponse
from modules.llm_provider import LLMProvider
from modules.prompt_manager import PromptManager
from modules.retriever import Retriever
from modules.guardrails import Guardrails
from modules.retry_fallback import RetryFallbackHandler
from modules.pii_handler import PIIHandler
from modules.cost_tracker import CostTracker
from modules.query_rewriter import QueryRewriter

from langchain_core.output_parsers import PydanticOutputParser
from langsmith import traceable
import logging

class RAGPipeline:

    def __init__(self):

        self.llm = LLMProvider()

        self.prompt_manager = PromptManager()

        self.retriever = Retriever()

        self.parser = PydanticOutputParser(
            pydantic_object=RAGResponse
        )

        self.retry_handler = RetryFallbackHandler()

        self.cost_tracker = CostTracker()

        self.query_rewriter = QueryRewriter(
            self.llm
        )

    def run(self, request: RAGRequest) -> RAGResponse:
        """
        Public entry point.

        IMPORTANT:
        PII sanitization happens BEFORE tracing.
        """

        # -----------------------------
        # Redact PII from user query
        # -----------------------------
        safe_query = PIIHandler.redact(
            request.query
        )

        # -----------------------------
        # Validate sanitized query
        # -----------------------------
        Guardrails.validate_query(
            safe_query
        )

        # -----------------------------
        # Execute traced pipeline
        # -----------------------------
        return self._execute_pipeline(
            safe_query
        )

    @traceable(name="RAG Pipeline Execution")
    def _execute_pipeline(
        self,
        safe_query: str
    ) -> RAGResponse:
        """
        Internal traceable pipeline execution.
        Only sanitized data reaches LangSmith.
        """

        # -----------------------------
        # Query Rewriting
        # -----------------------------
        rewritten_query = self.query_rewriter.rewrite(
            safe_query
        )

        # -----------------------------
        # Retrieval
        # -----------------------------
        docs = self.retriever.retrieve(
            rewritten_query
        )

        logging.info(
            f"Using rewritten query for retrieval: "
            f"{rewritten_query}"
        )

        # -----------------------------
        # Build retrieval context
        # -----------------------------
        raw_context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        # -----------------------------
        # Sanitize retrieved context
        # -----------------------------
        context = Guardrails.sanitize_context(
            raw_context
        )

        # -----------------------------
        # Collect unique sources
        # -----------------------------
        sources = list(
            set(
                [
                    doc.metadata.get(
                        "source",
                        "unknown"
                    )
                    for doc in docs
                ]
            )
        )

        # -----------------------------
        # Create prompt
        # -----------------------------
        prompt = self.prompt_manager.format(
            context,
            safe_query
        )

        # -----------------------------
        # Structured prompt
        # -----------------------------
        structured_prompt = f"""
        {prompt}

        Please respond in valid JSON format as:
        {{
            "answer": "<answer text>",
            "sources": {sources},
            "confidence": <float between 0 and 1>
        }}
        """

        # -----------------------------
        # Start cost tracking
        # -----------------------------
        self.cost_tracker.start()

        try:

            # -----------------------------
            # LLM Generation
            # -----------------------------
            raw_output = self.retry_handler.execute(
                "LLM Generation",
                self.llm.generate,
                structured_prompt
            )

            # -----------------------------
            # Parse structured output
            # -----------------------------
            response = self.retry_handler.execute(
                "Output Parsing",
                self.parser.parse,
                raw_output
            )

            return response

        finally:

            # -----------------------------
            # Stop cost tracking
            # -----------------------------
            self.cost_tracker.stop()

            # -----------------------------
            # Log metrics
            # -----------------------------
            self.cost_tracker.log_metrics(
                structured_prompt,
                raw_output if 'raw_output' in locals() else ""
            )

    def ingest(self, file_path: str):
        """
        PDF ingestion entry point.
        """

        self.retriever.ingest_pdf(
            file_path
        )