from .base_tool import BaseTool


class CreateChoiceTool(BaseTool):
    def get_schema(self) -> dict:
        schema = {
            "type": "function",
            "name": "create_choice",
            "description": "Show options for the user to choose from. Options are displayed directly in the chat UI and submitted by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Question text or background context, displayed above the options."
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of selectable options."
                    },
                    "single_choice": {
                        "type": "boolean",
                        "description": "Whether only a single option can be selected. true = single-choice, false = multi-choice."
                    }
                },
                "required": ["options", "single_choice"]
            },
        }
        return schema

    async def call(self, options: list[str], single_choice: bool, description: str = ""):
        # The actual UI rendering is handled by the agent/UI layer.
        return "Choice created. Waiting for user selection."

    def tool_call_message(self, **kwargs) -> str:
        return "Creating a choice prompt for the user..."

    def tool_result_message(self, **kwargs) -> str:
        return "Choice prompt sent to the user."
