from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import BM25Retriever
from langsmith import traceable
from modules.pii_handler import PIIHandler
from sentence_transformers import CrossEncoder
from config import Config

import os
import uuid
import logging


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
        loader = PyPDFLoader(file_path)

        documents = loader.load()

        logging.info(
            f"Loaded {len(documents)} pages from PDF"
        )

        # -----------------------------
        # Split into chunks
        # -----------------------------
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
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
        Hybrid Retrieval:
        Semantic Search + BM25 Search
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

        # -----------------------------
        # Semantic Retrieval
        # -----------------------------
        semantic_results = self.db.max_marginal_relevance_search(
            query=query,
            k=Config.TOP_K,
            fetch_k=Config.MMR_FETCH_K,
            lambda_mult=Config.MMR_LAMBDA
        )

        logging.info(            
            f"MMR Semantic Results: {len(semantic_results)}"
        )

        for idx, doc in enumerate(semantic_results):
            logging.info(
                f"MMR Chunk {idx+1}: "
                f"{doc.page_content[:120]}"
            )

        # -----------------------------
        # BM25 Retrieval
        # -----------------------------
        bm25_results = self.bm25_retriever.invoke(
            query
        )

        logging.info(
            f"BM25 Results: {len(bm25_results)}"
        )

        # -----------------------------
        # Merge Results
        # -----------------------------
        combined_results = (
            semantic_results + bm25_results
        )

        # -----------------------------
        # Deduplicate Results
        # -----------------------------
        unique_docs = []

        seen_content = set()

        for doc in combined_results:

            if doc.page_content not in seen_content:

                unique_docs.append(doc)

                seen_content.add(doc.page_content)

        # -----------------------------
        # Limit reranker candidates
        # -----------------------------
        candidate_docs = unique_docs[:10]

        # -----------------------------
        # Cross-Encoder Reranking
        # -----------------------------
        reranked_results = self.rerank_documents(
            query,
            candidate_docs
        )

        logging.info(
            f"Retrieved {len(reranked_results)} reranked chunks"
        )

        return reranked_results


    def rerank_documents(
        self,
        query,
        documents
    ):
        """
        Rerank retrieved documents using cross-encoder
        """

        logging.info(
            "Starting cross-encoder reranking..."
        )

        pairs = [
            (query, doc.page_content)
            for doc in documents
        ]

        scores = self.reranker.predict(
            pairs
        )

        reranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        reranked_docs = [
            doc for doc, score in reranked
        ]

        for idx, (doc, score) in enumerate(reranked):

            logging.info(
                f"Reranked {idx+1} | "
                f"Score: {score:.4f} | "
                f"{doc.page_content[:120]}"
            )

        return reranked_docs[:Config.TOP_K]