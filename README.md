# self_play_20Q
This code base implements a system for playing a guessing game between two AI agents, a guesser and a host. The code can be run in asynchronously two modes, easy and hard, which determines the topic pool for the host agent to pick from.
```play.py``` 
The SelfPlay class this file is the core of the system. It can be initialized with the number of games to be played. It has two main functions: play_game and start. The play_game function plays a single game between the guesser and host agent. It takes optional arguments for the topic and the agents to use but can use defaults if none are provided.  The start function plays the specified number of games. It creates a log file and loops for the number of games specified calling play_game each time.
The guesser agent is assumed to be a ReactGuesser and the host agent is assumed to be a MultiAgentHostWithHeuristics but can be overridden during both play_game and start.

```evaluate_self_play.py```
After running play.py, run this to evaluate the play sessions. It will print the results.

```play_test_guesser.py```
Run this to play a game with the guesser agent.

```play_test_host.py```
Run this to play a game with the host agent.

See ```IMPLEMENTATION_NOTES.md``` for more details.
