from .tool_source import (
    WriteHTMLTool,
    ReadHTMLTool,
)

import logging
logger = logging.getLogger(__name__)

TOOL_MAPPING = {
    "write_html_report": WriteHTMLTool(),
    "read_current_report": ReadHTMLTool(),
}


def get_tool_schema_list(tool_names: list[str]) -> list[dict]:
    """Return the tool schema list for the given tool names."""
    tool_list = [tool.get_schema() for tool_name, tool in TOOL_MAPPING.items() if tool_name in tool_names]
    return tool_list


async def call_tool(func_name: str, kwargs: dict, user_id: str | None = None):
    """Call the corresponding tool by function name and kwargs, and return its result."""
    # call the tool
    if func_name not in TOOL_MAPPING:
        raise ValueError(f"function name unknown!{func_name}")

    tool = TOOL_MAPPING[func_name]

    # Special handling for tools that need user_id
    if func_name in ["write_html_report", "read_current_report", "get_rednote_account_info"]:
        kwargs["user_id"] = user_id

    # call the function
    logger.info(f"call tool: {func_name}, kwargs: {kwargs}")
    result = await tool.call(**kwargs)

    return result


def tool_call_progress_message(func_name: str, kwargs: dict) -> str:
    # Tool call progress message
    if func_name not in TOOL_MAPPING:
        raise ValueError(f"function name unknown!{func_name}")

    tool = TOOL_MAPPING[func_name]
    return tool.tool_call_message(**kwargs)


def tool_result_progress_message(func_name: str, kwargs: dict) -> str:
    # Tool result progress message
    if func_name not in TOOL_MAPPING:
        raise ValueError(f"function name unknown!{func_name}")

    tool = TOOL_MAPPING[func_name]
    return tool.tool_result_message(**kwargs)


__all__ = ["get_tool_schema_list", "call_tool", "tool_call_progress_message"]
