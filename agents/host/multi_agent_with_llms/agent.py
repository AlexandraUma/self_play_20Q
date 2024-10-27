from agents.frameworks.zero_shot_llm import ZeroShotLLMAgent
from agents.host.multi_agent_with_llms.program import topic_suggester_prompt, state_tracker_prompt, answerer_prompt


class MultiAgentHost:
    """
    MultiAgentHost serves as a host for a guessing game, utilizing multiple agents to suggest topics,
    track game state, and provide responses to player guesses.
    """
    GREETING_MESSAGE_TEMPLATE = "Hi! I'm {name}, the host of this game. I'm thinking of an object. You have 20 questions to guess what it is. Go ahead!"

    def __init__(self, logger, name):
        """
        Initializes the MultiAgentHost with a given logger and host name.
        Args:
            logger: Logger to be used for logging purposes.
            name (str): Name of the host.
        """
        self.name = name
        self.logger = logger
        self.logger.debug("Initializing MultiAgentHost with name: %s", name)
        self._initialize_agents()
        self._hold_topic_in_memory()

    def _initialize_agents(self):
        """
        Initializes the agents for suggesting topics, tracking state, and answering questions.
        """
        self.logger.debug("Initializing agents...")
        self.topic_suggester = ZeroShotLLMAgent(logger=self.logger, prompt=topic_suggester_prompt, temperature=0.9)
        self.state_tracker = ZeroShotLLMAgent(logger=self.logger, prompt=state_tracker_prompt)
        self.answerer = ZeroShotLLMAgent(logger=self.logger, prompt=answerer_prompt)

    def _hold_topic_in_memory(self):
        """
        Add the topic to the host agent's memory.
        """
        self.logger.debug("Holding topic in memory...")
        self.topic = self._suggest_topic()
        self.logger.debug("Suggested topic: %s", self.topic)
        self.answerer.update_context("system", f"Here is the topic you're thinking of: {self.topic}")

    def _suggest_topic(self) -> str:
        """
        Suggests an appropriate object for the guesser to guess.
        Returns:
            str: Suggested topic.
        """
        self.logger.debug("Suggesting topic...")
        topic = self.topic_suggester.get_response_to_input("Suggest an appropriate object for the guesser to guess")
        self.logger.debug("Topic suggested: %s", topic)
        return topic

    def _add_guess_number_to_context(self, new_message: str):
        """
        Adds the current guess number to the answerer's context.
        Args:
            new_message (str): The new guess to add to the conversation context.
        """
        self.logger.debug("Adding guess number to context for message: %s", new_message)
        conversation_so_far = f"{self._build_answerer_conversation_context()}\nGuesser: {new_message}"
        number_of_guesses = self._state_number_of_guesses_made(conversation_so_far)
        self.logger.info("Number of guesses made: %s", number_of_guesses)
        self.answerer.update_context("system", f"Guess Number: {number_of_guesses}")

    def _build_answerer_conversation_context(self) -> str:
        """
        Builds the context of the conversation between the host and the guesser from the answerer's context.
        Returns:
            str: Formatted conversation context.
        """
        self.logger.debug("Building answerer conversation context...")
        conversation = []
        role_mapper = {"assistant": "Answerer", "user": "Guesser"}
        for entry in self.answerer.context:
            role = entry["role"]
            if role not in role_mapper:
                continue
            role = role_mapper[role]
            content = entry["content"]
            conversation.append(f"{role}: {content}")
        conversation_context = "\n".join(conversation)
        self.logger.debug("Conversation context built: %s", conversation_context)
        return conversation_context

    def _state_number_of_guesses_made(self, conversation_so_far: str) -> str:
        """
        Determines the number of guesses made based on the state tracker's response to the conversation so far.
        Args:
            conversation_so_far (str): Current conversation context.
        Returns:
            str: Number of guesses made.
        """
        self.logger.debug("Getting number of guesses made from state tracker...")
        number_of_guesses = self.state_tracker.get_response_to_input(conversation_so_far)
        self.logger.debug("State tracker response: %s", number_of_guesses)
        return number_of_guesses

    def greet_guesser(self) -> str:
        """
        Generates and returns a greeting message for the guesser.
        Returns:
            str: Greeting message.
        """
        self.logger.debug("Generating greeting message...")
        greeting = self.GREETING_MESSAGE_TEMPLATE.format(name=self.name)
        self.answerer.update_context("assistant", greeting)
        self.logger.debug("Greeting message generated: %s", greeting)
        return greeting

    def respond_to_guess(self, message: str) -> str:
        """
        Responds to the guesser's guess by updating the conversation context and getting a response from the answerer.
        Args:
            message (str): The guesser's message/guess.
        Returns:
            str: Response to the guesser's guess.
        """
        self.logger.debug("Responding to guess: %s", message)
        guess_number = self._state_number_of_guesses_made(message)
        response = self.answerer.get_response_to_input(message)
        self.logger.debug("Response to guess: %s", response)
        return response
