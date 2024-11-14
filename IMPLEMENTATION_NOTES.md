# **Section 1: The Nature of the 20Q Task Environment**

In this section, we describe the nature of the 20Q task using the taxonomy outlined by Stuart Russell and Peter Norvig in *Artificial Intelligence: A Modern Approach*.

The 20Q environment is characterized as follows:
* **Multi-agent:** The game involves two distinct roles—the ***host*** and the ***guesser***—each acting independently. Both roles have hidden states that must be communicated to be known by the other.
* **Partially observable:** Neither agent can directly access the other's thoughts or internal state.
* **Competitive (or Semi-cooperative):** 20Q can be played competitively, with each agent striving to outperform the other. In this mode, the host aims to choose a topic the guesser can't identify (within the game's constraints), while the guesser attempts to deduce the topic in as few turns as possible.Alternatively, the game can be semi-cooperative. For instance, a doting father as host might craft a challenge that's engaging yet winnable for his young son as the guesser.
* **Deterministic:** Disregarding the inherent uncertainty from partial observability and multi-agent interactions, 20Q can be considered deterministic. As Russell and Norvig state, if the game's next state is solely determined by its current state and the agents' actions, the environment is deterministic. (One could argue for a stochastic view by considering the ignored elements.)
* **Sequential:** Strategic play involves each guess influencing subsequent ones. Poor play might treat the game episodically, leading to randomness.
* **Static:** The game state remains unchanged while agents are deliberating.
* **Discrete:**
    * **Time:** The game consists of exactly 20 turns, not necessarily in real-time.
    * **Outcomes:** Possible results are win, lose (at turn 20), or continue.
    * **Actions:** The host's actions are limited to yes, no, you win, you lose. The guesser's actions, while more varied, remain discrete—each guess is a single unit within a vast but finite set of possibilities.
* **Known:** Despite being partially observable and extensive, the environment is known due to clearly stated rules.


# **Section 2: Project Scope**

Due to time constraints, we've limited the project scope as follows:

1. **Question Limit:** Only 20 yes/no questions are permitted. Non-yes/no questions don't count towards this limit.
2. **Question Format:** Only yes/no questions are allowed. All other question types prompt a redirect.
3. **Answer Format:** Responses are strictly limited to "yes", "no", "yes, you win!", "no, you lose" or "please ask a yes/no question". No additional context or explanations are provided.
4. **Agent Turn:** Each agent participates in only one turn of the game.
5. **Topic Scope:** The game focuses exclusively on common noun topics.


# **Section 3: The Agents**

The 20Q game features two key agents: the host and the guesser. We'll now explore their implementations and preliminary evaluations.


### **The Host**

The host has three main responsibilities:

1. **Topic Selection:** Choosing the subject for the guesser to identify.
2. **Guess Evaluation:** Assessing the accuracy of each guess and providing feedback.
3. **Turn Tracking:** Monitoring the number of guesses to ensure adherence to the 20-question limit.

We evaluated the host's performance based on these criteria:

* **Topic Variety:** The diversity of subjects presented.
* **Guess Evaluation Accuracy:** The precision of the host's judgments on guess correctness.
* **Turn Tracking:** Adherence to the 20-question limit and avoidance of premature game termination.

Note: We did not assess **topic difficulty** in this exploration.

To evaluate these criteria, we conducted both manual and automated assessments, starting with manual evaluations followed by automated evaluations in self-play sessions.


### **Simple Reflex Host With Memory**

Given the host's reactive role, we implemented a Simple Reflex Agent with Memory. This language model-based agent uses simple if-then rules and stores interaction history to inform future responses.

A manual evaluation of six game sessions yielded these results:

* **Guess Evaluation Accuracy:** 99.2% (One incorrect evaluation out of 120 questions)
* **Turn Tracking:** 0% accuracy (Consistently exceeded the 20-question limit)

While the agent excelled at evaluating guesses, it failed to adhere to the turn limit. This simple reflex host with memory can be considered a simplified **model-based reflex agent**, as it uses conversation history to infer guess count and determine end-game conditions.


### **Multi-Agent Host**

To address the Simple Reflex Host's limitations, we developed a Multi-Agent Host. Initially, this approach incorporated a **topic suggester** and a **state tracker**—both simple reflex agents without memory—working alongside the answerer. However, given our simplified game scope, we adopted a more practical approach:
* **Topic Suggester:** Replaced with a simple function selecting topics from a[ curated corpus](https://www.kaggle.com/code/waechter/llm-20-questions-games-dataset/output?select=keywords.csv).
* **State Tracking:** Replaced with a function estimating guess number by counting "yes" and "no" host responses. This relies on the answerer's ability to respond only with "yes" or "no" as instructed.

This streamlined approach effectively addresses topic variety and turn tracking issues. The Multi-Agent Host, enhanced with heuristics, achieved 100% accuracy in turn tracking. In 30 game sessions, it didn't repeat topics, as the probability of selecting each word in the keyword corpus is about 0.06%.

All **automatic evaluation results** after self-play used this agent. See `data/evaluation_results.csv` for details.


## **The Guesser**
The guesser's primary goal is to correctly identify the hidden topic using as few questions as possible. This requires employing effective questioning strategies to efficiently narrow down the search space.

We evaluated the guesser's performance using these metrics:


1. **Win Rate:** The percentage of games won.
2. **Question Efficiency:** A measure of the guesser's effectiveness. An efficient guesser should maximize "yes" responses while minimizing unnecessary questions. This metric calculates the ratio of "yes" to "no" responses received.
3. **Average Turns:** The mean number of turns used per game.

The following sections detail the implementation and evaluation of various guesser agent iterations.


### **Goal-Based Host with Simple Prompting**
Unlike the host agent, the guesser's task is inherently more challenging. We can't pre-specify questions due to the unknown topic. Instead, the agent must generate questions autonomously based on a simple goal: accurately guessing the topic.

Automatic evaluation showed a 70% win rate for easy topics, but the agent struggled with tougher ones, achieving only 50% accuracy. Note that these results are based on a limited sample size of 10 games per difficulty level. Additionally, the agent's question efficiency was around 40%, indicating room for improvement in its ability to efficiently explore the search space. See `data/evaluation_results.txt` for more details.


### **Goal-Based Host with Explicit Reasoning**
An initial attempt to incorporate a reasoning component into the agent proved unsuccessful. The resulting agent showed a preference for depth-first search strategies, which is suboptimal given the vast search space. For example, after correctly identifying that "ballet shoes" could be found indoors, the agent wasted 7 guesses trying to pinpoint the specific room.

While these results suggest that reasoning could be valuable, further research is needed to develop a more effective reasoning component for the agent.


# **Section 4: Improvements**
This document and the accompanying codebase present an initial exploration of the self-play 20Q task. While promising, the current agents have room for improvement in several areas:

**Agent Enhancements:**
* **Host Agent:**
    * Improve prompting for the multi-host agent with heuristics—include guardrails to prevent LLM misuse and jailbreaking.
    * Incorporate a reasoning component, such as a ReAct framework or chain-of-thought prompting, to enhance guess evaluation accuracy.
    * (Alternatively, include a classifier to categorize each question as True or False)
* **Guesser Agent:**
    * Refine prompting for current approaches.
    * Enhance reasoning capabilities to minimize redundant questions and avoid "tunnel vision."
    * Consider including a component that uses heuristics and a dictionary to make educated guesses after discerning the category.
    * Train the agent using Reinforcement Learning to optimize question selection.

**Experimental Setup:**
* **Better Error Handling:** E.g., Stopping a run if LLM calls fail.
* **Parallelism:** Identify and resolve blocking code in asynchronous execution of agent pairs to accelerate large-scale evaluation.
* **Codebase:** Reorganize and refactor the code to improve readability and maintainability.
* **Better Documentation:** Enhance accessibility for users and contributors.

**Game Variations:**
* **"Sometimes" Answer:** Introduce a third answer category to facilitate more nuanced reasoning.
* **Categorized Topics:** Limit topic exploration to specific categories for a simplified game. However, it's important to note that this simplification merely postpones the underlying challenges.

By addressing these areas, we can significantly enhance the performance and sophistication of the self-play 20Q agents.
