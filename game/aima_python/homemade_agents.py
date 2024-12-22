import numpy as np

def expect_minmax(state, game, max_depth=np.inf):
    """
    [Figure 5.11]
    Return the best move for a player after dice are thrown. The game tree
	includes chance nodes along with min and max nodes.
	"""
    player = game.to_move(state)

    def max_value(state, max_depth=np.inf):
        if max_depth <= 0:
            return game.utility(state, player)

        v = -np.inf
        for a in game.actions(state):
            v = max(v, chance_node(state, a, max_depth-1))
        return v

    def min_value(state, max_depth=np.inf):
        if max_depth <= 0:
            return game.utility(state, player)

        v = np.inf
        for a in game.actions(state):
            v = min(v, chance_node(state, a, max_depth-1))
        return v

    def chance_node(state, action, max_depth=np.inf):
        res_state = game.result(state, action)
        if game.terminal_test(res_state):
            return game.utility(res_state, player)
        if max_depth <= 0:
            return game.utility(res_state, player)
        sum_chances = 0
        num_chances = len(game.chances(res_state))
        for chance in game.chances(res_state):
            res_state = game.outcome(res_state, chance)
            util = 0
            # if res_state.to_move == player:
            if res_state['to_move'] == player:
                util = max_value(res_state, max_depth-1)
            else:
                util = min_value(res_state, max_depth-1)
            sum_chances += util * game.probability(chance)
        return sum_chances / num_chances

    # Body of expect_min_max:
    return max(game.actions(state), key=lambda a: chance_node(state, a, max_depth=max_depth), default=None)

def expect_min_max_player(game, state):
    return expect_minmax(state, game, max_depth=3)