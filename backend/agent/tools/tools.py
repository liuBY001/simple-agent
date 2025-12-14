from pathlib import Path


import logging

logger = logging.getLogger(__name__)


async def write_html_report(html, user_id: str | None = None):
    # Use absolute path to ensure file is written to the correct location
    filename = f"html_report_{user_id}.html" if user_id else "html_report.html"
    report_dir = Path(__file__).parent.parent.parent.parent / "temp" / "reports"
    report_dir.mkdir(exist_ok=True, parents=True)
    html_path = report_dir / filename
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return "success"


async def read_current_report(user_id: str | None = None):
    # Get current report information
    filename = f"html_report_{user_id}.html" if user_id else "html_report.html"
    html_path = Path(__file__).parent.parent.parent.parent / "temp" / "reports" / filename

    content = ""
    if html_path.exists():
        with html_path.open(mode="r") as f:
            content = f.read()
    else:
        content = "There's no current report yet."
    return content


async def create_form(headers: list[str]):
    # Create a form for users to fill out
    return "success"


async def create_choice(options: list[str], single_choice: bool):
    return "success"


TOOL_MAPPING = {
    "write_html_report": {
        "json_schema": {
            "type": "function",
            "name": "write_html_report",
            "description": "Write HTML report, will update to the current page",
            "parameters": {
                "type": "object",
                "properties": {
                    "html": {
                        "type": "string",
                        "description": "Specific HTML report content",
                    }
                },
                "required": ["html"],
            },
        },
        "implementation": write_html_report,
    },
    "read_current_report": {
        "json_schema": {
            "type": "function",
            "name": "read_current_report",
            "description": "Get current HTML report content",
            "parameters": {},
        },
        "implementation": read_current_report,
    },
    "create_form": {
        "json_schema": {
            "type": "function",
            "name": "create_form",
            "description": "Provide a form for users to fill out",
            "parameters": {
                "type": "object",
                "properties": {
                    "headers": {
                        "type": "array",
                        "items": {"type": "string", "description": "Each item in the form for users to fill out"},
                    }
                },
                "required": ["headers"],
            },
        },
        "implementation": create_form,
    },
    "create_choice": {
        "json_schema": {
            "type": "function",
            "name": "create_choice",
            "description": "Provide options for users to choose from",
            "parameters": {
                "type": "object",
                "properties": {
                    "options": {"type": "array", "items": {"type": "string", "description": "Option description"}},
                    "single_choice": {"type": "boolean", "description": "Single choice corresponds to true, multiple choice corresponds to false"},
                },
                "required": ["options", "single_choice"],
            },
        },
        "implementation": create_choice,
    },
}


def get_tool_schema_list() -> list[dict]:
    """Get tool schema list"""
    tool_list = [v["json_schema"] for v in TOOL_MAPPING.values()]
    return tool_list


async def call_tool(func_name: str, kwargs: dict, user_id: str | None = None):
    """Call the corresponding function based on function name and keyword arguments kwargs, return the result"""
    # call the tool
    if func_name not in TOOL_MAPPING:
        raise ValueError(f"function name unknown!{func_name}")

    func_async = TOOL_MAPPING[func_name]["implementation"]

    # Special handling for tools that need user_id
    if func_name in ["write_html_report", "read_current_report"]:
        kwargs["user_id"] = user_id

    # call the function
    result = await func_async(**kwargs)

    return result


__all__ = ["get_tool_schema_list", "call_tool"]