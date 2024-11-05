import os
import logging
from typing import List, Dict, Callable, Union, Coroutine
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_random
from openai import RateLimitError, APITimeoutError, APIError
from dotenv import load_dotenv

load_dotenv()
API_KEY_ENV_VAR = "OPENAI_API_KEY"

class ChatLLM:
    """A framework for running a chat LLM with GPT 4o.
    """

    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(self, logger: logging.Logger, prompt: str, temperature: float = 0.0, with_memory: bool = True):
        """Initializes the ChatLLM class instance with gpt 40.

        Args:
            logger (logging.Logger): Logger to record activity.
            prompt (str): Initial prompt to start the chat.
            temperature (float, optional): Controls the randomness of the chat responses. Defaults to 0.0.
            with_memory (bool, optional): Flag to enable/disable conversation memory. Defaults to True.
        """
        self.logger = logger
        self.context: List[Dict[str, str]] = []  # Holds the chat context
        self.with_memory = with_memory
        self.api_key = self._load_openai_api_key()
        self.chat_llm = self._initialize_chat_llm(temperature)

        self.logger.info("Initializing ChatLLM")
        self.logger.info(f"ChatLLM will {'use' if self.with_memory else 'not use'} memory.")
        self.add_message_to_context(self.ROLE_SYSTEM, prompt)

    def _load_openai_api_key(self) -> str:
        api_key = os.getenv(API_KEY_ENV_VAR)
        if not api_key:
            raise ValueError(f"Please set the {API_KEY_ENV_VAR} environment variable.")
        self.logger.info(f"Loaded OpenAI API key: {api_key[:4]}... (truncated)")
        return api_key

    def _initialize_chat_llm(self, temperature: float) -> ChatOpenAI:
        return ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=0,
            api_key=self.api_key
        )

    async def _async_invoke_llm(self) -> str:
        return await self._invoke_llm_on_context(self.chat_llm.ainvoke, is_async=True)

    def _invoke_llm(self) -> str:
        return self._invoke_llm_on_context(self.chat_llm.invoke, is_async=False)

    def add_message_to_context(self, role: str, new_message: str):
        """Adds a new message to the chat context.

        Args:
            role (str): The role of the message sender (e.g., system, user, assistant).
            new_message (str): The new message to add.
        """
        self.context.append({"role": role, "content": new_message})

    @retry(stop=stop_after_attempt(3), wait=wait_random(0.1, 0.5),
           retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)))
    def _invoke_llm_on_context(self, llm_method: Callable, is_async: bool) -> Union[str, Coroutine]:
        """Invoke the LLM on the context using the provided method, handling
        both sync and async cases.
        """
        self.logger.info(f"{'Async ' if is_async else ''}Invoking LLM with context")
        try:
            if is_async:
                # Asynchronous invocation
                async def async_invoke():
                    async_response = await llm_method(self.context)
                    return async_response.content
                return async_invoke()
            else:
                # Synchronous invocation
                response = llm_method(self.context)
                return response.content
        except (APIError, APITimeoutError, RateLimitError) as e:
            error_message = f"Failed to invoke LLM after 3 attempts due to: {str(e)}"
            self.logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            self.logger.error(error_message)
            return error_message

    async def async_get_response_to_input(self, new_message: str) -> str:
        """Asynchronously generate a response to the new message and update the conversation history.

        Args:
            new_message (str): The new message from the user.

        Returns:
            str: The response to the new message.
        """
        self.add_message_to_context(self.ROLE_USER, new_message)
        response = await self._async_invoke_llm()
        self._maybe_update_context(self.ROLE_ASSISTANT, response)
        return response

    def get_response_to_input(self, new_message: str) -> str:
        """Generate a response to the new message and update the conversation history.

        Args:
            new_message (str): The new message from the user.

        Returns:
            str: The response to the new message.
        """
        self.add_message_to_context(self.ROLE_USER, new_message)
        response = self._invoke_llm()
        self._maybe_update_context(self.ROLE_ASSISTANT, response)
        return response

    def _maybe_update_context(self, role: str, new_message: str):
        """Helper function for *get_response_to_input. Only updates the chat
        history if the LLM was initialised to use memory
        """
        if self.with_memory:
            # Adds the message to the context if memory is used
            self.add_message_to_context(role, new_message)
        else:
            # Keeps only the first message in context if memory isn't used
            self.context = self.context[:1]
