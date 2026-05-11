import re


class EntityExtractor:

    # -------------------------------------------------
    # Non-entity stopwords
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
        "show"
    }

    @staticmethod
    def extract_entities(
        query: str
    ) -> list[str]:
        """
        Lightweight entity extraction
        using capitalized words
        with stopword filtering
        """

        if not query:

            return []

        raw_entities = re.findall(
            r"\b[A-Z][a-zA-Z0-9]+\b",
            query
        )

        cleaned_entities = []

        for entity in raw_entities:

            entity_lower = entity.lower()

            if entity_lower not in (
                EntityExtractor.STOPWORDS
            ):

                cleaned_entities.append(
                    entity_lower
                )

        return list(
            set(cleaned_entities)
        )