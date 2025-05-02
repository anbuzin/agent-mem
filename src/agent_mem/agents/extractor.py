from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from gel import AsyncIOClient
from agent_mem.common.types import CommonMessage


class ExtractorContext(BaseModel):
    gel_client: AsyncIOClient
    message: CommonMessage


agent = Agent("openai:gpt-4o-mini", deps_type=ExtractorContext)


@agent.system_prompt
async def get_system_prompt():
    return "You are a helpful assistant that can answer questions and help with tasks."


@agent.tool
async def upsert_fact(context: RunContext[ExtractorContext], key: str, value: str):
    await context.deps.gel_client.query(
        """
        with
            key := <str>$key,
            value := <str>$value,
            message := (
                select Message filter .id = <uuid>$message_id
            )
        insert Fact {
            key := key,
            value := value,
            from_message := message
        } unless conflict on .key else {
            update Fact filter .key = key set {
                value := value,
                from_message := message
            }
        }
        """,
        key=key,
        value=value,
        message_id=context.message.id,
    )


@agent.tool
async def delete_fact(context: RunContext[ExtractorContext], key: str):
    await context.deps.gel_client.query(
        """
        delete Fact filter .key = <str>$key;
        """,
        key=key,
    )


@agent.tool
async def upsert_prompt(context: RunContext[ExtractorContext], key: str, value: str):
    await context.deps.gel_client.query(
        """
        with 
            key := <str>$key,
            value := <str>$value,
            message := (    
                select Message filter .id = <uuid>$message_id
            )
        insert Prompt {
            key := key,
            value := value,
            from_message := message
        } unless conflict on .key else {
            update Prompt filter .key = key set {
                value := value,
                from_message := message
            }
        }
        """,
        key=key,
        value=value,
        message_id=context.message.id,
    )


@agent.tool
async def delete_prompt(context: RunContext[ExtractorContext], key: str):
    await context.deps.gel_client.query(
        """
        delete Prompt filter .key = <str>$key;
        """,
        key=key,
    )


@agent.tool
async def get_extractor_agent() -> Agent:
    return agent
