import logging
import re

from langsmith import traceable


class QueryRewriter:

    # -----------------------------
    # Tunable thresholds
    # -----------------------------
    VERY_SHORT_THRESHOLD = 3

    PRONOUN_CONTEXT_THRESHOLD = 8

    VAGUE_PHRASE_THRESHOLD = 6

    # -----------------------------
    # Ambiguous pronouns
    # -----------------------------
    AMBIGUOUS_PRONOUNS = {
        "it",
        "they",
        "this",
        "that",
        "these",
        "those"
    }

    # -----------------------------
    # Conversational vague phrases
    # -----------------------------
    VAGUE_PHRASES = [
        "tell me more",
        "explain more",
        "can you elaborate",
        "what happened next",
        "what about",
        "how about"
    ]

    # -----------------------------
    # Generic code / syntax indicators
    # Helps avoid unnecessary rewriting
    # for already-specific technical queries
    # -----------------------------
    CODE_INDICATORS = [
        "select ",
        "def ",
        "class ",
        "```",
        "{",
        "};",
        "import ",
        "function ",
        "api ",
        "sql ",
        "json"
    ]

    def __init__(self, llm):

        self.llm = llm

    def should_rewrite(
        self,
        query: str
    ) -> bool:
        """
        Determine whether query rewriting
        is actually necessary.
        """

        # -----------------------------
        # Input validation
        # -----------------------------
        if query is None:

            logging.warning(
                "Selective Rewrite: Query is None"
            )

            return False

        query = query.strip()

        if len(query) == 0:

            logging.warning(
                "Selective Rewrite: Blank query"
            )

            return False

        # -----------------------------
        # Normalize query
        # -----------------------------
        query_lower = query.lower()

        # -----------------------------
        # Tokenize safely
        # Handles punctuation better
        # -----------------------------
        tokens = re.findall(
            r"\b\w+\b",
            query_lower
        )

        # -----------------------------
        # Skip rewriting for
        # syntax-heavy technical queries
        # -----------------------------
        if any(
            indicator in query_lower
            for indicator in self.CODE_INDICATORS
        ):

            logging.info(
                "Selective Rewrite: "
                "Code/syntax query detected - skipping rewrite"
            )

            return False

        # -----------------------------
        # Very short queries
        # Usually ambiguous
        # -----------------------------
        if len(tokens) <= self.VERY_SHORT_THRESHOLD:

            logging.info(
                "Selective Rewrite: "
                "Very short query detected"
            )

            return True

        # -----------------------------
        # Pronoun ambiguity
        # Only trigger when query
        # is relatively short
        # -----------------------------
        pronoun_count = sum(
            1
            for token in tokens
            if token in self.AMBIGUOUS_PRONOUNS
        )

        if (
            pronoun_count > 0
            and len(tokens)
            <= self.PRONOUN_CONTEXT_THRESHOLD
        ):

            logging.info(
                "Selective Rewrite: "
                "Ambiguous pronoun query detected"
            )

            return True

        # -----------------------------
        # Conversational vague phrases
        # Only for shorter queries
        # to reduce false positives
        # -----------------------------
        has_vague_phrase = any(
            phrase in query_lower
            for phrase in self.VAGUE_PHRASES
        )

        if (
            has_vague_phrase
            and len(tokens)
            <= self.VAGUE_PHRASE_THRESHOLD
        ):

            logging.info(
                "Selective Rewrite: "
                "Vague conversational query detected"
            )

            return True

        # -----------------------------
        # Query already appears
        # retrieval-friendly
        # -----------------------------
        logging.info(
            "Selective Rewrite: "
            "Skipping rewrite"
        )

        return False

    @traceable(name="Query Rewriting")
    def rewrite(
        self,
        query: str
    ) -> str:
        """
        Rewrite user query
        only when necessary.
        """

        # -----------------------------
        # Decide whether rewriting
        # is actually needed
        # -----------------------------
        if not self.should_rewrite(query):

            return query

        logging.info(
            f"Original Query: {query}"
        )

        prompt = f"""
        You are a query rewriting assistant
        for a RAG system.

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

        rewritten_query = (
            self.llm.generate(prompt)
        )

        rewritten_query = (
            rewritten_query.strip()
        )

        logging.info(
            f"Rewritten Query: "
            f"{rewritten_query}"
        )

        logging.info(
            f"Selective Rewrite Decision: "
            f"{self.should_rewrite(query)}"
        )

        return rewritten_query