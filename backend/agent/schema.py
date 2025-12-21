from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union


# frontend elements
class Message(BaseModel):
    # User messages and AI messages
    type: Literal["message"] = Field(default="message")
    role: Literal["user", "assistant"]
    content: str  # for now, only support text


class MessageAssistant(BaseModel):
    type: Literal["message"] = Field(default="message")
    content: str


class FormRow(BaseModel):
    header: str
    content: str = Field(default="")


class FormRequest(BaseModel):
    # Form request message
    type: Literal["form_request"] = Field(default="form_request")
    description: str = Field(default="", description="The description of the form, displayed above the form.")
    rows: list[FormRow] = Field(default_factory=list)


class FormResult(BaseModel):
    type: Literal["form_result"] = Field(default="form_result")
    rows: list[FormRow]


class ChoiceRequest(BaseModel):
    type: Literal["choice_request"] = Field(default="choice_request")
    description: str = Field(
        default="", description="The description of the choice question, displayed above the choices."
    )
    options: list[str]
    single_choice: bool


class ChoiceResult(BaseModel):
    type: Literal["choice_result"] = Field(default="choice_result")
    chosen: list[str]


class ThinkingOutput(BaseModel):
    type: Literal["thinking"] = Field(default="thinking")
    content: str


class ToolCallOutput(BaseModel):
    type: Literal["tool_call"] = Field(default="tool_call")
    content: str


class ToolResponseOutput(BaseModel):
    type: Literal["tool_response"] = Field(default="tool_response")
    content: str


class StreamingDisplayOutput(BaseModel):
    # just for display purpose on the frontend
    type: Literal["streaming_display"] = Field(default="streaming_display")
    content: str


class MessageDelta(BaseModel):
    type: Literal["message_delta"] = Field(default="message_delta")
    content: str


# possible types for agent input
Input = Annotated[Union[Message, FormRequest, FormResult, ChoiceRequest, ChoiceResult], Field(discriminator="type")]

# possible types for agent output
Output = Annotated[
    Union[
        Message,
        ThinkingOutput,
        ToolCallOutput,
        ToolResponseOutput,
        FormRequest,
        ChoiceRequest,
        MessageDelta,
        StreamingDisplayOutput,
    ],
    Field(discriminator="type"),
]


# Possible types for agent final response, subset of Output
class LLMFinalResponse(BaseModel):
    type: Literal["message", "choice_request", "form_request"]
    content: Union[MessageAssistant, FormRequest, ChoiceRequest]

    @classmethod
    def llm_json_schema(cls) -> dict:
        # LLM schema needs all fields to be required, so we return a json schema with all fields required
        return {
            "$defs": {
                "ChoiceRequest": {
                    "properties": {
                        "type": {"const": "choice_request", "title": "Type", "type": "string"},
                        "description": {
                            "description": "The description of the choice question, displayed above the choices.",
                            "title": "Description",
                            "type": "string",
                        },
                        "options": {"items": {"type": "string"}, "title": "Options", "type": "array"},
                        "single_choice": {"title": "Single Choice", "type": "boolean"},
                    },
                    "required": ["type", "options", "single_choice", "description"],
                    "title": "ChoiceRequest",
                    "type": "object",
                    "additionalProperties": False,
                },
                "FormRequest": {
                    "properties": {
                        "type": {"const": "form_request", "title": "Type", "type": "string"},
                        "description": {
                            "description": "The description of the form, displayed above the form.",
                            "title": "Description",
                            "type": "string",
                        },
                        "rows": {"items": {"$ref": "#/$defs/FormRow"}, "title": "Rows", "type": "array"},
                    },
                    "title": "FormRequest",
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["type", "description", "rows"],
                },
                "FormRow": {
                    "properties": {
                        "header": {"title": "Header", "type": "string"},
                        "content": {"default": "", "title": "Content", "type": "string"},  #
                    },
                    "required": ["header", "content"],
                    "title": "FormRow",
                    "type": "object",
                    "additionalProperties": False,
                },
                "MessageAssistant": {
                    "properties": {
                        "type": {"const": "message", "title": "Type", "type": "string"},
                        "content": {"title": "Content", "type": "string"},
                    },
                    "required": ["content", "type"],
                    "title": "MessageAssistant",
                    "type": "object",
                    "additionalProperties": False,
                },
            },
            "properties": {
                "type": {"enum": ["message", "choice_request", "form_request"], "title": "Type", "type": "string"},
                "content": {
                    "anyOf": [
                        {"$ref": "#/$defs/MessageAssistant"},
                        {"$ref": "#/$defs/FormRequest"},
                        {"$ref": "#/$defs/ChoiceRequest"},
                    ],
                    "title": "Content",
                },
            },
            "required": ["type", "content"],
            "title": "LLMFinalResponse",
            "type": "object",
            "additionalProperties": False,
        }


class UIContext(BaseModel):
    # UI context == conversation history
    context: list[Input]
    user_id: str | None = None
