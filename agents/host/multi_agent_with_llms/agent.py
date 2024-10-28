from agents.frameworks.chat_llm import ChatLLM
from agents.utils.formatting_utils import format_conversation_context
from agents.host.multi_agent_with_llms.program import topic_suggester_prompt, state_tracker_prompt, answerer_prompt


class MultiAgentHost:
    """
    MultiAgentHost serves as a host for a guessing game, utilizing multiple agents to suggest topics,
    track game state, and provide responses to player guesses.
    """
    GREETING_MESSAGE_TEMPLATE = "Hi! I'm {name}, the host of this game. I'm thinking of an object. You have 20 questions to guess what it is. Go ahead!"

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
        self.logger.info("Initializing MultiAgentHost with name: %s", name)
        self._initialize_agents()

    def _initialize_agents(self):
        """
        Initializes the agents for suggesting topics, tracking state, and answering questions.
        """
        self.logger.info("Initializing agents...")
        self.topic_suggester = ChatLLM(logger=self.logger, prompt=topic_suggester_prompt, temperature=0.9)
        self.state_tracker = ChatLLM(logger=self.logger, prompt=state_tracker_prompt, with_memory=False)
        self.answerer = ChatLLM(logger=self.logger, prompt=answerer_prompt)

    def _suggest_topic(self) -> str:
        """
        Suggests an appropriate object for the guesser to guess.
        Returns:
            str: Suggested topic.
        """
        self.logger.info("Suggesting topic...")
        topic = self.topic_suggester.get_response_to_input("Suggest an appropriate object for the guesser to guess")
        self.logger.info("Topic suggested: %s", topic)
        return topic

    def _get_guess_number_from_state_tracker(self) -> str:
        """
        The Guess Number is the number of valid guesses made by the guesser, assuming the current
        guess is a valid guess. E.g. If the user has made 2 valid guesses, in the current
        turn, the guess number will be 3.

        The state tracker returns the number of valid guesses so far. We increment this number by 1
        Returns:
            str: Number of guesses made.
        """
        self.logger.info("Getting the guess number from state tracker...")

        # Get the conversation context so far
        role_mapper = {"assistant": "Answerer", "user": "Guesser"}
        conversation_so_far = format_conversation_context(self.answerer.context, role_mapper)

        # Get the guess number from the state tracker
        guess_number = int(self.state_tracker.get_response_to_input(conversation_so_far)) + 1

        self.logger.info("Guess Number: %s", guess_number)
        return str(guess_number)

    def hold_topic_in_memory(self):
        """
        Add the topic to the host agent's memory.
        """
        self.logger.info("Getting topic to hold in memory...")
        if not self.topic:
            self.topic = self._suggest_topic()
        self.answerer.update_context("system", f"Here is the topic you're thinking of: {self.topic}")

    def greet_guesser(self) -> str:
        """
        Generates and returns a greeting message for the guesser.
        Returns:
            str: Greeting message.
        """
        self.logger.info("Generating greeting message...")
        greeting = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
        self.answerer.update_context("assistant", greeting)
        return greeting

    def respond_to_guesser(self, new_message: str) -> str:
        """
        Responds to the guesser's guess by updating the conversation context and getting a response from the answerer.
        Args:
            new_message (str): The guesser's message/guess.
        Returns:
            str: Response to the guesser's guess.
        """
        self.logger.info("Responding to guess: %s", new_message)

        # Add the current guess number to the answerer's context
        guess_number = self._get_guess_number_from_state_tracker()
        self.answerer.update_context("system", f"Guess Number: {guess_number}")

        # Get the response from the answerer
        response = self.answerer.get_response_to_input(new_message)
        self.logger.info("Responding to guesser with: %s", response)
        return response
