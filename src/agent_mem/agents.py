from pydantic_ai import Agent


talker_agent = Agent("openai:gpt-4o-mini")
summarizer_agent = Agent("openai:gpt-4o-mini")
extractor_agent = Agent("openai:gpt-4o-mini")


def get_talker_agent():
    return talker_agent

def get_summarizer_agent():
    return summarizer_agent

def get_extractor_agent():
    return extractor_agent
