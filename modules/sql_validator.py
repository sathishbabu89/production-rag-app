import logging


class SQLValidator:

    @staticmethod
    def validate_query(
        query: str
    ):

        """
        Validate generated SQL query
        for safety.
        """

        query_upper = (
            query.upper()
        )

        # -----------------------------
        # Allow only SELECT
        # -----------------------------

        if not query_upper.strip().startswith(
            "SELECT"
        ):

            logging.warning(
                "Rejected non-SELECT query"
            )

            return False

        # -----------------------------
        # Block dangerous keywords
        # -----------------------------

        blocked_keywords = [

            "DELETE",
            "DROP",
            "UPDATE",
            "INSERT",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "REPLACE"
        ]

        for keyword in blocked_keywords:

            if keyword in query_upper:

                logging.warning(
                    f"Blocked SQL keyword: "
                    f"{keyword}"
                )

                return False

        # -----------------------------
        # Prevent multiple statements
        # -----------------------------

        if query.count(";") > 1:

            logging.warning(
                "Multiple SQL statements blocked"
            )

            return False

        logging.info(
            "SQL query validated successfully"
        )

        return True