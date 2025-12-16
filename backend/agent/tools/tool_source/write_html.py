from pathlib import Path

from .base_tool import BaseTool

import logging
logger = logging.getLogger(__name__)


class WriteHTMLTool(BaseTool):
    def get_schema(self) -> dict:
        schema = {
            "type": "function",
            "name": "write_html_report",
            "description": (
                "Create a report or update the current report. Replace lines from start_line to end_line "
                "(both inclusive) with the provided content. Note: ranges across multiple changes must not overlap."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start_line": {
                                    "type": "integer",
                                    "description": "Start line number to replace (inclusive)."
                                },
                                "end_line": {
                                    "type": "integer",
                                    "description": "End line number to replace (inclusive)."
                                },
                                "change_to": {
                                    "type": "string",
                                    "description": "Replacement content.",
                                }
                            }
                        }
                    }
                },
            },
        }
        return schema

    async def call(self, changes: list[dict], user_id: str | None = None):
        # update the content from start_line to end_line(both inclusive)

        # load original content
        filename = f"html_report_{user_id}.html" if user_id else "html_report.html"
        html_path = Path(__file__).parent.parent.parent.parent.parent / "temp" / "reports" / filename

        logger.info(f"Writing html report to: {html_path}")

        # if file not exists, create it
        if not html_path.exists():
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("")

            logger.info(f"Created new html report file: {html_path}")

        with open(html_path, "r", encoding="utf-8") as f:
            old_lines = f.readlines()

        # we assume that all change intervals are mutually exclusive
        change_checklist = []
        for change in changes:
            change["done"] = False
            change_checklist.append(change)

        content_updated = ""
        
        # Special case: if the file is empty, apply all changes directly
        if not old_lines:
            for change in change_checklist:
                change_to_content = change.get("change_to", "")
                content_updated += change_to_content
                if change_to_content and not change_to_content.endswith("\n"):
                    content_updated += "\n"
                change["done"] = True
        else:
            for line_idx, line in enumerate(old_lines):
                # check if falls into change zone
                need_change = False
                for change in change_checklist:
                    start_line = change["start_line"]
                    end_line = change["end_line"]
                    if line_idx >= start_line and line_idx <= end_line:
                        need_change = True
                        if not change["done"]:
                            # At the first line of the replacement range, inject the replacement content
                            content_updated += change.get("change_to", "")
                            # If change_to doesn't end with a newline, append one
                            change_to_content = change.get("change_to", "")
                            if change_to_content and not change_to_content.endswith("\n"):
                                content_updated += "\n"
                            change["done"] = True
                            
                if not need_change:
                    # Not in a replacement range; keep the original line
                    content_updated += line

        # update the file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content_updated)
        
        return "Report updated!"

    def tool_call_message(self, **kwargs) -> str:
        update_message = ""
        changes = kwargs.get("changes", [])
        for change in changes:
            start_line = change.get("start_line", 0)
            end_line = change.get("end_line", None)
            change_to = change.get("change_to", "")
            update_message += f"Lines {start_line} to {end_line}: updating content to: {change_to[:100]}...\n"

        return f"Updating HTML report...\n{update_message}"

    def tool_result_message(self, **kwargs) -> str:
        # the result message to yield to front end
        return "Report updated!"
