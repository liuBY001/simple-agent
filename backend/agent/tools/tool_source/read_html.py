from pathlib import Path

from .base_tool import BaseTool


class ReadHTMLTool(BaseTool):
    def get_schema(self) -> dict:
        schema = {
            "type": "function",
            "name": "read_current_report",
            "description": (
                "Get the current HTML report content. Each line is prefixed with a line number starting from 0. "
                "Use this to inspect the report before making edits."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            },
        }
        return schema

    async def call(self, user_id: str | None = None):
        # Get the current report content
        filename = f"html_report_{user_id}.html" if user_id else "html_report.html"
        html_path = Path(__file__).parent.parent.parent.parent.parent / "temp" / "reports" / filename

        # if file not exists, create it
        if not html_path.exists():
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("")

        with open(html_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Prefix each line with its line number
        numbered_lines = [f"{i}|{line}" for i, line in enumerate(lines)]
        return "".join(numbered_lines) if numbered_lines else "(Report is empty)"

    def tool_call_message(self, **kwargs) -> str:
        return "Reading current report..."

    def tool_result_message(self, **kwargs) -> str:
        return "Report read complete."
