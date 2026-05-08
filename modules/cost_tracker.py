import time
import logging


class CostTracker:

    def __init__(self):

        self.start_time = None
        self.end_time = None

    def start(self):

        self.start_time = time.time()

    def stop(self):

        self.end_time = time.time()

    def calculate_latency(self):

        if self.start_time and self.end_time:
            return round(
                self.end_time - self.start_time,
                2
            )

        return 0

    def estimate_tokens(self, text: str):

        # Rough estimation:
        # ~4 chars ≈ 1 token
        return int(len(text) / 4)

    def estimate_cost(
        self,
        prompt_tokens,
        completion_tokens
    ):

        # Placeholder pricing
        # Adjust later for actual DeepSeek pricing

        input_cost = (
            prompt_tokens / 1000
        ) * 0.001

        output_cost = (
            completion_tokens / 1000
        ) * 0.002

        return round(
            input_cost + output_cost,
            6
        )

    def log_metrics(
        self,
        prompt,
        response
    ):

        prompt_tokens = self.estimate_tokens(prompt)

        completion_tokens = self.estimate_tokens(response)

        total_tokens = (
            prompt_tokens + completion_tokens
        )

        latency = self.calculate_latency()

        estimated_cost = self.estimate_cost(
            prompt_tokens,
            completion_tokens
        )

        logging.info(
            f"""
===== COST TRACKING =====
Prompt Tokens     : {prompt_tokens}
Completion Tokens : {completion_tokens}
Total Tokens      : {total_tokens}
Latency (sec)     : {latency}
Estimated Cost($) : {estimated_cost}
=========================
"""
        )

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency": latency,
            "estimated_cost": estimated_cost
        }