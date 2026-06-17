class ConversationState:

    def __init__(self):

        self.current_entity = None

        self.current_route = None

        self.last_query = None

    def update_entity(
        self,
        entity
    ):

        self.current_entity = entity

    def get_entity(self):

        return self.current_entity

    def update_route(
        self,
        route
    ):

        self.current_route = route

    def update_query(
        self,
        query
    ):

        self.last_query = query

    def clear(self):

        self.current_entity = None

        self.current_route = None

        self.last_query = None