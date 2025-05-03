from pydantic_ai import Agent, RunContext
from pydantic import BaseModel


class TalkerContext(BaseModel):
    user_facts: list[str]
    behavior_prompt: list[str]


agent = Agent("openai:gpt-4o-mini", deps_type=TalkerContext)


PROMPT_TEMPLATE = """
You are a helpful assistant that can answer questions and help with tasks.

You have the following facts about the user:
{user_facts}

You need to follow these behavior preferences:
{behavior_prompt}
"""


@agent.system_prompt
def get_system_prompt(context: RunContext[TalkerContext]):
    return PROMPT_TEMPLATE.format(
        user_facts="\n".join(context.deps.user_facts),
        behavior_prompt=context.deps.behavior_prompt,
    )


def get_talker_agent() -> Agent:
    return agent
