import time
import logging

logging.basicConfig(level=logging.INFO)


class RetryFallbackHandler:

    def __init__(self, max_retries=3, delay=2):
        self.max_retries = max_retries
        self.delay = delay

    #def execute(self, func, *args, **kwargs):
    def execute(self, operation_name, func, *args, **kwargs):
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logging.info(
                    f"{operation_name} | Attempt {attempt} started..."
                )

                result = func(*args, **kwargs)

                logging.info(
                    f"{operation_name} | Attempt {attempt} succeeded."
                )

                return result

            except Exception as e:
                last_exception = e

                error_message = str(e)

                logging.error(
                    f"[Retry {attempt}/{self.max_retries}] Error: {error_message}"
                )

                # ❌ Do NOT retry authentication errors
                if "401" in error_message or "authentication" in error_message.lower():
                    logging.error("Authentication error detected. Stopping retries.")
                    raise e

                # exponential backoff
                wait_time = self.delay * attempt

                logging.info(
                    f"Waiting {wait_time} seconds before retry..."
                )

                time.sleep(wait_time)

        raise Exception(
            f"All retry attempts failed. Last error: {str(last_exception)}"
        )