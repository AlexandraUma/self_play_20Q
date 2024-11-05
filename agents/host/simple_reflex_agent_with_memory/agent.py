import logging
from agents.frameworks.chat_llm import ChatLLM
from agents.host.simple_reflex_agent_with_memory.program import simple_reflex_agent_prompt

class SimpleReflexHost:
    """
    A host agent for the 20 Questions game.
    This host agent is a simple reflex agent with memory, that responds to the guesser's messages.
    It is essentially a wrapper around the ChatLLM class.
    """

    GREETING_MESSAGE_TEMPLATE = (
        "Hi! I'm {name}, the host of this game. I'm thinking of an object. "
        "You have 20 questions to guess what it is. Go ahead!"
    )

    ERROR_TOPIC_REQUIRED = "A topic must be provided to the SimpleReflexHost"

    def __init__(self, logger: logging.Logger, name: str, topic: str):
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
        self._validate_and_initialize()

    def _validate_and_initialize(self):
        """
        Validate the topic and initialize the language model.
        """
        if not self.topic:
            raise ValueError(self.ERROR_TOPIC_REQUIRED)
        self.llm = ChatLLM(logger=self.logger, prompt=simple_reflex_agent_prompt)
        self.logger.info(f"Initialized SimpleReflexHost with name: {self.name} and topic: {self.topic}")

    def hold_topic_in_memory(self):
        """
        Add the topic to the host agent's memory.
        """
        self.llm.add_message_to_context(self.llm.ROLE_SYSTEM, f"Here is the topic you're thinking of: {self.topic}")

    def greet_guesser(self) -> str:
        """
        Start the game by greeting the guesser.

        Returns:
            str: The greeting from the host agent.
        """
        greeting_message = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
        self.llm.add_message_to_context(self.llm.ROLE_ASSISTANT, greeting_message)
        self.logger.info(f"Greeting guesser with message: {greeting_message}")
        return greeting_message

    async def respond_to_guesser(self, guesser_message: str) -> str:
        """
        Get the response from the host agent.

        Args:
            guesser_message (str): The message from the guesser.

        Returns:
            str: The response from the host agent.
        """
        self.logger.info(f"Received guesser message: {guesser_message}")
        response = await self.llm.async_get_response_to_input(guesser_message)
        self.logger.info(f"Responding to guesser with: {response}")
        return response