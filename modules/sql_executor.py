import sqlite3
import logging


class SQLExecutor:

    DB_PATH = (
        "structured_data/"
        "business_metrics.db"
    )

    @staticmethod
    def execute_query(query: str):

        """
        Execute SQL query safely.
        """

        logging.info(
            f"Executing SQL Query: {query}"
        )

        try:

            conn = sqlite3.connect(
                SQLExecutor.DB_PATH
            )

            cursor = conn.cursor()

            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [

                description[0]

                for description in
                cursor.description
            ]

            conn.close()

            results = []

            for row in rows:

                results.append(
                    dict(zip(columns, row))
                )

            logging.info(
                f"Returned "
                f"{len(results)} rows"
            )

            return results

        except Exception as e:

            logging.error(
                f"SQL Execution Error: {e}"
            )

            return []