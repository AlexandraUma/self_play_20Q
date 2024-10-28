# Self-Play of 20Q with LLMs


# Section 1: The Nature of the 20Q Task Environment

In this section, we describe the nature of the 20Q task using the taxonomy outlined by Stuart Russell and Peter Norvig in *Artificial Intelligence: A Modern Approach*.

The 20Q environment is:



* **Multi-agent:** The game involves two delineated roles—the ***host*** and the ***guesser*** — each with the ability to act independently. Each role/agent has a (hidden) state that must be communicated to the other to be known.
* **Partially observable:**  Each agent in the environment does not know the “thoughts”  of the other.
* **Competitive (or Semi-cooperative)**: 20Q can be a competitive game, with each agent in the environment seeking to optimise their performance to best the other, and “win” the game. In this competitive mode, the host aims to suggest a topic that the guesser cannot guess (while sticking to whatever constraints the game sets). The guesser, for their part, aims to guess the topic, in as few turns as possible.

    The game can also be played semi-cooperatively. For example, it could be played with a doting father as host and his young son as the guesser.  The father-host could aim to make the game tough enough to be engaging but easy enough for the son to win.

* **Deterministic:** Ignoring the inherent uncertainty due to partial observability and the multi-agent nature, 20Q can be considered a deterministic environment. As Russell and Norvig state in *Artificial Intelligence: A Modern Approach*, if the next state of the game is solely determined by the current state and the agents’ action, then the environment is deterministic. (Of course, one could also view it as stochastic by considering the ignored elements.)
* **Sequential:** When played strategically, each guess influences subsequent ones. A bad player might treat the game episodically, causing the game to devolve into randomness.
* **Static:** While agents are "thinking," the game's state remains unchanged
* **Discrete:**
    * **Time:** The game has exactly 20 turns, which do not need to occur in real time.
    * **Outcomes:** The possible outcomes are win, lose (at turn 20), or continue.
    * **Actions:** For the host, actions are simple: yes, no, you win, you lose. For the guesser, while more complex, actions can still be considered discrete—each guess is an atomic unit within a vast but finite set of possible guesses.
* **Known:** Given the clearly stated rules, the environment, despite being partially observable and extensive, is known.


# Section 2: Project Scope

Owing to time restrictions, the scope of this project is limited as follows:



1. **Question Limit:** Only 20 yes/no questions are allowed. Non-yes/no questions do not count towards this limit.
2. **Question Format**: Only yes/no questions. Everything else is met with a redirect. 
3. **Answer Format:** Responses must be strictly "yes", "no”, “yes, you win!”, “no, you lose” or “please ask a yes/no question”. No additional explanations or context will be provided.
4. **Agent Turn:** Each agent will only participate in one turn of the game.
5. **Topic Scope:** The game will focus on common noun topics.


# Section 3: The Agents

The 20Q game involves two key agents: the host and the guesser. In the following sections, we delve into the implementations and preliminary evaluations of these agents. 


### The Host

The host has three primary responsibilities:



1. **Topic Selection:** Choosing a subject for the guesser to identify.
2. **Guess Evaluation:** Assessing the accuracy of each guess and providing feedback.
3. **Turn Tracking:** Monitoring the number of guesses to ensure adherence to the 20-question limit.

The host's performance was evaluated based on the following criteria:



* **Topic Variety:** The diversity of topics presented.
* **Guess Evaluation Accuracy:** The precision of the host's judgments on guess correctness.
* **Turn Tracking:** Adherence to the 20-question limit and avoidance of premature game termination.

**Topic difficulty** is assessed in this exploration.

To assess these criteria, we will conduct both manual and automated evaluations. Manual evaluations will be conducted initially, followed by automated evaluations in self-play sessions.


### Simple Reflex Host With Memory

Given the reactive nature of the host's role, a Simple Reflex Agent with Memory is a suitable implementation. This agent, a language model, is prompted with simple if-then rules and stores interaction history to inform future responses.

A manual evaluation of six game sessions yielded the following results:



* **Guess Evaluation Accuracy:** 99.2% (One incorrect evaluation out of 120 questions)
* **Turn Tracking:** 0% accuracy (Consistently exceeded the 20-question limit)

While the agent demonstrated high accuracy in evaluating guesses, it failed to adhere to the turn limit. This simple reflex host with memory can be considered a simplified **model-based reflex agent**, as it stores the conversation history to infer the number of guesses and determine the appropriate end-game condition.


### Multi-Agent Host

To address the limitations of the Simple Reflex Host with Memory, a Multi-Agent Host was implemented. This approach would have incorporated a **topic suggester** and a **state tracker**, both simple reflex agents without memory, to work in conjunction with the answerer. This approach showed promise, however given that we’ve limited the scope of the game for this simple exploration, a more practical approach was adopted: 



* **Topic Suggester **was replaced with a simple function that selects topics from a [curated corpus](https://www.kaggle.com/code/waechter/llm-20-questions-games-dataset/output?select=keywords.csv).
* **State Tracking **was replaced with a function that estimates guess number by counting the number of “yes” and “no” host responses.  This function relies on the ability of the answerer to only respond to the host with “yes” or “no” as instructed.

This simplified approach, while not utilising full-fledged agents, effectively addresses the issues of topic variety and turn tracking. This Multi-Agent Host, enhanced with heuristics, achieved 100% accuracy in turn tracking, and in 30 game sessions, did not repeat topics as the probability of picking each word in keyword corpus is about 0.06%.


## The Guesser

The guesser's primary objective is to correctly identify the hidden topic using as few questions as possible. To achieve this, the guesser must employ effective questioning strategies that efficiently narrow down the search space.

To evaluate the guesser's performance, we will consider the following metrics:



1. **Win Rate:** The percentage of games  won.
2. **Question Efficiency:** A measure of the guesser's efficiency. A good guesser should maximise "yes" responses, minimising unnecessary questions. This metric calculates the ratio of "yes" to "no" responses received.
3. **Average Turns: **Average number of turns used during the game.

The rest of this section will detail the implementation and evaluation of various guesser agent iterations.


### Goal-Based Host with Simple Prompting

Unlike the host agent, the guesser agent's task is inherently more challenging. We cannot pre-specify questions due to the unknown topic. Instead, the agent must autonomously generate questions based on a simple goal: accurately guessing the topic.

Automatic evaluation showed  a 70% win rate for easy topics, it struggled with tougher ones, achieving only 50% accuracy. It's important to note that these results are based on a limited sample size of 10 games per difficulty level. Additionally, the agent's question efficiency was around 40%, indicating room for improvement in its ability to efficiently explore the search space.


### Goal-Based Host with Explicit Reasoning

An initial attempt to incorporate a reasoning component into the agent proved unsuccessful. The resulting agent exhibited a preference for depth-first search strategies, which is suboptimal given the vastness of the search space. For instance, after correctly identifying that "ballet shoes" could be found indoors, the agent wasted 7 guesses attempting to pinpoint the specific room.

While these results suggest that reasoning could be a valuable tool, further research is necessary to develop a more effective reasoning component for the agent.


# Section 4: Improvements

This document and the accompanying codebase present an initial exploration of the self-play 20Q task. While promising, the current agents have room for improvement in several areas:

**Agent Enhancements:**



* **Host Agent:**
    * Incorporate a reasoning component, such as a ReAct framework or chain-of-thought prompting, to enhance guess evaluation accuracy.
* **Guesser Agent:**
    * Improve reasoning capabilities to minimise redundant questions and avoid "tunnel vision."
    * Train the agent using Reinforcement Learning to optimise question selection.

**Experimental Setup:**



* **Parallelism:** Implement asynchronous execution of agent pairs to accelerate large-scale evaluation.
* **Codebase:** Reorganise and refactor the code for improved readability and maintainability.

**Game Variations:**



* **"Sometimes" Answer:** Introduce a third answer category to facilitate more nuanced reasoning.
* **Categorised Topics:** Limit topic exploration to specific categories for a simplified game. However, it's important to note that this simplification merely postpones the underlying challenges.

By addressing these areas, we can significantly enhance the performance and sophistication of the self-play 20Q agents.
