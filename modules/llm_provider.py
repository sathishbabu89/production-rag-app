from langchain_openai import ChatOpenAI
from langsmith import traceable

from config import Config

import logging


class LLMProvider:

    def __init__(self):

        logging.info(
            "Initializing DeepSeek LangChain LLM..."
        )

        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL,
            temperature=0.3
        )

    @traceable(name="DeepSeek LLM Generation")
    def generate(self, prompt: str):

        response = self.llm.invoke(prompt)

        return response.content