from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic_ai import Agent
from gel import AsyncIOClient
import gel.ai

import uuid

from agent_mem.common.types import CommonChat, CommonMessage
from agent_mem.db import get_gel
from agent_mem.agents.talker import get_talker_agent, TalkerContext
from agent_mem.agents.extractor import get_extractor_agent, ExtractorContext


ADD_MESSAGE_QUERY = """
    with chat := (
        select Chat filter .id = <uuid>$chat_id
    ),
    new_message := (
        insert Message {
            llm_role := <str>$role,
            body := <optional str>$content,
            tool_name := <optional str>$tool_name,
            tool_args := <optional json>$tool_args,
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
            tool_name,
            tool_args,
            created_at
        } order by .created_at,
        history: {
            llm_role,
            body,
            tool_name,
            tool_args,
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
                tool_name,
                tool_args,
                created_at
            } order by .created_at,
            archive: {
                llm_role,
                body,
                tool_name,
                tool_args,
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
    talker_agent: Agent = Depends(get_talker_agent),
    extractor_agent: Agent = Depends(get_extractor_agent),
    gel_client: AsyncIOClient = Depends(get_gel),
) -> StreamingResponse:
    chat = await get_chat(request.chat_id, gel_client)



    async def stream_response():
        full_response = ""

        yield "*Running extractor...*\n"

        await extractor_agent.run(
            f"""
            Extract facts and behavior preferences from the following message:
            {request.message.content}
            """,
            deps=ExtractorContext(
                gel_client=gel_client,
            ),
        )

        yield "*Fetching facts...*\n"

        gel_ai_client = await gel.ai.create_async_rag_client(gel_client, model="gpt-4o-mini")
        embedding_vector = await gel_ai_client.generate_embeddings(
            request.message.content,
            model="text-embedding-3-small",
        )
        
        user_facts = await gel_client.query(
            """
            with 
                vector_search := ext::ai::search(Fact, <array<float32>>$embedding_vector),
                facts := (
                    select vector_search.object
                    order by vector_search.distance asc 
                    limit 5
                )
            select facts.body
            """,
            embedding_vector=embedding_vector,
        )

        behavior_prompt = await gel_client.query(
            """
            select Prompt.body
            """
        )

        yield "*Gathering context...*\n"

        async with talker_agent.run_stream(
            request.message.content,
            message_history=chat.to_pydantic_ai_messages(),
            deps=TalkerContext(
                gel_client=gel_client,
                user_facts=user_facts,
                behavior_prompt=behavior_prompt,
            ),
        ) as result:
            async for text in result.stream_text(delta=True):
                full_response += text
                yield text

        for message in result.new_messages():
            for part in message.parts:
                common_message = CommonMessage.from_pydantic_ai_message_part(part)
                await gel_client.query(
                    ADD_MESSAGE_QUERY,
                    chat_id=request.chat_id,
                    role=common_message.role,
                    content=common_message.content,
                    tool_name=common_message.tool_name,
                    tool_args=common_message.tool_args,
                )

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
    )
