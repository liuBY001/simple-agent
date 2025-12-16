"""
Tool base class definition

1. tool schema
2. tool function
3. tool call message
4. tool result message

"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    @abstractmethod
    def get_schema(self) -> dict:
        raise NotImplementedError("Not implemented yet!")

    @abstractmethod
    async def call(self, **kwargs):
        # the actual tool function
        raise NotImplementedError("Not implemented yet!")

    @abstractmethod
    def tool_call_message(self, **kwargs) -> str:
        # tool call message to yield to the front end
        raise NotImplementedError("Not implemented yet!")

    @abstractmethod
    def tool_result_message(self, **kwargs) -> str:
        # the result message to yield to front end
        raise NotImplementedError("Not implemented yet!")
