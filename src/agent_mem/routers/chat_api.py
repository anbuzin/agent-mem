from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import uuid

from agent_mem.common.types import CommonChat, CommonMessage
from agent_mem.db import get_gel
from agent_mem.agents.talker import get_talker_agent, TalkerSystemPrompt


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


router = APIRouter()


class MessageRequest(BaseModel):
    chat_id: uuid.UUID
    message: CommonMessage


@router.get("/chat/{chat_id}")
async def get_chat(chat_id: uuid.UUID, gel_client=Depends(get_gel)) -> CommonChat:
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


@router.get("/chats")
async def get_chats(gel_client=Depends(get_gel)) -> list[CommonChat]:
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


@router.post("/chat")
async def create_chat(gel_client=Depends(get_gel)) -> uuid.UUID:
    result = await gel_client.query_single(
        """
        insert Chat; 
        """
    )
    return result.id


@router.post("/message")
async def handle_message(
    request: MessageRequest,
    talker_agent=Depends(get_talker_agent),
    gel_client=Depends(get_gel),
) -> StreamingResponse:
    chat = await get_chat(request.chat_id, gel_client)

    await gel_client.query(
        ADD_MESSAGE_QUERY,
        chat_id=request.chat_id,
        role=request.message.role,
        content=request.message.content,
    )

    user_facts = await gel_client.query(
        """
        select Fact.body 
        limit 5;
        """
    )

    behavior_prompt = await gel_client.query(
        """
        select Prompt.body
        """
    )

    async def stream_response():
        full_response = ""

        async with talker_agent.run_stream(
            request.message.content, 
            message_history=chat.to_pydantic_ai_messages(),
            deps=TalkerSystemPrompt(
                user_facts=user_facts,
                behavior_prompt=behavior_prompt,
            ),
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
