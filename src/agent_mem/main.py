import gel
import asyncio
import uuid
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent_mem.common.types import Chat, Message

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gel_client = gel.create_async_client()


class SummarizeRequest(BaseModel):
    chat_id: str
    messages: list[str]
    cutoff: str


class MessageRequest(BaseModel):
    chat_id: uuid.UUID
    message: Message


@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    print(f"Summarizing messages: {request}")

    await gel_client.query(
        """
        select insert_summary(
            <uuid>$chat_id,
            <str>$summary,
            <datetime><str>$cutoff
        )
        """,
        chat_id=request.chat_id,
        summary="This is a summary",
        cutoff=request.cutoff,
    )

    return {"summary": "This is a test summary"}


@app.get("/chat/{chat_id}")
async def get_chat(chat_id: uuid.UUID) -> Chat:
    result = await gel_client.query_single(
        """
        with 
        chat_id := <uuid>$chat_id,
        chat := (select Chat filter .id = chat_id)
    select assert_exists(chat) {
        id,
        archive: {
            llm_role,
            body,
            created_at
        } order by .created_at,
        history: {
            llm_role,
            body,
            created_at
        } order by .created_at
    }
    """,
        chat_id=chat_id,
    )
    return Chat.from_gel_result(result)


@app.get("/chats")
async def get_chats() -> list[Chat]:
    result = await gel_client.query(
        """
        select Chat {
            id,
            history: {
                llm_role,
                body,
                created_at
            } order by .created_at,
            archive: {
                llm_role,
                body,
                created_at
            } order by .created_at
        }
        order by .created_at desc
        """
    )
    return [Chat.from_gel_result(chat) for chat in result]


@app.post("/chat")
async def create_chat() -> uuid.UUID:
    result = await gel_client.query_single(
        """
        insert Chat; 
        """
    )
    return result.id


@app.post("/message")
async def handle_message(request: MessageRequest) -> StreamingResponse:
    await gel_client.query(
        ADD_MESSAGE_QUERY,
        chat_id=request.chat_id,
        role=request.message.role,
        content=request.message.content,
    )

    return StreamingResponse(
        handle_streamed_llm_response(request.chat_id, fake_response_generator()),
        media_type="text/plain",
    )

async def fake_response_generator():
    for word in "This is a test response, it's a long response".split():
        yield word + " "
        await asyncio.sleep(0.05)


ADD_MESSAGE_QUERY = """
    with chat := (
        select Chat filter .id = <uuid>$chat_id
    ),
    new_message := (
        insert Message {
            llm_role := <str>$role,
            body := <str>$content,
        }
    )
    update chat
    set {
        archive := distinct (.archive union new_message)
    }
"""


async def handle_streamed_llm_response(
    chat_id: uuid.UUID, generator: AsyncGenerator[str, None]
):
    full_response = ""
    async for chunk in generator:
        full_response += chunk
        yield chunk

    await gel_client.query(
        ADD_MESSAGE_QUERY,
        chat_id=chat_id,
        role="assistant",
        content=full_response,
    )


