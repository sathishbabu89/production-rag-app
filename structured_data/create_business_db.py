import sqlite3

# -----------------------------
# Connect SQLite DB
# -----------------------------

conn = sqlite3.connect(
    "structured_data/business_metrics.db"
)

cursor = conn.cursor()

# -----------------------------
# Create Normalized Table
# -----------------------------

cursor.execute("""

CREATE TABLE IF NOT EXISTS company_metrics (

    company_name TEXT,

    founder TEXT,

    revenue_billion REAL,

    employee_count INTEGER,

    founded_year INTEGER
)

""")

# -----------------------------
# Insert Normalized Data
# -----------------------------

companies = [

    (
        "Reliance Industries",
        "Dhirubhai Ambani",
        124.0,
        403303,
        1966
    ),

    (
        "Tata Group",
        "Ratan Tata",
        160.0,
        1151353,
        1868
    ),

    (
        "Infosys",
        "N. R. Narayana Murthy",
        20.1,
        328594,
        1981
    ),

    (
        "Wipro",
        "Azim Premji",
        10.8,
        230000,
        1945
    ),

    (
        "Myntra",
        "Mukesh Bansal",
        0.72,
        10000,
        2007
    ),

    (
        "BYJU'S",
        "Byju Raveendran",
        0.56,
        19377,
        2011
    ),

    (
        "Paytm",
        "Vijay Shekhar Sharma",
        1.01,
        15000,
        2010
    ),

    (
        "Nykaa",
        "Falguni Nayar",
        1.87,
        5000,
        2012
    ),

    (
        "Ola",
        "Bhavish Aggarwal",
        0.35,
        4000,
        2010
    ),

    (
        "Zoho",
        "Sridhar Vembu",
        1.62,
        17000,
        1996
    )
]

# -----------------------------
# Insert Data
# -----------------------------

cursor.executemany("""

INSERT INTO company_metrics
VALUES (?, ?, ?, ?, ?)

""", companies)

# -----------------------------
# Commit & Close
# -----------------------------

conn.commit()

conn.close()

print(
    "Normalized business_metrics.db created successfully!"
)