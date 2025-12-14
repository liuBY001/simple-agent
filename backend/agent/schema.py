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
    rows: list[FormRow]


class FormResult(BaseModel):
    type: Literal["form_result"] = Field(default="form_result")
    rows: list[FormRow]


class ChoiceRequest(BaseModel):
    type: Literal["choice_request"] = Field(default="choice_request")
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


# Possible types for agent input
Input = Annotated[Union[Message, FormRequest, FormResult, ChoiceRequest, ChoiceResult], Field(discriminator="type")]

# Possible types for agent output
Output = Annotated[
    Union[Message, ThinkingOutput, ToolCallOutput, ToolResponseOutput, FormRequest, ChoiceRequest],
    Field(discriminator="type"),
]


# Possible types for agent final response, subset of Output
class LLMFinalResponse(BaseModel):
    type: Literal["message", "choice_request", "form_request"]
    content: Union[MessageAssistant, FormRequest, ChoiceRequest]


class UIContext(BaseModel):
    # UI context == conversation history
    context: list[Input]
    user_id: str | None = None
