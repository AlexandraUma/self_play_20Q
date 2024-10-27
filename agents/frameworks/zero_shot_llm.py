import os
import logging
from typing import List, Dict
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_random
from openai import RateLimitError, APITimeoutError, APIError
from dotenv import load_dotenv

load_dotenv()
API_KEY_ENV_VAR = "OPENAI_API_KEY"


class ZeroShotLLMAgent:
    """A zero-shot LLM that stores the conversation history.
    In this 20Q project, this class is typically instantiated for the host and
    the guesser agents. As such, logging for the public methods is left to the
    caller.
    """
    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(self, logger: logging.Logger, prompt: str, temperature: float = 0.0, with_memory: bool = True):
        """
        Initialize the ZeroShotLLMAgent.
        Args:
            logger (logging.Logger): The logger instance.
            prompt (str): The initial system prompt.
            temperature (float): The temperature for the OpenAI model.
        """
        self.logger = logger
        self.with_memory = with_memory
        self.context: List[Dict[str, str]] = []
        self.logger.debug("Initializing ZeroShotLLMAgent")

        if self.with_memory:
            self.logger.debug("ZeroShotLLMAgent will use memory.")
        else:
            self.logger.debug("ZeroShotLLMAgent will not use memory.")

        self.api_key = self._load_openai_api_key()
        self.chat_llm = self._initialize_chat_llm(temperature)
        self.update_context(self.ROLE_SYSTEM, prompt)

    def _load_openai_api_key(self) -> str:
        """Load the OpenAI API key from the environment."""
        api_key = os.getenv(API_KEY_ENV_VAR)
        if not api_key:
            raise ValueError(f"Please set the {API_KEY_ENV_VAR} environment variable.")
        self.logger.debug(f"Loaded OpenAI API key: {api_key[:4]}... (truncated)")
        return api_key

    def _initialize_chat_llm(self, temperature: float) -> ChatOpenAI:
        """Initialize the ChatOpenAI model."""
        return ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=0,
            api_key=self.api_key
        )

    @retry(stop=stop_after_attempt(3), wait=wait_random(0.1, 0.5),
           retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)))
    def _invoke_llm_on_context(self) -> str:
        """
        Invoke the LLM with the conversation history.
        Returns the response from the LLM.
        """
        self.logger.debug(f"Invoking LLM with context: {self.context}")
        try:
            response = self.chat_llm.invoke(self.context).content
            self.logger.debug(f"Received response from LLM: {response}")
            return response
        except (APIError, APITimeoutError, RateLimitError) as e:
            error_message = f"Failed to invoke LLM after 3 attempts due to: {str(e)}"
            self.logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            self.logger.error(error_message)
            return error_message

    def get_response_to_input(self, new_message: str) -> str:
        """
        Generate a response to the new message and update the conversation history
        if memory is enabled.
        
        Args:
            new_message (str): The new message from the user.
        Returns:
            str: The response to the new message.
        """
        self.update_context(self.ROLE_USER, new_message)
        response = self._invoke_llm_on_context()

        if self.with_memory:
            self.update_context(self.ROLE_ASSISTANT, response)
        else:
            # If the memory is disabled, only keep the system messages #Todo: this is not efficient
            self.context = [entry for entry in self.context if entry["role"] == self.ROLE_SYSTEM]

        return response

    def update_context(self, role: str, new_message: str):
        """
        Update the conversation history with a new message.
        Args:
            role (str): The role of the speaker ("system", "user", or "assistant").
            new_message (str): The new message to add to the conversation history.
        """
        self.context.append({"role": role, "content": new_message})
