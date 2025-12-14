from dotenv import load_dotenv

load_dotenv()

import sys
from pathlib import Path
from openai import OpenAI

sys.path.append(str(Path(__file__).parent.parent))


from agent.agent_openai.agent_html import Agent
from agent.schema import UIContext, Message


async def test_agent():

    client = OpenAI()

    agent = Agent(client=client)

    ui_context = UIContext(
        context=[
            Message(
                role="user",
                content="give me a single choice question please.",
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
