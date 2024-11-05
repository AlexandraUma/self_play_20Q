import time
import logging
import asyncio
from agents.host.multi_agent_with_heuristics.agent import MultiAgentHostWithHeuristics
from agents.host.simple_reflex_agent_with_memory.agent import SimpleReflexHost
from agents.host.multi_agent_with_llms.agent import MultiAgentHost

# Constants for the game
TOPICS = ["elephant", "strawberry", "cake", "cucumber", "puzzle", "doll", "traffic light", "tiger", "bald eagle", "jellyfish",
          "motorcycle", "ballet shoes"]

MAX_TURNS = 25

logging.basicConfig(level="INFO")
logger = logging.getLogger("20Q")


def test_topic_guesser():
    agent_config = input("Enter the multi-agent config to test (llm/heuristics): ").strip().lower()
    if agent_config == "llm":
        multi_agent_host = MultiAgentHost(logger=logger, name="Alice")
    else:
        multi_agent_host = MultiAgentHostWithHeuristics(logger=logger, name="Alice")
    all_topics = []
    for i in range(30):
        topic = multi_agent_host._suggest_topic()
        time.sleep(0.2)
        all_topics.append(topic)
    print(f"Total topics suggested: {len(all_topics)}")
    print(f"Unique topics suggested: {len(set(all_topics))}")
    print(f"Topics suggested: {set(all_topics)}")


def get_host(agent_choice: str, topic=None):
    if agent_choice == "simple":
        return SimpleReflexHost(logger=logger, name="Alice", topic=topic)
    elif agent_choice == "multi":
        return MultiAgentHost(logger=logger, name="Alice")
    else:
        return MultiAgentHostWithHeuristics(logger=logger, name="Alice")


async def play_game(host, game_index, topic=None):
    print("#" * 50, f"Game {game_index}", "#" * 50)

    # Set the topic if provided
    if topic:
        host.topic = topic

    # Hold the topic in memory
    host.hold_topic_in_memory()
    print(f'---------Host is thinking of {host.topic}-----------')

    # Use the greeting to start the game
    greeting = host.greet_guesser()
    print(f"{host.name}: {greeting}")

    # We play a maximum of 25 turns, regardless of the validity of the guesses in that time
    for turn in range(MAX_TURNS):
        print(f"----Turn {turn + 1}----")
        guesser_message = input("Guesser: ")
        if 'end' in guesser_message:
            break

        response = await host.respond_to_guesser(guesser_message)
        print(f"{host.name}: {response}")
        if "you've got it" in response or "you didn't guess it" in response:
            break

    # End the game
    if turn == 24:
        print("Game terminated after 25 turns.")
    else:
        print("Game over!\n")


async def test_the_host():
    num_games = input("Enter the number of games to play: ")
    try:
        num_games = int(num_games)
    except ValueError:
        print('Invalid number of games. Playing 1 game by default.')
        num_games = 1

    agent_choice = input("Enter the agent to play with (simple/multi/heuristic): ").strip().lower()

    for i in range(num_games):
        # for the simple agent, we need to set the topic before we even begin.
        if agent_choice == "simple":
            topic = TOPICS[i % len(TOPICS)]
        else:
            topic = None
        host = get_host(agent_choice, topic)
        await play_game(host, game_index=i+1, topic='strawberry')


if __name__ == "__main__":
    asyncio.run(test_the_host())