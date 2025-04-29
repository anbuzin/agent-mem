import gel
from fastapi import FastAPI, Request
from pydantic import BaseModel


app = FastAPI()
gel_client = gel.create_async_client()


class SummarizeRequest(BaseModel):
    chat_id: str
    messages: list[str]
    cutoff: str

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
        cutoff=request.cutoff
    )

    return {"summary": "This is a test summary"}
