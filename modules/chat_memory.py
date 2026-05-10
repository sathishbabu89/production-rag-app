from langchain_community.chat_message_histories import (
    ChatMessageHistory
)


class ChatMemory:

    def __init__(self):

        self.history = ChatMessageHistory()

    def save_context(
        self,
        user_query: str,
        ai_response: str
    ):

        self.history.add_user_message(
            user_query
        )

        self.history.add_ai_message(
            ai_response
        )

    def get_history(self):

        return self.history.messages

    def clear(self):

        self.history.clear()