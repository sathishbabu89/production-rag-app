import logging

from pathlib import Path

from modules.pipeline import (
    RAGPipeline
)

from modules.technical_evaluation_dataset import (
    TECHNICAL_EVALUATION_DATASET
)


class TechnicalRetrievalEvaluator:

    def __init__(self):

        self.pipeline = RAGPipeline()

        evaluation_pdf = Path(
            "evaluation_docs/"
            "technical_docs/"
            "spring_boot_docs.pdf"
        )

        if not evaluation_pdf.exists():

            raise FileNotFoundError(
                f"Technical evaluation PDF not found: "
                f"{evaluation_pdf}"
            )

        logging.info(
            "Ingesting technical evaluation PDF..."
        )

        self.pipeline.ingest(
            str(evaluation_pdf)
        )

    def evaluate(self):

        total_queries = len(
            TECHNICAL_EVALUATION_DATASET
        )

        hit_count = 0

        precision_scores = []

        recall_scores = []

        mrr_scores = []

        precision_at_1_scores = []

        for sample in TECHNICAL_EVALUATION_DATASET:

            query = sample["query"]

            expected_entities = (
                sample["expected_entities"]
            )

            logging.info(
                f"\nEvaluating Technical Query: "
                f"{query}"
            )

            retrieved_docs = (
                self.pipeline.retriever.retrieve(
                    query
                )
            )

            retrieved_text = [
                doc.page_content.lower()
                for doc in retrieved_docs
            ]

            relevant_positions = []

            relevant_count = 0

            for idx, text in enumerate(
                retrieved_text
            ):

                if any(
                    entity.lower() in text
                    for entity in expected_entities
                ):

                    relevant_count += 1

                    relevant_positions.append(
                        idx + 1
                    )

            # ---------------------------------
            # Precision@K
            # ---------------------------------
            precision_at_k = (
                relevant_count /
                len(retrieved_docs)
            ) if retrieved_docs else 0

            precision_scores.append(
                precision_at_k
            )

            # ---------------------------------
            # Recall@K
            # ---------------------------------
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

            # ---------------------------------
            # Hit Rate
            # ---------------------------------
            hit = relevant_count > 0

            if hit:

                hit_count += 1

            # ---------------------------------
            # MRR
            # ---------------------------------
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

            # ---------------------------------
            # Precision@1
            # ---------------------------------
            precision_at_1 = 0

            if retrieved_text:

                first_chunk = retrieved_text[0]

                if any(
                    entity.lower() in first_chunk
                    for entity in expected_entities
                ):

                    precision_at_1 = 1

            precision_at_1_scores.append(
                precision_at_1
            )

            # ---------------------------------
            # Query-level logs
            # ---------------------------------
            logging.info(
                f"Relevant Chunks: "
                f"{relevant_count}"
            )

            logging.info(
                f"Precision@K: "
                f"{precision_at_k:.2f}"
            )

            logging.info(
                f"Precision@1: "
                f"{precision_at_1:.2f}"
            )

            logging.info(
                f"Recall@K: "
                f"{recall_at_k:.2f}"
            )

            logging.info(
                f"MRR: "
                f"{reciprocal_rank:.2f}"
            )

        # ---------------------------------
        # Final Metrics
        # ---------------------------------
        avg_precision = (
            sum(precision_scores)
            /
            total_queries
        )

        avg_precision_at_1 = (
            sum(precision_at_1_scores)
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

        print("\n")

        print(
            "===================================="
        )

        print(
            " Technical Retrieval Metrics "
        )

        print(
            "===================================="
        )

        print(
            f"Precision@K : "
            f"{avg_precision:.2f}"
        )

        print(
            f"Precision@1 : "
            f"{avg_precision_at_1:.2f}"
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