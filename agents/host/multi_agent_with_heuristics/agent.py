import random
import pandas as pd
from typing import List
from agents.frameworks.chat_llm import ChatLLM
from agents.host.multi_agent_with_heuristics.program import answerer_prompt


class MultiAgentHostWithHeuristics:
    """
    MultiAgentHost serves as a host for a guessing game, utilizing multiple agents to suggest topics,
    track game state, and provide responses to player guesses. In this version, the topic suggester
    and state tracker agents are replaced with heuristics.
    """
    GREETING_MESSAGE_TEMPLATE = "Hi! I'm {name}, the host of this game. I'm thinking of an object. You have 20 questions to guess what it is. Go ahead!"
    KEYWORDS_FILE_PATH = "data/keywords.csv"

    def __init__(self, logger, name, topic=None):
        """
        Initializes the MultiAgentHost with a given logger and host name.
        Args:
            logger: Logger to be used for logging purposes.
            name (str): Name of the host.
            optional topic (str): The topic to add to the host agent's memory.
        """
        self.name = name
        self.logger = logger
        self.topic = topic
        self.keywords = self._load_keywords()
        self.logger.info("Initializing MultiAgentHostWithHeuristics.")
        self._initialize_agents()
        self.logger.info("MultiAgentHostWithHeuristics initialized successfully.")

    def _initialize_agents(self):
        """
        Initializes the agents for suggesting topics, tracking state, and answering questions.
        """
        self.answerer = ChatLLM(logger=self.logger, prompt=answerer_prompt)

    def _suggest_topic(self) -> str:
        """
        Suggests an appropriate object for the guesser to guess.
        Returns:
            str: Suggested topic.
        """
        topic = random.choice(self.keywords).title()
        self.logger.info(f"Suggested topic: {topic}")
        return topic

    def _load_keywords(self) -> List[str]:
        """
        Loads keywords from a CSV file.
        Returns:
            List[str]: List of keywords.
        """
        self.logger.info(f"Loading keywords from {self.KEYWORDS_FILE_PATH}")
        keywords = pd.read_csv(self.KEYWORDS_FILE_PATH).keyword.tolist()
        self.logger.info(f"Keywords loaded: {len(keywords)} found.")
        return keywords

    def _get_guess_number(self) -> str:
        """
        The Guess Number is the number of valid guesses made by the guesser, assuming the current
        guess is a valid guess. E.g. If the user has made 2 valid guesses, in the current
        turn, the guess number will be 3.

        We get the guess number by counting the number of times the answerer has responded
        with "Yes" or "No" to the guesser's guesses and incrementing the count by 1.

        Returns:
            str: Guess number as a string.
        """
        guess_number = 1
        for entry in self.answerer.context:
            if entry["role"] == "assistant":
                host_response = entry["content"].strip('.').lower()
                if host_response in ["yes", "no"]:
                    guess_number += 1
        self.logger.info("Guess Number: %s", guess_number)
        return str(guess_number)

    def hold_topic_in_memory(self):
        """
        Add the topic to the host agent's memory.
        """
        if self.topic is None:
            self.topic = self._suggest_topic()
        self.answerer.add_message_to_context("system", f"Here is the topic you're thinking of: {self.topic}")

    def greet_guesser(self) -> str:
        """
        Generates and returns a greeting message for the guesser.
        Returns:
            str: Greeting message.
        """
        greeting = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
        self.logger.info(f"Greeting guesser with message: {greeting}")
        self.answerer.add_message_to_context("assistant", greeting)
        return greeting

    async def respond_to_guesser(self, new_message: str) -> str:
        """
        Responds to the guesser's guess by updating the conversation context and getting a response from the answerer.
        Args:
            new_message (str): The guesser's message/guess.
        Returns:
            str: Response to the guesser's guess.
        """
        self.logger.info(f"Responding to guess: {new_message}")

        # Add the current guess number to the answerer's context
        guess_number = self._get_guess_number()
        self.answerer.add_message_to_context("system", f"Guess Number: {guess_number}")

        # Get the response from the answerer
        response = await self.answerer.async_get_response_to_input(new_message)
        if guess_number == "19":
            response += " You have one guess left. Make it count!"
        self.logger.info(f"Responding to guesser with: {response}")
        return response
