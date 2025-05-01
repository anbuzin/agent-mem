from fastapi import APIRouter, Depends
from pydantic import BaseModel

from agent_mem.db import get_gel
from agent_mem.agents import get_summarizer_agent

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
