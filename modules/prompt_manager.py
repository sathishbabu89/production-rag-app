from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)


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

    @staticmethod
    def conversational_retrieval_prompt():

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a conversational query reformulation assistant
                    for a Retrieval-Augmented Generation (RAG) system.

                    Your task is to rewrite the latest user question
                    into a standalone retrieval-friendly query
                    using the previous conversation history.

                    IMPORTANT RULES:
                    - Always use chat history to resolve ambiguity
                    - Preserve the original user intent
                    - Replace vague references like:
                    "it", "they", "this", "tell me more"
                    with the actual topic/entity from history
                    - NEVER ask the user for clarification
                    - NEVER answer the question
                    - ONLY return the rewritten retrieval query
                    - Keep the rewritten query concise and retrieval-optimized

                    EXAMPLES:

                    Chat History:
                    User: Explain Zoho story

                    User Query:
                    Tell me more

                    Rewritten Query:
                    Tell me more about Zoho story


                    Chat History:
                    User: Explain Nykaa success

                    User Query:
                    Why was it successful?

                    Rewritten Query:
                    Why was Nykaa successful?
                    """
                ),

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),

                (
                    "human",
                    "{input}"
                )
            ]
        )