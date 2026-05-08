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

from modules.pipeline import RAGPipeline
from modules.schema import RAGRequest
from langsmith import Client
# -----------------------------
# LangSmith Initialization
# -----------------------------
os.environ["LANGCHAIN_TRACING_V2"] = "true"

client = Client()

print("✅ LangSmith tracing enabled")

st.title("📄 Production RAG Chatbot")

pipeline = RAGPipeline()

# 📂 Upload PDF
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    with st.spinner("Processing PDF..."):
        pipeline.ingest(temp_path)

    st.success("✅ PDF processed successfully!")

# 💬 Chat
query = st.text_input("Ask your question")

if query:
    request = RAGRequest(query=query)
    try:
        response = pipeline.run(request)

        st.write("### Answer")
        st.write(response.answer)

        st.write("### Sources")
        for src in response.sources:
            st.write(f"- {src}")

    except ValueError as e:
        st.error(f"🚨 Security Alert: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")