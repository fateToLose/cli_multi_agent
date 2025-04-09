from .data_models import ConversationBlocks, Messages


class Conversation:
    def __init__(self) -> None:
        self._data = ConversationBlocks()

    def add_message(self, role: str, content: str) -> None:
        message = Messages(role=role, content=content)
        self._data.messages.append(message)

    def consolidate_msg_for_api(self) -> list:
        return [{"role": msg.role, "content": msg.content} for msg in self._data.messages]

    @property
    def messages(self) -> list[Messages]:
        """Get all messages in the conversation."""
        return self._data.messages.copy()

    @messages.setter
    def messages(self, new_messages: list[Messages]) -> None:
        """Set the conversation messages."""
        self._data = ConversationBlocks(messages=new_messages)

    def clear(self) -> None:
        self._data = ConversationBlocks()
