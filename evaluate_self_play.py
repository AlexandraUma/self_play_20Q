import re
import logging
from typing import List, Dict
from agents.frameworks.chat_llm import ChatLLM


class Evaluation:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)

    @staticmethod
    def get_session_from_logs(path_to_file: str) -> List[List[Dict[str, str]]]:
        """
        Get the session from the logs.
        Args:
            path_to_file (str): The file path to the logs.
        Returns:
            List[str]: The session from the logs.
        """
        with open(path_to_file, "r") as fp:
            log_text = fp.read()

        # Find the
        games = re.split(r'#+ Game \d+ ####+', log_text)

        all_games_turns = []
        for game in games[1:]:  # Skip the empty split before the first game
            # Extract each turn by finding lines starting with 'Guesser:' or 'Host:'
            turns = re.findall(r'----Turn \d+\nGuesser: (.*?)\nHost: (.*?)\n', game)

            # Create a list of dictionaries for each turn
            game_turns = []
            for guesser_content, host_content in turns:
                game_turns.append({"role": "Guesser", "content": guesser_content})
                game_turns.append({"role": "Host", "content": host_content})

            all_games_turns.append(game_turns)

        return all_games_turns

    @staticmethod
    def _compose_conversation(turns):
        conversation = []
        turn_number = 1

        for i in range(0, len(turns), 2):  # Iterate in pairs of Guesser and Host
            guesser_turn = turns[i]
            host_turn = turns[i + 1] if i + 1 < len(turns) else {"role": "Host", "content": ""}

            # Format the turn number and content
            conversation.append(f"----Turn {turn_number}")
            conversation.append(f"Guesser: {guesser_turn['content']}")
            conversation.append(f"Host: {host_turn['content']}")

            turn_number += 1

        return "\n".join(conversation)

    def _get_num_misleading_answers(self, conversation: str) -> int:
        """
        Get the number of misleading answers in the conversation.

        Args:
        ----
        - conversation (str): The conversation between the host and the guesser.

        Returns:
        -------
        - int: The number of misleading answers in the conversation.
        """
        llm = ChatLLM(logger=self.logger, prompt=("You will be given a conversation between a host and a guesser. "
                                                  "Your task is to identify the misleading answers given by the host. "
                                                  "Just the host's answers, not the guesser's questions."
                                                  "Return the number of misleading/incorrect Host answers in the conversation, say nothing else"
                                                  "If there are no misleading answers, return 0."))
        try:
            return int(llm.get_response_to_input(conversation))
        except ValueError as e:
            self.logger.error(f"Failed to get the number of misleading answers due to: {str(e)}")
            return -1

    def evaluate_host(self, path_to_file: str):
        """
        Using an LLM, evaluate the host agent by asking the model how many times the host agent misleads the guesser
        for each game. Then calculate the average number of misleading answers per game. This is the miss rate.

        Args:
        ----
        - game_turns (List[Dict[str, str]]): The turns of the game.
        """
        print("Evaluating Host:")

        # Get the session from the logs
        all_game_turns = self.get_session_from_logs(path_to_file)

        total_misses, total_turns = 0, 0
        for game_turns in all_game_turns:
            conversation = self._compose_conversation(game_turns)
            total_misses += self._get_num_misleading_answers(conversation)
            if total_misses != -1:
                total_turns += len(game_turns) // 2

        answer_accuracy = (total_turns - total_misses) / total_turns if total_turns > 0 else -1
        print(f"Answer Accuracy: {answer_accuracy}")

    @staticmethod
    def _calculate_win_rate(all_game_turns):
        """
        Calculate the win rate of the host agent.

        Args:
        ----
        - game_turns (List[List[Dict[str, str]]]): The turns of the games.

        Returns:
        -------
        - float: The win rate of the host agent.
        """
        num_wins = 0
        num_games = 0
        for game_turns in all_game_turns:
            if game_turns[-1]["role"] == "Host":
                num_games += 1
                if "you've got it" in game_turns[-1]["content"]:
                    num_wins += 1
        return num_wins / num_games if num_games > 0 else -1

    @staticmethod
    def _calculate_average_number_of_turns(all_game_turns):
        """
        Calculate the average number of turns taken by the host agent to guess the topic.

        Args:
        ----
        - game_turns (List[List[Dict[str, str]]]): The turns of the games.

        Returns:
        -------
        - float: The average number of turns taken by the host agent to guess the topic.
        """
        total_turns = 0
        num_games = 0
        for game_turns in all_game_turns:
            num_games += 1
            total_turns += len(game_turns) // 2
        return total_turns / num_games if num_games > 0 else -1

    @staticmethod
    def _calculate_guess_efficiency(all_game_turns):
        """
        Calculate the ratio of yes answers to no answers that the guesser received.

        Args:
        ----
        - game_turns (List[List[Dict[str, str]]]): The turns of the games.

        Returns:
        -------
        - float: The ratio of yes answers to no answers that the guesser received.
        """
        num_yes, num_no = 0, 0
        for game_turns in all_game_turns:
            for turn in game_turns:
                if turn["role"] == "Host":
                    if "yes" in turn["content"].lower():
                        num_yes += 1
                    elif "no" in turn["content"].lower():
                        num_no += 1
        num_answers = num_yes + num_no
        return num_yes / num_answers if num_answers > 0 else -1

    def evaluate_guesser(self, path_to_file: str):
        """
        Evaluate the guesser agent.

        Args:
        ----
        - file_path (str): The file path to the logs.

        """
        print("Evaluating Guesser:")
        # Get the session from the logs
        all_game_turns = self.get_session_from_logs(path_to_file)

        # Calculate the win rate of the guesser agent
        win_rate = self._calculate_win_rate(all_game_turns)
        print(f"Win rate: {win_rate}")

        # Calculate the average number of turns taken by the guesser agent to guess the topic
        average_turns = self._calculate_average_number_of_turns(all_game_turns)
        print(f"Average number of turns: {average_turns}")

        # Calculate the guesser agent's question efficiency
        guess_efficiency = self._calculate_guess_efficiency(all_game_turns)
        print(f"Guess Efficiency: {guess_efficiency}")


if __name__ == "__main__":
    import os

    evaluator = Evaluation()

    files = os.listdir("data/logs/self_play_sessions/")
    for file in files:
        print(f"---------Evaluating self play: {file.split('.')[0]}----------")
        file_path = f"data/logs/self_play_sessions/{file}"
        evaluator.evaluate_guesser(file_path)
        evaluator.evaluate_host(file_path)
        print()
