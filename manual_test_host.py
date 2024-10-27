import time
import logging
from agents.host.multi_agent_with_heuristics.agent import MultiAgentHostWithHeuristics
from agents.host.simple_reflex_agent_with_memory.agent import SimpleReflexHost
from agents.host.multi_agent_with_llms.agent import MultiAgentHost

# Constants for the game
TOPICS = ["strawberry", "cake", "cucumber", "puzzle", "doll", "traffic light", "tiger", "bald eagle", "jellyfish",
          "motorcycle"]
MAX_TURNS = 25

logging.basicConfig(level="INFO")
logger = logging.getLogger("20Q")


def get_host(agent_choice: str, index: int):
    if agent_choice == "simple":
        return SimpleReflexHost(logger=logger, name="Alice", topic=TOPICS[index])
    elif agent_choice == "multi":
        return MultiAgentHost(logger=logger, name="Alice")
    else:
        return MultiAgentHostWithHeuristics(logger=logger, name="Alice")


def greet_and_play_game(host):
    greeting = host.greet_guesser()
    print(f"{host.name}: {greeting}")
    for turn in range(MAX_TURNS):
        print(f"\n========{host.llm.context}========\n")

        print(f"----Turn {turn + 1}----")

        guesser_message = input("Guesser: ")
        if 'end' in guesser_message:
            break

        response = host.respond_to_guess(guesser_message)
        print(f"{host.name}: {response}")
        if "you've got it" in response or "you didn't guess it" in response:
            break
    print("Game over!\n")


def test_the_host():
    num_games = input("Enter the number of games to play: ")
    try:
        num_games = int(num_games)
    except ValueError:
        print('Invalid number of games. Playing 1 game by default.')
        num_games = 1

    agent_choice = input("Enter the agent to play with (simple/multi/heuristic): ").strip().lower()

    for i in range(num_games):
        host = get_host(agent_choice, i % len(TOPICS))
        print("#" * 50, f"Playing 20 Questions with the topic: {host.topic}", "#" * 50)
        greet_and_play_game(host)


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


if __name__ == "__main__":
    test_the_host()
