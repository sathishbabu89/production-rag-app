import logging

from modules.llm_provider import (
    LLMProvider
)


class TextToSQL:

    def __init__(self):

        self.llm = LLMProvider()

    def generate_sql(
        self,
        question: str
    ):

        logging.info(
            f"Generating SQL for: {question}"
        )

        prompt = f"""

You are an expert SQLite SQL generator.

Convert the user question into a valid SQLite SELECT query.

IMPORTANT RULES:
- Only generate SELECT queries
- Do NOT generate DELETE, UPDATE, DROP, INSERT
- Use ONLY this table:

Table: company_metrics

Columns:
- company_name
- founder
- revenue_billion
- employee_count
- founded_year

Return ONLY SQL query.
No explanation.
No markdown.
No ```.

User Question:
{question}

SQL Query:

"""

        sql_query = self.llm.generate(
            prompt
        )

        sql_query = sql_query.strip()

        logging.info(
            f"Generated SQL: {sql_query}"
        )

        return sql_query