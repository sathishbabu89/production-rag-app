import logging

from pathlib import Path

from modules.evaluation_dataset import (
    EVALUATION_DATASET
)

from modules.pipeline import (
    RAGPipeline
)


class RetrievalEvaluator:

    def __init__(self):

        # -----------------------------------------
        # Initialize pipeline
        # -----------------------------------------
        self.pipeline = RAGPipeline()

        # -----------------------------------------
        # Load evaluation PDF
        # -----------------------------------------
        evaluation_pdf = Path(
            "evaluation_docs/"
            "Top_10_Indian_Business_Success_Stories_Expanded_5_Pages.pdf"
        )

        if not evaluation_pdf.exists():

            raise FileNotFoundError(
                f"Evaluation PDF not found: "
                f"{evaluation_pdf}"
            )

        logging.info(
            "Ingesting evaluation PDF..."
        )

        self.pipeline.ingest(
            str(evaluation_pdf)
        )

    def evaluate(self):

        total_queries = len(
            EVALUATION_DATASET
        )

        hit_count = 0

        precision_scores = []

        recall_scores = []

        mrr_scores = []

        # -----------------------------------------
        # Run evaluation query-by-query
        # -----------------------------------------
        for sample in EVALUATION_DATASET:

            query = sample["query"]

            expected_entities = (
                sample["expected_entities"]
            )

            logging.info(
                f"\nEvaluating Query: {query}"
            )

            # -----------------------------------------
            # Retrieve documents
            # -----------------------------------------
            retrieved_docs = (
                self.pipeline.retriever.retrieve(
                    query
                )
            )

            retrieved_text = [
                doc.page_content.lower()
                for doc in retrieved_docs
            ]

            # -----------------------------------------
            # Relevance Detection
            # -----------------------------------------
            relevant_positions = []

            relevant_count = 0

            for idx, text in enumerate(
                retrieved_text
            ):

                if any(
                    entity in text
                    for entity in expected_entities
                ):

                    relevant_count += 1

                    relevant_positions.append(
                        idx + 1
                    )

            # -----------------------------------------
            # Precision@K
            # -----------------------------------------
            precision_at_k = (
                relevant_count /
                len(retrieved_docs)
            ) if retrieved_docs else 0

            precision_scores.append(
                precision_at_k
            )

            # -----------------------------------------
            # Recall@K
            # -----------------------------------------
            recall_at_k = (
                relevant_count /
                len(expected_entities)
            )

            recall_at_k = min(
                recall_at_k,
                1.0
            )

            recall_scores.append(
                recall_at_k
            )

            # -----------------------------------------
            # Hit Rate
            # -----------------------------------------
            hit = relevant_count > 0

            if hit:

                hit_count += 1

            # -----------------------------------------
            # Mean Reciprocal Rank (MRR)
            # -----------------------------------------
            if relevant_positions:

                reciprocal_rank = (
                    1 /
                    relevant_positions[0]
                )

            else:

                reciprocal_rank = 0

            mrr_scores.append(
                reciprocal_rank
            )

            # -----------------------------------------
            # Query-level logs
            # -----------------------------------------
            logging.info(
                f"Relevant Chunks: "
                f"{relevant_count}"
            )

            logging.info(
                f"Precision@K: "
                f"{precision_at_k:.2f}"
            )

            logging.info(
                f"Recall@K: "
                f"{recall_at_k:.2f}"
            )

            logging.info(
                f"MRR: "
                f"{reciprocal_rank:.2f}"
            )

        # -----------------------------------------
        # Final Aggregate Metrics
        # -----------------------------------------
        avg_precision = (
            sum(precision_scores)
            /
            total_queries
        )

        avg_recall = (
            sum(recall_scores)
            /
            total_queries
        )

        hit_rate = (
            hit_count
            /
            total_queries
        )

        avg_mrr = (
            sum(mrr_scores)
            /
            total_queries
        )

        # -----------------------------------------
        # Final Report
        # -----------------------------------------
        print("\n")

        print(
            "===================================="
        )

        print(
            " Retrieval Evaluation Metrics "
        )

        print(
            "===================================="
        )

        print(
            f"Precision@K : "
            f"{avg_precision:.2f}"
        )

        print(
            f"Recall@K    : "
            f"{avg_recall:.2f}"
        )

        print(
            f"Hit Rate    : "
            f"{hit_rate:.2f}"
        )

        print(
            f"MRR         : "
            f"{avg_mrr:.2f}"
        )

        print(
            "===================================="
        )