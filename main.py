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

from modules.pipeline import RAGPipeline
from modules.schema import RAGRequest

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
pipeline = RAGPipeline()


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

    pipeline.ingest(temp_path)

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
# Streaming Response
# -----------------------------
if user_query:

    try:

        response_container = st.empty()

        streamed_text = ""

        
        for chunk in pipeline.stream_answer(
            user_query
        ):

            streamed_text += chunk

            response_container.markdown(
                streamed_text + "▌"
            )

            time.sleep(0.01)

        response_container.markdown(
            streamed_text
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )