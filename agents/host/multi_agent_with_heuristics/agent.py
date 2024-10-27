import random
import pandas as pd
from typing import List
from agents.frameworks.zero_shot_llm import ZeroShotLLMAgent
from agents.host.multi_agent_with_llms.program import answerer_prompt


class MultiAgentHostWithHeuristics:
    """
    MultiAgentHost serves as a host for a guessing game, utilizing multiple agents to suggest topics,
    track game state, and provide responses to player guesses. In this version, the topic suggester
    and state tracker agents are replaced with heuristics.
    """
    GREETING_MESSAGE_TEMPLATE = "Hi! I'm {name}, the host of this game. I'm thinking of an object. You have 20 questions to guess what it is. Go ahead!"
    KEYWORDS_FILE_PATH = "data/keywords.csv"

    def __init__(self, logger, name):
        """
        Initializes the MultiAgentHost with a given logger and host name.
        Args:
            logger: Logger to be used for logging purposes.
            name (str): Name of the host.
        """
        self.name = name
        self.logger = logger
        self.keywords = self._load_keywords()
        self.logger.debug("Initializing MultiAgentHostWithHeuristics.")
        self._initialize_agents()
        self._hold_topic_in_memory()
        self.logger.debug("MultiAgentHostWithHeuristics initialized successfully.")

    def _initialize_agents(self):
        """
        Initializes the agents for suggesting topics, tracking state, and answering questions.
        """
        self.logger.debug("Initializing ZeroShotLLMAgent for answerer.")
        self.answerer = ZeroShotLLMAgent(logger=self.logger, prompt=answerer_prompt)

    def _hold_topic_in_memory(self):
        """
        Add the topic to the host agent's memory.
        """
        self.topic = self._suggest_topic()
        self.logger.debug(f"Selected topic: {self.topic}")
        self.answerer.update_context("system", f"Here is the topic you're thinking of: {self.topic}")

    def _suggest_topic(self) -> str:
        """
        Suggests an appropriate object for the guesser to guess.
        Returns:
            str: Suggested topic.
        """
        topic = random.choice(self.keywords).title()
        self.logger.debug(f"Suggested topic: {topic}")
        return topic

    def _load_keywords(self) -> List[str]:
        """
        Loads keywords from a CSV file.
        Returns:
            List[str]: List of keywords.
        """
        self.logger.debug(f"Loading keywords from {self.KEYWORDS_FILE_PATH}")
        keywords = pd.read_csv(self.KEYWORDS_FILE_PATH).keyword.tolist()
        self.logger.debug(f"Keywords loaded: {len(keywords)} found.")
        return keywords

    def _add_guess_to_context(self, guess: str):
        """
        Adds the current guess number to the answerer's context.
        Args:
            guess (str): The new guess to add to the conversation context.
        """
        guess_count = self._count_guesses(guess)
        self.logger.debug(f"Adding guess to context. Guess: {guess}, Guess Count: {guess_count}")
        self.answerer.update_context("system", f"Guess Number: {guess_count}")

    def _count_guesses(self, guess: str) -> str:
        """
        Counts the number of yes/no guesses made by the guesser by counting the number of times
        the answerer has responded with "Yes" or "No".
        Args:
            guess (str): Current conversation context.
        Returns:
            str: Number of guesses made.
        """
        count = 0
        for entry in self.answerer.context + [{"role": "assistant", "content": guess}]:
            if entry["role"] == "assistant":
                response = entry["content"].strip('.').lower()
                if response == "yes" or response == "no":
                    count += 1
        self.logger.info("Number of guesses made: %s", count)
        return str(count)

    def greet_guesser(self) -> str:
        """
        Generates and returns a greeting message for the guesser.
        Returns:
            str: Greeting message.
        """
        greeting = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
        self.logger.debug(f"Greeting guesser with message: {greeting}")
        self.answerer.update_context("assistant", greeting)
        return greeting

    def respond_to_guess(self, guess: str) -> str:
        """
        Responds to the guesser's guess by updating the conversation context and getting a response from the answerer.
        Args:
            guess (str): The guesser's message/guess.
        Returns:
            str: Response to the guesser's guess.
        """
        self.logger.debug(f"Responding to guess: {guess}")
        self._add_guess_to_context(guess)
        response = self.answerer.get_response_to_input(guess)
        self.logger.debug(f"Answerer's response: {response}")
        return response
