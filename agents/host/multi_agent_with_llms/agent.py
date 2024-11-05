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
            logger: Logger instance for logging purposes.
            name (str): Name of the host.
            topic (str, optional): Topic to add to the host agent's memory. Defaults to None.
        """
        self.name = name
        self.logger = logger
        self.topic = topic
        self.logger.info("Initializing MultiAgentHost with name: %s", name)
        self._initialize_agents()

    def _initialize_agents(self):
        """
        Initializes the agents for suggesting topics, tracking game state, and answering questions.
        """
        self.logger.info("Initializing agents...")
        self.topic_suggester = ChatLLM(logger=self.logger, prompt=topic_suggester_prompt, temperature=0.9)
        self.state_tracker = ChatLLM(logger=self.logger, prompt=state_tracker_prompt, with_memory=False)
        self.answerer = ChatLLM(logger=self.logger, prompt=answerer_prompt)

    def _get_suggested_topic(self) -> str:
        """
        Suggests an appropriate object for the guesser to guess.

        Returns:
            str: Suggested topic.
        """
        self.logger.info("Suggesting topic...")
        topic = self.topic_suggester.get_response_to_input("Suggest an appropriate object for the guesser to guess")
        self.logger.info("Topic suggested: %s", topic)
        return topic

    async def _get_guess_number(self) -> str:
        """
        Returns the incremented number of valid guesses made by the guesser.

        Returns:
            str: Number of guesses made.
        """
        self.logger.info("Getting the guess number from the state tracker...")
        conversation_so_far = self._format_conversation_context()
        guess_number = await self.state_tracker.async_get_response_to_input(conversation_so_far)
        guess_number = int(guess_number) + 1
        self.logger.info("Guess Number: %s", guess_number)
        return str(guess_number)

    def _format_conversation_context(self) -> str:
        """
        Formats the conversation context for the state tracker.

        Returns:
            str: Formatted conversation context.
        """
        role_mapper = {"assistant": "Answerer", "user": "Guesser"}
        return format_conversation_context(self.answerer.context, role_mapper)

    def hold_topic_in_memory(self):
        """
        Adds the topic to the host agent's memory.

        Returns:
            str: The topic to be held in memory.
        """
        self.logger.info("Getting topic to hold in memory...")
        if not self.topic:
            self.topic = self._get_suggested_topic()
        self.answerer.add_message_to_context("system", f"Here is the topic you're thinking of: {self.topic}")
        return self.topic

    def greet_guesser(self) -> str:
        """
        Generates and returns a greeting message for the guesser.

        Returns:
            str: Greeting message.
        """
        self.logger.info("Generating greeting message...")
        greeting = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
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
        self.logger.info("Responding to guess: %s", new_message)
        guess_number = await self._get_guess_number()
        self.answerer.add_message_to_context("system", f"Guess Number: {guess_number}")
        response = await self.answerer.async_get_response_to_input(new_message)
        self.logger.info("Responding to guesser with: %s", response)
        return response