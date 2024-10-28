import sys
import time
import logging

from agents.guesser.goal_based_agent_with_react.agent import ReactGuesser
from agents.host.multi_agent_with_heuristics.agent import MultiAgentHostWithHeuristics


class SelfPlay:

    def __init__(self, num_games):
        """Initialize the SelfPlay class.

        Args:
        ----
        - num_games (int): The number of games to play.
        - [optional] guesser_agent (object): The guesser agent to use. Default is
            the SimpleGuesser agent.
        - [optional] host_agent (object): The host agent to use. Default is the
            MultiAgentHostWithHeuristics
        """
        self.logger = logging.getLogger('20Q_SelfPlay')
        self.logger.info("Initializing SelfPlay for {} games.".format(num_games))
        self.num_games = num_games

    def play_game(self, topic=None, host_agent=None, guesser_agent=None):
        """Play a single game between the host and guesser agents.
        """
        self.logger.info("Playing a single game.")

        # Initialize the agents
        host_agent = host_agent if host_agent else MultiAgentHostWithHeuristics(logger=self.logger, name="Kay")
        guesser_agent = guesser_agent if guesser_agent else ReactGuesser(logger=self.logger, name="Bob")

        # If a topic is provided, use it, otherwise use the host's topic
        if topic:
            host_agent.topic = topic

        # Hold the topic in memory
        host_agent.hold_topic_in_memory()
        print(f'---------Host is thinking of {host_agent.topic}-----------')

        # Use the greeting to start the game
        host_message = host_agent.greet_guesser()
        print(f"Host: {host_message}")

        # We play a maximum of 25 turns, regardless of the validity of the guesses in that time
        turn = 0
        for turn in range(25):
            print(f"----Turn {turn + 1}")

            # guesser makes a guess
            guesser_message = guesser_agent.make_guess(host_message)
            print(f"Guesser: {guesser_message}")

            # host responds to the guess
            time.sleep(0.8)
            host_message = host_agent.respond_to_guesser(guesser_message)
            print(f"Host: {host_message}")

            if "you've got it" in host_message or "you didn't guess it" in host_message:
                break

        # End the game
        if turn == 24:
            print("Game terminated after 25 turns.")
        else:
            print("Game over!")

    def start(self, topics=None):
        """Start the self-play session.
        """
        self.logger.info("Starting the self-play session.")

        sys.stdout = open('data/logs/self_play_sessions/react_guesser_hard.txt', 'w')
        for idx in range(self.num_games):
            print("\n", '#' * 50, f"Game {idx + 1}", '#' * 50)
            if topics:
                self.play_game(topic=topics[idx % len(topics)])
            else:
                self.play_game()
            time.sleep(20)
        sys.stdout.close()

        self.logger.info("Self-play session completed.")


if __name__ == "__main__":
    logging.basicConfig(level="ERROR")

    EASY_TOPICS = ["strawberry", "ballet shoes", "elephant", "cake", "cucumber", "puzzle", "traffic light",
                   "motorcycle", "jellyfish", "doll", "bald eagle"]

    HARD_TOPICS = ["Silver Ore", "Pressure Gauge", "Soldering Iron", "Router", "Cupcake", "Nintendo Wii",
                   "Ventilation System", "Honeydew", "Tiramisu", "Electric Screwdriver"]

# Initialize the self-play session with the number of games to play
num_games_to_play = input("Enter the number of games to play: ")
num_games_to_play = int(num_games_to_play) if num_games_to_play.isdigit() else 1
self_play = SelfPlay(num_games=num_games_to_play)

# Choose the mode of play
mode = input("Enter the mode of play (easy/hard): ").strip().lower()

if mode == "easy":
    self_play.start(EASY_TOPICS)
else:
    self_play.start(HARD_TOPICS)
