from dotenv import load_dotenv

load_dotenv()

import sys
from pathlib import Path
from openai import AsyncOpenAI

sys.path.append(str(Path(__file__).parent.parent))


from agent.agent_openai.agent import Agent
from agent.schema import UIContext, Message


async def test_agent():

    client = AsyncOpenAI()

    system_prompt = (
        "You are an expert report writer who is great at generating clean, beautiful HTML reports. "
        "Present results via the report rather than back-and-forth conversation; the chat should only be used "
        "to clarify requirements. In most cases, communicate with the user via multiple-choice questions or by "
        "asking them to fill out a form. After generating the report, only briefly notify the user—do not repeat "
        "the report content in chat. Your main task is to write the report."
    )

    agent = Agent(oai_client=client, system_prompt=system_prompt, tools=["read_current_report", "write_html_report"])

    ui_context = UIContext(
        context=[
            # Message(
            #     role="user",
            #     content="give me a single choice question please.",
            # ),
            # Message(
            #     role="user",
            #     content="write me a short essay on topic of human and nature, in 200 words.",
            # ),
            Message(
                role="user",
                content="check current report, discard it, and write a new report on generative ai in 200 words.",
            ),
        ]
    )

    ans_gen = agent.trigger(context=ui_context)

    async for chunk in ans_gen:
        print(chunk)

    return


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_agent())
