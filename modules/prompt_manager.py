
from langchain_core.prompts import PromptTemplate


class PromptManager:

    def __init__(
        self,
        prompt_name="rag_prompt_v1.txt"
    ):

        with open(
            f"prompts/{prompt_name}",
            "r",
            encoding="utf-8"
        ) as f:

            template = f.read()

        self.prompt = PromptTemplate(
            input_variables=[
                "context",
                "query"
            ],
            template=template
        )

    def format(
        self,
        context: str,
        query: str
    ) -> str:

        return self.prompt.format(
            context=context,
            query=query
        )