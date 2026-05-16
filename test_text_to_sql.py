from modules.text_to_sql import (
    TextToSQL
)

from modules.sql_validator import (
    SQLValidator
)

from modules.sql_executor import (
    SQLExecutor
)

# -----------------------------
# User Question
# -----------------------------

question = (
    "Which company has highest revenue?"
)

# -----------------------------
# Generate SQL
# -----------------------------

generator = TextToSQL()

sql_query = generator.generate_sql(
    question
)

print("\nGenerated SQL:\n")

print(sql_query)

# -----------------------------
# Validate SQL
# -----------------------------

is_valid = (
    SQLValidator.validate_query(
        sql_query
    )
)

print("\nSQL Valid:")

print(is_valid)

# -----------------------------
# Execute SQL
# -----------------------------

if is_valid:

    results = (
        SQLExecutor.execute_query(
            sql_query
        )
    )

    print("\nSQL Results:\n")

    print(results)

else:

    print(
        "\nSQL execution blocked."
    )