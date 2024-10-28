from agents.frameworks.chat_llm import ChatLLM
from agents.guesser.goal_based_with_simple_prompt.program import simple_prompt_template


class SimpleGuesser:
    """A simple guesser agent for the 20 Questions game.
    """

    def __init__(self, logger, name):
        """Initialize the guesser agent.
        """
        self.name = name
        self.logger = logger
        self.logger.info(f"Initializing {self.name} with prompt")
        self.llm = ChatLLM(logger=logger, prompt=simple_prompt_template.format(name=name))

    def make_guess(self, message):
        """Make a guess based on the message from the host agent.
        """
        response = self.llm.get_response_to_input(message)
        self.logger.info(f"Guesser responded with: {response}")
        return response