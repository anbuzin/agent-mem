from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx
import os

from agent_mem.db import get_gel
from agent_mem.agents.summarizer import get_summarizer_agent
from agent_mem.agents.extractor import get_extractor_agent, ExtractorContext
from agent_mem.common.types import CommonChat


router = APIRouter()


class SummarizeRequest(BaseModel):
    chat_id: str
    messages: list[str]
    cutoff: str
    summary_datetime: str


@router.post("/summarize")
async def summarize(
    request: SummarizeRequest,
    summarizer_agent=Depends(get_summarizer_agent),
    gel_client=Depends(get_gel),
):
    print(f"Summarizing messages: {request}")

    formatted_messages = "\n\n".join([m for m in request.messages])

    response = await summarizer_agent.run(
        f"""
        Summarize the following messages:
        {formatted_messages}
        Only respond with the summary, no other text.
        """
    )

    summary = response.output

    await gel_client.query(
        """
        select insert_summary(
            <uuid>$chat_id,
            <datetime><str>$cutoff,
            <str>$summary,
            <datetime><str>$summary_datetime
        )
        """,
        chat_id=request.chat_id,
        cutoff=request.cutoff,
        summary=summary,
        summary_datetime=request.summary_datetime,
    )

    return {"summary": summary}


class ExtractRequest(BaseModel):
    chat_id: str


@router.post("/extract")
async def extract(
    request: ExtractRequest,
    gel_client=Depends(get_gel),
    extractor_agent=Depends(get_extractor_agent),
):
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
        chat_id=request.chat_id,
    )
    chat = CommonChat.from_gel_result(result)

    formatted_messages = "\n\n".join([f"{m.role}: {m.content}" for m in chat.history])

    response = await extractor_agent.run(
        f"""
        Conversation history:
        {formatted_messages}
        """,
        deps=ExtractorContext(
            gel_client=gel_client,
        ),
    )

    return {"response": response.output}


class GetTitleRequest(BaseModel):
    chat_id: str
    messages: list[str]


@router.post("/get_title")
async def get_title(
    request: GetTitleRequest,
    gel_client=Depends(get_gel),
):
    formatted_messages = "\n\n".join([m for m in request.messages])

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Generate a concise title (5 words or less) for the following conversation. Return only the title, no other text.",
            },
            {"role": "user", "content": formatted_messages},
        ],
        "max_tokens": 20,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    response.raise_for_status()
    response_data = response.json()
    title = response_data["choices"][0]["message"]["content"].strip()

    await gel_client.query(
        """
        update Chat
        filter .id = <uuid>$chat_id
        set {
            title := <str>$title
        }
        """,
        chat_id=request.chat_id,
        title=title,
    )

    return {"title": title}
