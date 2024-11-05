import asyncio
import time
import logging
from agents.guesser.goal_based_agent_with_react.agent import ReactGuesser
from agents.host.multi_agent_with_heuristics.agent import MultiAgentHostWithHeuristics


class SelfPlay:
    MAX_TURNS = 25

    def __init__(self, num_games):
        """Initialize the SelfPlay class."""
        self.logger = logging.getLogger('20Q_SelfPlay')
        self.logger.info("Initializing SelfPlay for {} games.".format(num_games))
        self.num_games = num_games

    async def play_game(self, topic=None, host_agent=None, guesser_agent=None):
        """Play a single game between the host and guesser agents."""
        self.logger.info("Playing a single game.")
        game_log = []

        # Initialize the agents
        if not host_agent:
            self.logger.info("No host agent provided. Using MultiAgentHostWithHeuristics.")
            host_agent = MultiAgentHostWithHeuristics(logger=self.logger, name="Kay")
        if not guesser_agent:
            self.logger.info("No guesser agent provided. Using ReactGuesser.")
            guesser_agent = ReactGuesser(logger=self.logger, name="Bob")

        # If a topic is provided, use it, otherwise the host will choose one
        if topic:
            host_agent.topic = topic

        # Play a round of 20 Questions
        host_agent.hold_topic_in_memory()
        game_log.append(f"---------Host is thinking of {host_agent.topic}-----------")

        # Host greets the guesser
        host_message = host_agent.greet_guesser()
        game_log.append(f"Host: {host_message}")

        # Turns loop
        turn = 0
        for turn in range(SelfPlay.MAX_TURNS):
            self.logger.info(f"----Turn {turn + 1}")

            # Guesser makes a guess
            guesser_message = await guesser_agent.make_guess(host_message)
            game_log.append(f"Guesser: {guesser_message}")

            # Host responds to the guess
            host_message = await host_agent.respond_to_guesser(guesser_message)
            game_log.append(f"Host: {host_message}")

            if "you've got it" in host_message or "you didn't guess it" in host_message:
                break

        # End the game log message
        self.logger.info(
            "Game terminated after {} turns.".format(turn + 1) if turn == SelfPlay.MAX_TURNS - 1 else "Game over!"
        )
        return game_log

    async def start(self, topics=None, session_name=None):
        """Play several rounds of 20 Questions in parallel."""
        self.logger.info("Starting the self-play session for {} games.".format(self.num_games))
        if topics is None or len(topics) == 0:
            raise ValueError("Topics must be a non-empty list.")
        if not session_name:
            session_name = f"self_play_session_{int(time.time())}.txt"

        start_time = time.time()

        # Collect all tasks
        tasks = [
            asyncio.create_task(self.play_game(topic=topics[idx % len(topics)]))
            for idx in range(self.num_games)
        ]

        all_logs = await asyncio.gather(*tasks)
        end_time = time.time()
        self.logger.info(f"Session completed in {end_time - start_time:.2f} seconds.")

        # Save the logs to a file asynchronously
        await self._save_logs(session_name, all_logs)

    @staticmethod
    async def _save_logs(session_name, all_logs):
        """Save the game logs to a file."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, SelfPlay._write_logs, session_name, all_logs)

    @staticmethod
    def _write_logs(session_name, all_logs):
        """Write logs to a file (blocking)."""
        with open(session_name, "w") as f:
            for game_log in all_logs:
                for line in game_log:
                    f.write(line + "\n")
                f.write("\n\n")


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    EASY_TOPICS = ["strawberry", "ballet shoes", "elephant", "cake", "cucumber", "puzzle", "traffic light",
                   "motorcycle", "jellyfish", "doll", "bald eagle"]
    HARD_TOPICS = ["Silver Ore", "Pressure Gauge", "Soldering Iron", "Router", "Cupcake", "Nintendo Wii",
                   "Ventilation System", "Honeydew", "Tiramisu", "Electric Screwdriver"]

    # Initialize the self-play session with the number of games to play
    num_games_to_play = input("Enter the number of games to play: ").strip()
    try:
        num_games_to_play = int(num_games_to_play)
        if num_games_to_play <= 0:
            raise ValueError
    except ValueError:
        print("Invalid input. Number of games should be a positive integer. Defaulting to 1 game.")
        num_games_to_play = 1

    self_play = SelfPlay(num_games=num_games_to_play)

    # Choose the mode of play
    mode = input("Enter the mode of play (easy/hard): ").strip().lower()
    session_topics = EASY_TOPICS if mode == "easy" else HARD_TOPICS

    # Start the async self-play session
    asyncio.run(self_play.start(topics=session_topics))
