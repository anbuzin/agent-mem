import gel
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv
import uuid
import asyncio
from typing import AsyncGenerator
from agent_mem.common.types import CommonMessage, CommonChat

load_dotenv()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gel_client = gel.create_async_client()

talker_agent = Agent("openai:gpt-4o-mini")
summarizer_agent = Agent("openai:gpt-4o-mini")
extractor_agent = Agent("openai:gpt-4o-mini")


class SummarizeRequest(BaseModel):
    chat_id: str
    messages: list[str]
    cutoff: str


class MessageRequest(BaseModel):
    chat_id: uuid.UUID
    message: CommonMessage


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
async def get_chat(chat_id: uuid.UUID) -> CommonChat:
    result = await gel_client.query_single(
        """
        with 
        chat_id := <uuid>$chat_id,
        chat := (select Chat filter .id = chat_id)
    select assert_exists(chat) {
        id,
        title,
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
    return CommonChat.from_gel_result(result)


@app.get("/chats")
async def get_chats() -> list[CommonChat]:
    result = await gel_client.query(
        """
        select Chat {
            id,
            title,
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
    return [CommonChat.from_gel_result(chat) for chat in result]


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
    chat = await get_chat(request.chat_id)

    await gel_client.query(
        ADD_MESSAGE_QUERY,
        chat_id=request.chat_id,
        role=request.message.role,
        content=request.message.content,
    )

    async def stream_response():
        full_response = ""
        async with talker_agent.run_stream(
            request.message.content, message_history=chat.to_pydantic_ai_messages()
        ) as result:
            async for text in result.stream_text(delta=True):
                full_response += text
                yield text

        await gel_client.query(
            ADD_MESSAGE_QUERY,
            chat_id=request.chat_id,
            role="assistant",
            content=full_response,
        )

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
    )


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

