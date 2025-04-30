from pydantic import BaseModel, Field
import uuid
import datetime
from pydantic_ai.messages import ModelMessage
from pydantic_ai.messages import SystemPromptPart, UserPromptPart, TextPart
from pydantic_ai.messages import ModelRequest, ModelResponse


class CommonMessage(BaseModel):
    role: str
    content: str
    created_at: datetime.datetime | None = None

    @classmethod
    def from_gel_result(cls, result: dict):
        return cls(
            role=result.llm_role, content=result.body, created_at=result.created_at
        )

    @classmethod
    def from_pydantic_ai_message_part(cls, message: ModelMessage):
        match getattr(message, "part_kind", "unknown"):
            case "system-prompt":
                role = "system"
            case "user-prompt":
                role = "user"
            case "text":
                role = "assistant"
            case _:
                role = "unknown"

        return cls(
            role=role,
            content=message.content,
            created_at=message.timestamp if hasattr(message, "timestamp") else None,
        )

    def to_pydantic_ai_message_part(self):
        """Convert CommonMessage to appropriate Pydantic AI message part."""

        match self.role:
            case "system":
                return SystemPromptPart(content=self.content, timestamp=self.created_at)
            case "user":
                return UserPromptPart(content=self.content, timestamp=self.created_at)
            case "assistant":
                return TextPart(content=self.content)
            case _:
                # Default fallback for unknown roles
                return UserPromptPart(
                    content=f"[Unknown role message: {self.content}]",
                    timestamp=self.created_at,
                )


def to_common_messages(messages: list[ModelMessage]):
    common_messages = []
    for message in messages:
        for part in message.parts:
            common_messages.append(CommonMessage.from_pydantic_ai_message_part(part))
    return common_messages


class CommonChat(BaseModel):
    id: uuid.UUID | None = None
    title: str | None = None
    history: list[CommonMessage] = Field(default_factory=list)
    archive: list[CommonMessage] = Field(default_factory=list)

    @classmethod
    def from_gel_result(cls, result: dict):
        return cls(
            id=result.id,
            title=result.title,
            history=[CommonMessage.from_gel_result(msg) for msg in result.history],
            archive=[CommonMessage.from_gel_result(msg) for msg in result.archive],
        )

    def to_pydantic_ai_messages(self):
        turns = []
        current_turn: ModelMessage | None = None

        for message in self.history:
            turn_type = (
                ModelRequest if message.role in ["system", "user"] else ModelResponse
            )

            if current_turn is None or type(current_turn) is not turn_type:
                # If we have messages in the current chunk, save it
                if current_turn:
                    turns.append(current_turn)
                # Start a new chunk
                current_turn = turn_type(parts=[message.to_pydantic_ai_message_part()])
            else:
                # Add to the current chunk
                current_turn.parts.append(message.to_pydantic_ai_message_part())

        if current_turn:
            turns.append(current_turn)

        return turns
