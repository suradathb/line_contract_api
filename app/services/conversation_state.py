class ConversationStateService:
    def __init__(self) -> None:
        self._state: dict[str, str] = {}

    def set_state(self, line_user_id: str, state: str) -> None:
        self._state[line_user_id] = state

    def get_state(self, line_user_id: str) -> str | None:
        return self._state.get(line_user_id)

    def clear_state(self, line_user_id: str) -> None:
        self._state.pop(line_user_id, None)


conversation_state_service = ConversationStateService()