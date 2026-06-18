import logging
import time

from modules.orchestrator import Orchestrator
from modules.pipeline import (
    RAGPipeline
)

from pathlib import Path


class SystemEvaluator:

    def __init__(self):
        self.orchestrator = Orchestrator()

        self.pipeline = RAGPipeline()

        evaluation_pdf = Path(
            "evaluation_docs/Top_10_Indian_Business_Success_Stories_Expanded_5_Pages.pdf"
        )

        if not evaluation_pdf.exists():

            raise FileNotFoundError(
                f" evaluation PDF not found: "
                f"{evaluation_pdf}"
            )

        logging.info(
            "Ingesting evaluation PDF..."
        )

        self.pipeline.ingest(
            str(evaluation_pdf)
        )

    # -----------------------------------------
    # Evaluate single query
    # -----------------------------------------
    def evaluate_query(self, sample: dict):

        query = sample["query"]

        expected_route = sample.get("expected_route")
        expected_sql = sample.get("expected_sql")
        expected_answer_contains = sample.get("expected_answer_contains")

        start_time = time.time()

        logging.info(f"\nEvaluating Query: {query}")

        # -----------------------------------------
        # Safe Orchestrator Call
        # -----------------------------------------
        try:
            result = self.orchestrator.process_query(query)

        except Exception as e:
            return {
                "query": query,
                "route_correct": False,
                "error": str(e),
                "status": "failed"
            }

        # -----------------------------------------
        # Safe extraction
        # -----------------------------------------
        actual_route = result.get("route")

        diagnostics = result.get("diagnostics", {})

        evaluation = {

            "query": query,
            "expected_route": expected_route,
            "actual_route": actual_route,

            "route_correct": (
                expected_route == actual_route
            ),

            "status": result.get("status", "success"),

            "latency": round(time.time() - start_time, 2),

            "error": result.get("error")
        }

        # =================================================
        # SQL ROUTE
        # =================================================
        if actual_route == "SQL":

            sql_query = result.get("sql_query")
            sql_results = result.get("results")

            evaluation.update({

                "sql_query": sql_query,
                "sql_results": sql_results,

                "sql_correct": (
                    expected_sql in str(sql_query)
                    if expected_sql and sql_query
                    else None
                )
            })

        # =================================================
        # RAG ROUTE
        # =================================================
        elif actual_route == "RAG":

            response_obj = result.get("response")
            error = result.get("error")

            answer = None

            if response_obj and hasattr(response_obj, "answer"):
                answer = response_obj.answer

            evaluation.update({

                "answer": answer,
                "rag_failed": error is not None,
                "error": error,

                "answer_contains_expected": (
                    expected_answer_contains.lower() in answer.lower()
                    if expected_answer_contains and answer
                    else None
                )
            })

        # =================================================
        # HYBRID ROUTE
        # =================================================
        elif actual_route == "HYBRID":

            rag_answer = result.get("rag_answer")
            sql_results = result.get("sql_results")
            final_answer = result.get("final_answer")

            evaluation.update({

                "rag_answer": rag_answer,
                "sql_results": sql_results,
                "final_answer": final_answer,

                "sql_correct": (
                    expected_sql in str(sql_results)
                    if expected_sql and sql_results
                    else None
                ),

                "answer_contains_expected": (
                    expected_answer_contains.lower() in final_answer.lower()
                    if expected_answer_contains and final_answer
                    else None
                )
            })

        return evaluation

    # -----------------------------------------
    # Batch evaluation
    # -----------------------------------------
    def evaluate_dataset(self, dataset: list):

        results = []

        correct_routes = 0
        failed_count = 0

        for sample in dataset:

            evaluation = self.evaluate_query(sample)

            results.append(evaluation)

            if evaluation.get("route_correct"):
                correct_routes += 1

            if evaluation.get("status") == "failed":
                failed_count += 1

            logging.info(
                f"Route Correct: {evaluation.get('route_correct')}"
            )

        # -----------------------------------------
        # Final Metrics
        # -----------------------------------------
        total = len(dataset)

        summary = {

            "total_queries": total,

            "route_accuracy": (
                correct_routes / total if total else 0
            ),

            "failure_rate": (
                failed_count / total if total else 0
            ),

            "results": results
        }

        print("\n===================================")
        print(" SYSTEM EVALUATION SUMMARY ")
        print("===================================")
        print(f"Total Queries   : {summary['total_queries']}")
        print(f"Route Accuracy  : {summary['route_accuracy']:.2f}")
        print(f"Failure Rate    : {summary['failure_rate']:.2f}")
        print("===================================\n")

        return summary