from abc import ABC, abstractmethod

from ..schema import UIContext


class ResponsiveAgent(ABC):

    @abstractmethod
    async def construct_prompt(self, context: UIContext):
        # convert the actual context to the prompt which the LLM api accepts
        raise NotImplementedError("not implemented yet!")

    @abstractmethod
    async def trigger(self, prompt):
        # async generator, yield the progress infomation and final response
        yield
