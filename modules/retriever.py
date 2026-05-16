from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langsmith import traceable
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    UnstructuredPDFLoader
)
from modules.pii_handler import PIIHandler
from modules.entity_extractor import EntityExtractor
from sentence_transformers import CrossEncoder
from config import Config

import os
import uuid
import logging
import pytesseract

# ---------------------------------
# Tesseract OCR Configuration
# ---------------------------------

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR"
)

TESSDATA_PATH = (
    r"C:\Program Files\Tesseract-OCR\tessdata"
)

os.environ["PATH"] += (
    os.pathsep + TESSERACT_PATH
)

os.environ["TESSDATA_PREFIX"] = (
    TESSDATA_PATH
)

pytesseract.pytesseract.tesseract_cmd = (
    rf"{TESSERACT_PATH}\tesseract.exe"
)



class Retriever:

    def __init__(self):

        logging.info("Initializing Retriever...")

        self.embedding = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL
        )

        logging.info("Loading cross-encoder reranker...")

        self.reranker = CrossEncoder(
            Config.RERANKER_MODEL
        )

        self.db = None
        self.collection_id = None
        self.bm25_retriever = None

    def load_existing(self):
        """
        Load existing Chroma DB if available.
        Useful after app restart.
        """

        if os.path.exists(Config.CHROMA_PATH):

            logging.info("Loading existing Chroma DB...")

            self.db = Chroma(
                persist_directory=Config.CHROMA_PATH,
                embedding_function=self.embedding
            )

    def ingest_pdf(self, file_path):
        """
        Ingest PDF into ChromaDB.

        Pipeline:
        PDF → Chunking → PII Redaction → Hybrid Indexing
        """

        logging.info(
            f"Starting PDF ingestion: {file_path}"
        )

        # -----------------------------
        # Load PDF
        # -----------------------------

        # -----------------------------
        # Try Fast Text Extraction
        # -----------------------------

        logging.info(
            "Attempting PyMuPDF extraction..."
        )

        loader = PyMuPDFLoader(file_path)

        documents = loader.load()

        combined_text = " ".join(
            doc.page_content
            for doc in documents
        )

        # -----------------------------
        # Validate Extraction Quality
        # -----------------------------

        MIN_TEXT_THRESHOLD = 200

        if len(combined_text.strip()) > MIN_TEXT_THRESHOLD:

            logging.info(
                "Document Type: text_pdf"
            )

            logging.info(
                "Parser Used: PyMuPDF"
            )

            logging.info(
                "OCR Used: False"
            )

        else:

            logging.warning(
                "PyMuPDF extraction weak."
            )

            logging.warning(
                "Falling back to OCR..."
            )

            loader = UnstructuredPDFLoader(
                file_path,
                strategy="hi_res"
            )

            documents = loader.load()

            logging.info(
                "Document Type: scanned_pdf"
            )

            logging.info(
                "Parser Used: OCR"
            )

            logging.info(
                "OCR Used: True"
            )

        logging.info(
            f"Loaded {len(documents)} pages from PDF"
        )

        # -----------------------------
        # Split into chunks
        # -----------------------------

        splitter = RecursiveCharacterTextSplitter(

            chunk_size=800,

            chunk_overlap=100,

            separators=[
                "\n# ",
                "\n## ",
                "\n### ",
                "\n\n",
                "\n- ",
                "\n• ",
                "\n",
                ". ",
                " "
            ]
        )

        docs = splitter.split_documents(documents)

        logging.info(
            f"Created {len(docs)} chunks"
        )

        # -----------------------------
        # PII Redaction
        # -----------------------------
        redacted_docs = []

        for doc in docs:

            redacted_content = PIIHandler.redact(
                doc.page_content
            )

            doc.page_content = redacted_content

            redacted_docs.append(doc)

        logging.info(
            "PII redaction completed"
        )

        # -----------------------------
        # BM25 Retriever
        # -----------------------------
        self.bm25_retriever = BM25Retriever.from_documents(
            redacted_docs
        )

        self.bm25_retriever.k = Config.TOP_K

        logging.info(
            "BM25 retriever initialized"
        )

        # -----------------------------
        # Create unique collection
        # -----------------------------
        self.collection_id = str(uuid.uuid4())

        logging.info(
            f"Creating Chroma collection: {self.collection_id}"
        )

        # -----------------------------
        # Store embeddings in Chroma
        # -----------------------------
        self.db = Chroma.from_documents(
            documents=redacted_docs,
            embedding=self.embedding,
            persist_directory=Config.CHROMA_PATH,
            collection_name=self.collection_id
        )

        self.db.persist()

        logging.info(
            "PDF ingestion completed successfully"
        )
        
    @traceable(name="Hybrid Retrieval")
    def retrieve(self, query: str):
        """
        Hybrid Retrieval Pipeline

        Steps:
        1. Semantic Retrieval (MMR)
        2. BM25 Retrieval
        3. Merge Results
        4. Deduplicate
        5. Entity-aware Boosting
        6. Cross-Encoder Reranking
        """

        if not self.db:

            logging.warning(
                "No active DB found. Attempting to load existing DB..."
            )

            self.load_existing()

        if not self.db:

            raise ValueError(
                "No vector database available. Please upload a PDF first."
            )

        logging.info(
            f"Running hybrid retrieval for query: {query}"
        )

        # -------------------------------------------------
        # Semantic Retrieval using MMR
        # -------------------------------------------------
        semantic_results = (
            self.db.max_marginal_relevance_search(
                query=query,
                k=Config.TOP_K,
                fetch_k=Config.MMR_FETCH_K,
                lambda_mult=Config.MMR_LAMBDA
            )
        )

        logging.info(
            f"MMR Semantic Results: "
            f"{len(semantic_results)}"
        )

        for idx, doc in enumerate(semantic_results):

            logging.info(
                f"MMR Chunk {idx + 1}: "
                f"{doc.page_content[:120]}"
            )

            logging.info(
                f"MMR Metadata {idx + 1}: "
                f"{doc.metadata}"
            )

        # -------------------------------------------------
        # BM25 Retrieval
        # -------------------------------------------------
        bm25_results = (
            self.bm25_retriever.invoke(
                query
            )
        )

        logging.info(
            f"BM25 Results: "
            f"{len(bm25_results)}"
        )

        # -------------------------------------------------
        # Merge Retrieval Results
        # -------------------------------------------------
        combined_results = (
            semantic_results + bm25_results
        )

        # -------------------------------------------------
        # Deduplicate Results
        # -------------------------------------------------
        unique_docs = []

        seen_content = set()

        for doc in combined_results:

            content = doc.page_content.strip()

            if content not in seen_content:

                unique_docs.append(doc)

                seen_content.add(content)

        logging.info(
            f"Unique Retrieved Chunks: "
            f"{len(unique_docs)}"
        )

        # -------------------------------------------------
        # Entity-aware Boosting
        # -------------------------------------------------
        entities = (
            EntityExtractor.extract_entities(
                query
            )
        )

        boosted_unique_docs = unique_docs

        if entities:

            logging.info(
                f"Detected entities: {entities}"
            )

            boosted_docs = []

            other_docs = []

            for doc in unique_docs:

                content_lower = (
                    doc.page_content.lower()
                )

                if any(
                    entity in content_lower
                    for entity in entities
                ):

                    boosted_docs.append(doc)

                else:

                    other_docs.append(doc)

            boosted_unique_docs = (
                boosted_docs + other_docs
            )

            logging.info(
                f"Entity boosted chunks: "
                f"{len(boosted_docs)}"
            )

        # -------------------------------------------------
        # Entity-prioritized candidate selection
        # -------------------------------------------------
        if entities:

            entity_docs = []

            fallback_docs = []

            for doc in boosted_unique_docs:

                content_lower = (
                    doc.page_content.lower()
                )

                if any(
                    entity in content_lower
                    for entity in entities
                ):

                    entity_docs.append(doc)

                else:

                    fallback_docs.append(doc)

            # -----------------------------------------
            # Prioritize entity-matching chunks
            # -----------------------------------------
            candidate_docs = (
                entity_docs[:5]
                +
                fallback_docs[:2]
            )

            logging.info(
                f"Entity candidate docs: "
                f"{len(entity_docs)}"
            )

            logging.info(
                f"Fallback candidate docs: "
                f"{len(fallback_docs)}"
            )

        else:

            candidate_docs = (
                boosted_unique_docs[:10]
            )

        logging.info(
            f"Candidate Docs for Reranking: "
            f"{len(candidate_docs)}"
        )

        # -------------------------------------------------
        # Cross-Encoder Reranking
        # -------------------------------------------------
        reranked_results = (
            self.rerank_documents(
                query,
                candidate_docs
            )
        )

        logging.info(
            f"Retrieved "
            f"{len(reranked_results)} "
            f"reranked chunks"
        )

        return reranked_results


    def rerank_documents(
        self,
        query,
        documents
    ):
        """
        Rerank retrieved documents using cross-encoder
        with:
        - Threshold filtering
        - Score gap filtering
        - Confidence-aware retrieval
        """

        logging.info(
            "Starting cross-encoder reranking..."
        )

        # -----------------------------
        # Build query-document pairs
        # -----------------------------

        pairs = [
            (query, doc.page_content)
            for doc in documents
        ]

        # -----------------------------
        # Predict reranker scores
        # -----------------------------

        scores = self.reranker.predict(
            pairs
        )

        # -----------------------------
        # Build scored docs
        # -----------------------------

        scored_docs = []

        for doc, score in zip(documents, scores):

            scored_docs.append({

                "document": doc,

                "score": float(score)
            })

        # -----------------------------
        # Sort by reranker score
        # -----------------------------

        reranked_docs = sorted(
            scored_docs,
            key=lambda x: x["score"],
            reverse=True
        )

        # -----------------------------
        # Log reranked results
        # -----------------------------

        for idx, item in enumerate(reranked_docs):

            logging.info(
                f"Reranked {idx+1} | "
                f"Score: {item['score']:.4f} | "
                f"{item['document'].page_content[:120]}"
            )

        # -----------------------------
        # Threshold Filtering
        # -----------------------------

        filtered_docs = [

            item

            for item in reranked_docs

            if item["score"] >=
            Config.RERANKER_SCORE_THRESHOLD
        ]

        logging.info(
            f"Chunks after threshold filtering: "
            f"{len(filtered_docs)}"
        )

        # -----------------------------
        # Safety Fallback
        # -----------------------------

        if len(filtered_docs) < Config.MIN_RERANKED_RESULTS:

            logging.warning(
                "Threshold removed all chunks. "
                "Using top reranked result."
            )

            filtered_docs = [
                reranked_docs[0]
            ]

        # -----------------------------
        # Score Gap Filtering
        # -----------------------------

        if (
            Config.ENABLE_SCORE_GAP_FILTERING
            and len(filtered_docs) >= 2
        ):

            top_score = (
                filtered_docs[0]["score"]
            )

            second_score = (
                filtered_docs[1]["score"]
            )

            score_gap = (
                top_score - second_score
            )

            logging.info(
                f"Top Score: "
                f"{top_score:.4f}"
            )

            logging.info(
                f"Second Score: "
                f"{second_score:.4f}"
            )

            logging.info(
                f"Score Gap: "
                f"{score_gap:.4f}"
            )

            if (
                score_gap >=
                Config.RERANKER_SCORE_GAP_THRESHOLD
            ):

                logging.info(
                    "Large score gap detected. "
                    "Returning only top chunk."
                )

                filtered_docs = [
                    filtered_docs[0]
                ]

        # -----------------------------
        # Final Documents
        # -----------------------------

        final_docs = [

            item["document"]

            for item in filtered_docs[
                :Config.TOP_K
            ]
        ]

        logging.info(
            f"Retrieved "
            f"{len(final_docs)} "
            f"reranked chunks"
        )

        return final_docs