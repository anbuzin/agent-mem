from pydantic import BaseModel, Field
import uuid
import datetime


class Message(BaseModel):
    role: str
    content: str 
    created_at: datetime.datetime | None = None

    @classmethod
    def from_gel_result(cls, result: dict):
        return cls(
            role=result.llm_role,
            content=result.body,
            created_at=result.created_at
        )

class Chat(BaseModel):
    id: uuid.UUID
    history: list[Message] = Field(default_factory=list)
    archive: list[Message] = Field(default_factory=list)

    @classmethod
    def from_gel_result(cls, result: dict):
        return cls(
            id=result.id,
            history=[Message.from_gel_result(msg) for msg in result.history],
            archive=[Message.from_gel_result(msg) for msg in result.archive]
        )
