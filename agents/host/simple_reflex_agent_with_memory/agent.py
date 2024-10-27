import logging
from agents.frameworks.zero_shot_llm import ZeroShotLLMAgent
from agents.host.simple_reflex_agent_with_memory.program import simple_reflex_agent_prompt


class SimpleReflexHost:
    """
    A host agent for the 20 Questions game.

    This host agent is a simple reflex agent that responds to the guesser's messages.
    As such it's merely a wrapper around the ZeroShotLLMAgent class.
    """

    GREETING_MESSAGE_TEMPLATE = ("Hi! I'm {name}, the host of this game. I'm thinking of an object. "
                                 "You have 20 questions to guess what it is. Go ahead!")

    def __init__(self, logger, name: str, topic: str):
        """
        Initialize the host agent.
        Args:
            logger (logging.Logger): The logger instance.
            name (str): The name of the host agent.
            topic (str): The topic to add to the host agent's memory.
        """
        self.logger = logger
        self.name = name
        self.topic = topic
        self.llm = ZeroShotLLMAgent(logger=logger, prompt=simple_reflex_agent_prompt, with_memory=True)
        self._hold_topic_in_memory()
        self.logger.debug(f"Initialized SimpleReflexHost with name: {name} and topic: {topic}")

    def _hold_topic_in_memory(self):
        """
        Add the topic to the host agent's memory.
        """
        self.llm.update_context(self.llm.ROLE_SYSTEM, f"Here is the topic you're thinking of: {self.topic}")

    def greet_guesser(self) -> str:
        """
        Start the game by greeting the guesser.
        Returns:
            str: The greeting from the host agent.
        """
        scripted_greeting = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
        self.llm.update_context(self.llm.ROLE_ASSISTANT, scripted_greeting)
        self.logger.debug(f"Greeting guesser with message: {scripted_greeting}")
        return scripted_greeting

    def respond_to_guess(self, message: str) -> str:
        """
        Get the response from the host agent.
        Args:
            message (str): The message from the guesser.
        Returns:
            str: The response from the host agent.
        """
        self.logger.debug(f"Received guesser message: {message}")
        response = self.llm.get_response_to_input(message)
        self.logger.debug(f"Responding to guesser with message: {response}")
        return response
