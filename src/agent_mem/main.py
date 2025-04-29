import gel
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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
    chat_id: str
    role: str
    content: str


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


@app.post("/save_message")
async def save_message(request: MessageRequest):
    await gel_client.query(
        """
        with chat := (
            select Chat filter .id = <uuid>$chat_id
        ),
        # Insert new message
        new_message := (
            insert Message {
                llm_role := <str>$role,
                body := <str>$content,
            }
        )
        # Add message to chat history
        update chat
        set {
            archive := distinct (.archive union new_message)
        }
        """,
        chat_id=request.chat_id,
        role=request.role,
        content=request.content
    )
    
    # For echo chat, just return the same message
    return {"role": request.role, "content": request.content}


@app.post("/create_chat")
async def create_chat():
    result = await gel_client.query(
        """
        insert Chat {}
        """
    )
    
    return {"chat_id": str(result[0].id)}


@app.get("/get_chat/{chat_id}")
async def get_chat(chat_id: str):
    result = await gel_client.query(
        """
        select Chat {
            history: {
                llm_role,
                body,
                created_at
            } order by .created_at
        } filter .id = <uuid>$chat_id
        """,
        chat_id=chat_id
    )
    
    if not result:
        return {"messages": []}
    
    messages = []
    for msg in result[0].history:
        messages.append({
            "role": msg.llm_role,
            "content": msg.body,
            "timestamp": msg.created_at
        })
    
    return {"messages": messages}
