from .base_tool import BaseTool


class CreateFormTool(BaseTool):
    def get_schema(self) -> dict:
        schema = {
            "type": "function",
            "name": "create_form",
            "description": "Show a form for the user to fill in. The form is displayed directly in the chat UI and submitted by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Instructions or background context for the form, displayed above the form."
                    },
                    "headers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Field labels (one per row) that the user should fill in."
                    }
                },
                "required": ["headers"]
            },
        }
        return schema

    async def call(self, headers: list[str], description: str = ""):
        # Create a form for the user to fill in.
        # The actual UI rendering is handled by the agent/UI layer.
        return "Form created. Waiting for user input."

    def tool_call_message(self, **kwargs) -> str:
        return "Creating a form for the user to fill in..."

    def tool_result_message(self, **kwargs) -> str:
        return "Form sent to the user."
