import json
import asyncio
from typing import AsyncGenerator
import logging

from ..schema import (
    UIContext,
    Output,
    Message,
    ThinkingOutput,
    ToolCallOutput,
    ToolResponseOutput,
    FormRequest,
    FormResult,
    ChoiceRequest,
    ChoiceResult,
    LLMFinalResponse,
)
from ..tools.tools import get_tool_schema_list, call_tool, tool_call_progress_message
from .base_agent import ResponsiveAgent

logger = logging.getLogger(__name__)


class Agent(ResponsiveAgent):
    def __init__(
        self,
        oai_client,
        system_prompt: str,
        model: str = "gpt-5.2",
        tools: list[str] = [],
        web_search: bool = True,
        reasonging_effort: str = "low",
        max_round_tool_call: int = 10,
    ):
        self.model = model
        self.client = oai_client
        self.system_prompt = system_prompt

        self.tools = get_tool_schema_list(tools)

        # add search tool
        if web_search:
            self.tools.append(
                {
                    "type": "web_search",
                }
            )

        # some configs
        self.reasoning_effort = reasonging_effort
        self.max_round_tool_call = max_round_tool_call

        logger.info(f"init agent with model: {self.model}, tools: {self.tools}, web_search: {web_search}, reasoning_effort: {self.reasoning_effort}, max_round_tool_call: {self.max_round_tool_call}")

    async def trigger(self, context: UIContext) -> AsyncGenerator[Output, None]:
        """
        trigger function
        take input from ui, yield response to ui

        input: UIContext
        output: Output
        """

        logger.info(f"trigger input: {context}")

        # the initial context pass to llm
        input_list = self.construct_prompt(context)

        get_message = False
        for i in range(self.max_round_tool_call):
            # get response
            logger.info(f"Round {i}, inputs sent to openai: {input_list}")

            response = self.client.responses.parse(
                model=self.model,
                tools=self.tools,  # list of schemas
                input=input_list,
                reasoning={"effort": self.reasoning_effort, "summary": "auto"},
                text_format=LLMFinalResponse,
            )

            logger.info(f"Round {i}, got openai response: {response.model_dump(warnings=False)}")

            # send intermediate responses back to ui
            for progress in self.send_openai_response_progress(response):
                yield progress

            # update context
            input_list += response.output

            # deal with tool calls
            tool_calls = [item for item in response.output if item.type == "function_call"]
            if len(tool_calls) > 0:
                logger.info(f"Round {i}, calling tools in parallel: {tool_calls}")
                tool_call_results = await self.trigger_tool_calls(tool_calls, context.user_id)
                logger.info(f"Round {i}, got tool call results: {tool_call_results}")

                for progress in self.send_tool_result_progress(tool_call_results):
                    yield progress

                input_list += tool_call_results

            else:
                # no tool call needed
                get_message = True
                break

        # deal with it if unfinished
        if not get_message:
            # yield fallback message
            yield self._output_to_sse(Message(role="assistant", content="tool call limit exceeded. Please try again."))

        yield "data: done\n\n"

    def parse_final_response(self, final_response: str):
        try:
            parsed_response = LLMFinalResponse.model_validate_json(final_response)
        except Exception as e:
            logger.error(f"Failed to parse final response: {e}")
            return final_response

        response_type = parsed_response.type
        if response_type == "message":
            return Message(role="assistant", content=parsed_response.content.content)
        else:
            return parsed_response.content

    def send_openai_response_progress(self, response):
        for output in response.output:
            if output.type == "reasoning":
                if output.summary:
                    for summary in output.summary:
                        if summary.type == "summary_text":
                            yield self._output_to_sse(ThinkingOutput(content=summary.text))
            elif output.type == "web_search_call":  # OpenAI built-in web search
                if output.action.type == "search":
                    query = output.action.query or ""
                    if query:
                        yield self._output_to_sse(ToolCallOutput(content=f"Searching: {query}"))
                elif output.action.type == "open_page":
                    url = output.action.url or ""
                    if url:
                        yield self._output_to_sse(ToolCallOutput(content=f"Opening page: {url}"))
                elif output.action.type == "find_in_page":
                    pattern = output.action.pattern or ""
                    url = output.action.url or ""
                    if pattern and url:
                        yield self._output_to_sse(ToolCallOutput(content=f"Finding in page: {pattern} in {url}"))
            elif output.type == "message":
                for content in output.content:
                    if content.type == "output_text":
                        # check the type
                        final_response_parsed = self.parse_final_response(content.text)
                        yield self._output_to_sse(final_response_parsed)
            elif output.type == "function_call":
                func_name = output.name
                arguments = json.loads(output.arguments)
                tool_call_message = tool_call_progress_message(func_name=func_name, kwargs=arguments)
                yield self._output_to_sse(ToolCallOutput(content=tool_call_message))

    def send_tool_result_progress(self, tool_call_results):
        # yield tool outputs
        for res in tool_call_results:
            output_val = res["output"]
            # simple formatting for display
            content_str = ""
            if isinstance(output_val, list):
                # try to extract text from multimodal content
                display_parts = []
                for item in output_val:
                    if isinstance(item, dict):
                        if item.get("type") == "input_text":
                            display_parts.append(item["text"])
                        elif item.get("type") == "input_image":
                            display_parts.append("[image]")
                content_str = "\n".join(display_parts)
            else:
                content_str = str(output_val)

            # truncate if too long
            if len(content_str) > 300:
                content_str = content_str[:300] + "..."

            yield self._output_to_sse(ToolResponseOutput(content=f"tool output: {content_str}"))

    async def trigger_tool_calls(self, tool_calls: list, user_id: str | None = None) -> list[dict]:
        # trigger tool calls in parallel
        tasks = []
        for tool_call in tool_calls:
            tool_call_name = tool_call.name
            tool_call_kwargs = json.loads(tool_call.arguments)
            tasks.append(asyncio.create_task(call_tool(tool_call_name, tool_call_kwargs, user_id)))

        task_results = await asyncio.gather(*tasks, return_exceptions=True)  # will perserve order

        tool_call_results = []
        for tool_call, task_result in zip(tool_calls, task_results):
            if isinstance(task_result, Exception):
                msg = f"error in calling tool. {task_result}"
            else:
                msg = task_result

            tool_call_results.append({"type": "function_call_output", "call_id": tool_call.call_id, "output": msg})

        return tool_call_results

    def construct_prompt(self, ui_context: UIContext) -> list[dict]:
        # convert context from ui to openai input format
        openai_context = []
        # add developer prompt
        developer_prompt = self.system_prompt
        openai_context.append({"role": "developer", "content": developer_prompt})
        for msg in ui_context.context:
            if isinstance(msg, Message):
                if msg.role == "user":
                    openai_context.append({"role": "user", "content": msg.content})
                elif msg.role == "assistant":
                    openai_context.append({"role": "assistant", "content": msg.content})
                else:
                    print(f"unsupported role: {msg.role}")
                    continue
            elif isinstance(msg, FormRequest):
                # construct form
                form_str = ""
                if msg.description:
                    form_str += f"{msg.description}\n"
                for row in msg.rows:
                    form_str += f"{row.header}: {row.content}\n"
                openai_context.append({"role": "assistant", "content": f"Form:\n{form_str}"})
            elif isinstance(msg, FormResult):
                # construct form result
                form_str = ""
                for row in msg.rows:
                    form_str += f"{row.header}: {row.content}\n"
                openai_context.append({"role": "user", "content": f"Form result:\n{form_str}"})

            elif isinstance(msg, ChoiceRequest):
                choice_str = ""
                if msg.description:
                    choice_str += f"{msg.description}\n"
                if msg.single_choice:
                    choice_str += "Options (single choice):\n"
                else:
                    choice_str += "Options (multiple choice):\n"
                for option in msg.options:
                    choice_str += option + "\n"
                openai_context.append({"role": "assistant", "content": choice_str})

            elif isinstance(msg, ChoiceResult):
                choosen_str = f"Selected: {msg.chosen}"
                openai_context.append({"role": "user", "content": choosen_str})

            else:
                logger.error(f"unsupported context: {msg}")
                continue

        return openai_context

    def _output_to_sse(self, output: Output) -> str:
        to_yield = f"data: {json.dumps(output.model_dump(), ensure_ascii=False)}\n\n"
        logger.info(f"to yield: {to_yield}")
        return to_yield
