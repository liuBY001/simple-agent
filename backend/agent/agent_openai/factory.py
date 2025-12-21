# the agent factory

from .agent import Agent
from . import oai_client

def create_report_agent():

    system_prompt = (
        "You are an expert report writer who is great at generating clean, beautiful HTML reports. "
        "Present results via the report rather than back-and-forth conversation; the chat should only be used "
        "to clarify requirements. In most cases, communicate with the user via multiple-choice questions or by "
        "asking them to fill out a form. After generating the report, only briefly notify the user—do not repeat "
        "the report content in chat. Your main task is to write the report. You can also use tools to view "
        "Xiaohongshu (Rednote) account and post information, as well as web search."
    )

    report_agent = Agent(
        oai_client=oai_client,
        system_prompt=system_prompt,
        model="gpt-5.2",
        tools=[
            "read_current_report",
            "write_html_report",
        ],
        web_search=True,
        reasonging_effort="low",
        max_round_tool_call=10
    )

    return report_agent

