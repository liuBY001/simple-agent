import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from agent.tools.tools import get_tool_schema_list, call_tool
import asyncio


def test_get_tool_schema_list():
    res = get_tool_schema_list()
    print(res)
    return


def test_call_tool():
    func_name = "write_html_report"
    kwargs = {"html": "<header> demo html </header>"}

    res = asyncio.run(call_tool(func_name=func_name, kwargs=kwargs))
    print(res)

    return res




if __name__ == "__main__":
    # test_get_tool_schema_list()

    test_call_tool()
