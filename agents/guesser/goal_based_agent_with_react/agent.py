import ast
import json

from agents.frameworks.chat_llm import ChatLLM
from agents.utils.formatting_utils import format_conversation_context
from agents.guesser.goal_based_agent_with_react.program import guesser_prompt, reasoner_prompt


class ReactGuesser:
    """A guesser agent for the 20 Questions game that uses
    ReAct style prompting.
    """

    def __init__(self, logger, name):
        """Initialize the guesser agent.
        """
        self.name = name
        self.logger = logger
        self.logger.info(f"Initializing {self.name} with prompt")
        self.guesser_agent = ChatLLM(logger=logger, prompt=guesser_prompt)
        self.reasoner_agent = ChatLLM(logger=logger, prompt=reasoner_prompt, with_memory=False)

    def make_guess(self, message):
        """Make a guess based on the message from the host agent
        using a single iteration of the ReAct algorithm.
        """
        # First, get the response from the reasoner agent.
        # ...get the conversation so far, this is the input to the reasoner agent.
        role_mapper = {"assistant": "Guesser", "user": "Answerer"}
        conversation_so_far = format_conversation_context(self.guesser_agent.context + [{"role": "user", "content": message}],
                                                              role_mapper)
        reasoner_input = f"CONVERSATION SO FAR:\n'''\n{conversation_so_far}\n'''"

        # Add the reasoner's response to the guesser's context.
        reasoner_response = self.reasoner_agent.get_response_to_input(reasoner_input)
        self.logger.info(f"Reasoner responded with: {reasoner_response}")
        self.guesser_agent.update_context("system",
                                          f"OBSERVATION: {reasoner_response}")

        # Now, get the guesser's response.
        response = self.guesser_agent.get_response_to_input(message)
        self.logger.info(f"Guesser responded with: {response}")
        return response
