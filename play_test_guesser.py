import logging
import asyncio
from agents.guesser.goal_based_agent_with_react.agent import ReactGuesser
from agents.guesser.goal_based_with_simple_prompt.agent import SimpleGuesser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("20Q ReactGuesser Test")


async def test_guesser():
    # choose the guesser agent
    agent_choice = input("Enter the agent to play with (simple/react): ").strip().lower()

    if agent_choice == "simple":
        guesser = SimpleGuesser(logger=logger, name="Bob")
    else:
        guesser = ReactGuesser(logger=logger, name="Bob")

    host_message = "I am thinking of an object. You have 20 questions to guess what it is. Go ahead!"
    print(f"Host (You): {host_message}")

    for i in range(20):
        print(f"----Turn {i + 1}----")
        guesser_response = await guesser.make_guess(host_message)
        print(f"Guesser: {guesser_response}")

        host_message = input("Host (You): ")
        if host_message == "stop":
            break

    print("Game over.")


if __name__ == "__main__":
    asyncio.run(test_guesser())
