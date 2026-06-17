import re


class EntityExtractor:

    # -------------------------------------------------
    # Non-entity words
    # -------------------------------------------------

    STOPWORDS = {

        "explain",
        "tell",
        "story",
        "about",
        "what",
        "why",
        "how",
        "when",
        "where",
        "more",
        "find",
        "information",
        "describe",
        "details",
        "give",
        "show",

        # Follow-up query words

        "who",
        "founded",
        "founder",
        "employee",
        "employees",
        "count",
        "revenue",
        "year",
        "company"
    }

    @staticmethod
    def extract_entities(
        query: str
    ) -> list[str]:
        """
        Extract likely business entities
        from user query.

        Examples:

        Explain Nykaa story
        -> ["Nykaa"]

        Who founded Nykaa
        -> ["Nykaa"]

        Explain Zoho story
        -> ["Zoho"]

        What about employee count?
        -> []
        """

        if not query:

            return []

        # -------------------------------------------------
        # Extract multi-word capitalized phrases
        # -------------------------------------------------

        raw_entities = re.findall(

            r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",

            query
        )

        cleaned_entities = []

        for entity in raw_entities:

            entity = entity.strip()

            # -------------------------------------------------
            # Split phrase into words
            # -------------------------------------------------

            parts = entity.split()

            # -------------------------------------------------
            # Remove stopwords
            # -------------------------------------------------

            filtered_parts = [

                part

                for part in parts

                if part.lower()
                not in EntityExtractor.STOPWORDS
            ]

            # -------------------------------------------------
            # Entire phrase removed
            # -------------------------------------------------

            if not filtered_parts:

                continue

            entity = " ".join(
                filtered_parts
            )

            # -------------------------------------------------
            # Ignore tiny fragments
            # -------------------------------------------------

            if len(entity) <= 2:

                continue

            cleaned_entities.append(
                entity
            )

        # -------------------------------------------------
        # Deduplicate while preserving order
        # -------------------------------------------------

        unique_entities = []

        seen = set()

        for entity in cleaned_entities:

            if entity not in seen:

                unique_entities.append(
                    entity
                )

                seen.add(entity)

        return unique_entities