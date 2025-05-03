from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, ConfigDict
from gel import AsyncIOClient


class ExtractorContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    gel_client: AsyncIOClient
    user_facts: list[str]
    behavior_preferences: list[str]


agent = Agent("openai:gpt-4o-mini", deps_type=ExtractorContext)


@agent.system_prompt
async def get_system_prompt(context: RunContext[ExtractorContext]):
    return f"""
    You are an agent that can extract facts about a user from their messages.
    The following facts are already known:
    {context.deps.user_facts}
    You can also extract agent behavior preferences that user expresses.
    The following preferences are already known:
    {context.deps.behavior_preferences}
    If no infomation can be extracted, simply quit.
    """


@agent.tool
async def upsert_fact(context: RunContext[ExtractorContext], key: str, value: str):
    await context.deps.gel_client.query(
        """
        with
            key := <str>$key,
            value := <str>$value,

        insert Fact {
            key := key,
            value := value,
        } unless conflict on .key else (
            update Fact filter .key = key set {
                value := value,
            }
        )
        """,
        key=key,
        value=value,
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
        insert Prompt {
            key := key,
            value := value,
        } unless conflict on .key else (
            update Prompt filter .key = key set {
                value := value,
            }
        )
        """,
        key=key,
        value=value,
    )


@agent.tool
async def delete_prompt(context: RunContext[ExtractorContext], key: str):
    await context.deps.gel_client.query(
        """
        delete Prompt filter .key = <str>$key;
        """,
        key=key,
    )


async def get_extractor_agent() -> Agent:
    return agent
