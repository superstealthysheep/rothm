### Rise of the Half Moon
This is an impelementation of the [Rise of the Half Moon](https://doodles.google/doodle/rise-of-the-half-moon/) Google doodle game. There're also some AI agents to play the game if that's your speed.

### tl;dr how to play?
1. Clone repo
2. `python -m venv ./.venv`
3. `./.venv/Scripts/activate`
    1. On Windows you might need to also do something like `Set-ExecutionPolicy Unrestricted -Scope Process` to be able to activate the virtual environment
3. `pip install -r requirements.txt`
4. `python game/aima_python/rothm.py`

### Dependencies:
- See `requirements.txt`

### What to run?/how?
- The main file is `game/aima_python/rothm.py`. If `rothm.py` is run as a script, the result is an interactive game where you play Player 0, and you choose an agent to be Player 1.
- Selected fun experiments are in `game/aima_python/experiments.py`. Currently it's set to run `free_for_all()` which is a pairwise comparison of four agents (random, greedy, expectiminimax, mcts) on a 3x3 board. 

Alternatively, write another file, import in the `RotHM` class, and use your favorite `aima-python` functions and agents on it!