import os
import logging
import warnings


# Suppress HF warnings
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

# Logging cleanup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

warnings.filterwarnings("ignore")

import streamlit as st
import tempfile
import os
import time

from modules.orchestrator import (
    Orchestrator
)

from langsmith import Client


# -----------------------------
# LangSmith Initialization
# -----------------------------
os.environ["LANGCHAIN_TRACING_V2"] = "true"

client = Client()

print("✅ LangSmith tracing enabled")


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📄 Production RAG Chatbot")


# -----------------------------
# Initialize Pipeline
# -----------------------------

@st.cache_resource
def load_assistant():

    return Orchestrator()


assistant = load_assistant()


# -----------------------------
# PDF Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload your PDF",
    type="pdf"
)


if uploaded_file:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp_file:

        tmp_file.write(
            uploaded_file.read()
        )

        temp_path = tmp_file.name
    
    assistant.pipeline.ingest(
        temp_path
    )

    st.success(
        "PDF processed successfully!"
    )


# -----------------------------
# User Query Input
# -----------------------------
user_query = st.text_input(
    "Ask your question"
)


# -----------------------------
# User Query Processing
# -----------------------------
if user_query:

    try:

        response_container = st.empty()

        with st.spinner(
            "Processing query..."
        ):

            response = (
                assistant.process_query(
                    user_query
                )
            )

        # -----------------------------
        # SQL Route
        # -----------------------------

        if response["route"] == "SQL":

            response_container.markdown(
                "## 🗄 SQL Results"
            )

            response_container.write(

                response["results"]
            )

        # -----------------------------
        # RAG Route
        # -----------------------------

        elif response["route"] == "RAG":

            response_container.markdown(
                "## 📚 RAG Response"
            )

            response_container.markdown(

                response["response"].answer
            )

        # -----------------------------
        # HYBRID Route
        # -----------------------------

        elif response["route"] == "HYBRID":

            response_container.markdown(
                "## 🔥 Hybrid Response"
            )

            response_container.markdown(

                response["final_answer"]
            )

        # -----------------------------
        # Error Handling
        # -----------------------------

        else:

            response_container.write(
                response
            )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )