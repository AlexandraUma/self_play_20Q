from agents.frameworks.chat_llm import ChatLLM
from agents.utils.formatting_utils import format_conversation_context
from agents.guesser.goal_based_agent_with_react.program import guesser_prompt, reasoner_prompt

class ReactGuesser:
    """A guesser agent for the 20 Questions game that uses
    ReAct style prompting.
    """

    def __init__(self, logger, name):
        """
        Initialize the guesser agent with a logger and name.

        Args:
            logger: Logger for logging messages.
            name (str): The name of the guesser agent.
        """
        self.name = name
        self.logger = logger
        self.logger.info(f"Initializing {self.name} with prompt")

        # Initialize guesser agent using the specified prompt
        self.guesser_agent = ChatLLM(logger=logger, prompt=guesser_prompt)

        # Initialize reasoner agent with the specified prompt and without memory
        self.reasoner_agent = ChatLLM(logger=logger, prompt=reasoner_prompt, with_memory=False)

    async def make_guess(self, message):
        """
        Make a guess based on the message from the host agent using
        a single iteration of the ReAct algorithm.

        Args:
            message (str): Message from the host agent.

        Returns:
            guesser_response (str): Response from the guesser agent.
        """
        # Format the conversation context with the incoming message
        formatted_conversation = self._format_conversation(message)

        # Create the input for reasoner agent
        reasoner_input = self._create_reasoner_input(formatted_conversation)

        # Get response from reasoner agent asynchronously
        reasoner_response = await self.reasoner_agent.async_get_response_to_input(reasoner_input)
        self.logger.info(f"Reasoner responded with: {reasoner_response}")

        # Add reasoner's response to guesser agent's context
        self.guesser_agent.add_message_to_context(ChatLLM.ROLE_SYSTEM, f"OBSERVATION: {reasoner_response}")

        # Get response from guesser agent asynchronously
        guesser_response = await self.guesser_agent.async_get_response_to_input(message)
        self.logger.info(f"Guesser responded with: {guesser_response}")

        return guesser_response

    def _format_conversation(self, message):
        """
        Format the conversation context by mapping roles and appending
        the new message.

        Args:
            message (str): New message to be appended to the conversation.

        Returns:
            formatted_conversation (str): Formatted conversation context.
        """
        role_mapper = {"assistant": "Guesser", "user": "Answerer"}

        # Use formatting utility to format the conversation context
        formatted_conversation = format_conversation_context(
            self.guesser_agent.context + [{"role": "user", "content": message}], role_mapper
        )
        return formatted_conversation

    @staticmethod
    def _create_reasoner_input(formatted_conversation):
        """
        Create the input string for the reasoner agent.

        Args:
            formatted_conversation (str): The formatted conversation context.

        Returns:
            str: The input string for the reasoner agent.
        """
        return f"CONVERSATION SO FAR:\n'''\n{formatted_conversation}\n'''"