# import sys
# sys.path.insert(0, "./aima_python")
# print(sys.path)

import copy
import random
import tkinter as tk
from functools import reduce
from operator import or_
import collections
# from aima_python import utils4e
# print('ligma')
# from aima_python import games4e
# import aima_python.games4e as games4e
import games4e
from collections import defaultdict
import homemade_agents
from tqdm.auto import tqdm
import time

bg_color = 'white'
white_color = 'lightblue'
black_color = 'pink'
pen_thickness = 3
node_radius = 15

class Graph:
    def __init__(self, n):
        self.size = n
        self.adj = defaultdict(set)
        self.pos = {}
        self.scale = 1
        self.canvas = None # must set before calling `display()`

    def add_edge(self, u, v):
        assert u in range(self.size)
        assert v in range(self.size)

        self.adj[u].add(v)
        self.adj[v].add(u)

    # save the position data here for easy drawing
    def set_pos(self, u, x, y):
        assert u in range(self.size)
        self.pos[u] = (x, y)

    @staticmethod
    def example_board(edge_length=3):
        g = Graph(edge_length ** 2)

        g.scale = 1
        x_off,y_off = 50,50
        spacing = 50
        for i in range(edge_length ** 2):
            g.set_pos(i, x_off + (i % edge_length)*spacing, y_off + (i // edge_length)*spacing)
            if i % edge_length < edge_length - 1:
                g.add_edge(i, i+1)
            if i // edge_length < edge_length - 1:
                g.add_edge(i, i+edge_length)
        return g

    def scaled_create_oval(scale, canvas, x0, y0, x1, y1, **kwargs):
        x0,y0,x1,y1 = map(lambda a: a*scale, [x0,y0,x1,y1])
        return canvas.create_oval(x0, y0, x1, y1, **kwargs)

    def scaled_create_line(scale, canvas, x0, y0, x1, y1, **kwargs):
        x0,y0,x1,y1 = map(lambda a: a*scale, [x0,y0,x1,y1])
        return canvas.create_line(x0, y0, x1, y1, **kwargs)

    def draw_node(scale, canvas, x, y, color=bg_color):
        Graph.scaled_create_oval(scale, canvas, x-node_radius, y-node_radius, 
                           x+node_radius, y+node_radius, fill=color, width=pen_thickness)

    def draw_edge(scale, canvas, x0, y0, x1, y1, phase=False, cycle=False, full=False):
        if cycle:
            Graph.scaled_create_line(scale, canvas, x0, y0, x1, y1, width=pen_thickness*2)
            xm,ym = (x0+x1)/2,(y0+y1)/2
        else:
            Graph.scaled_create_line(scale, canvas, x0, y0, x1, y1, width=pen_thickness)
            xm,ym = (x0+x1)/2,(y0+y1)/2
        
        if full:
            full_moon_radius = 3
            Graph.scaled_create_oval(scale, canvas,
                xm-full_moon_radius, ym-full_moon_radius,
                xm+full_moon_radius, ym+full_moon_radius,
                fill='white', width=pen_thickness
                )

        if phase:
            phase_moon_radius = 1
            def orthogonal_unit(x, y):
                x_orth,y_orth = -y,x
                mag = (x**2 + y**2) ** 0.5
                return x_orth/mag,y_orth/mag
            x_orth,y_orth = orthogonal_unit(x1-x0, y1-y0)
            for d in (-1, 1):
                x = xm + 5*d*x_orth           
                y = ym + 5*d*y_orth           

                Graph.scaled_create_oval(scale, canvas,
                    x-phase_moon_radius, y-phase_moon_radius,
                    x+phase_moon_radius, y+phase_moon_radius,
                    fill='black', width=pen_thickness
                    )

    def draw_board(self, canvas, state=None):
        node_colors = defaultdict(lambda: bg_color)
        node_values = defaultdict(str)
        
        if state is not None:
            color_mapper = {None: bg_color, 0: white_color, 1: black_color}

            for node,owner in enumerate(state['board']['owners']):
                node_colors[node] = color_mapper[owner]

            for node,value in enumerate(state['board']['cards']):
                if value is None:
                    node_values[node] = None
                else:
                    node_values[node] = str(value)
            # for node,color in state['ownership']:
            #     node_colors[node] = color

        for u,neigh in self.adj.items():
            for v in neigh:
                x_u,y_u = self.pos[u]
                x_v,y_v = self.pos[v]
                val_u = state['board']['cards'][u]
                val_v = state['board']['cards'][v]
                phase = full = cycle = None
                if val_u is not None and val_v is not None:
                    phase = val_u == val_v
                    full = (val_u + 4) % 8 == val_v
                    cycle = abs((val_u - val_v) % 8) == 1
                Graph.draw_edge(self.scale, canvas, 
                                         x_u, y_u, 
                                         x_v, y_v,
                                         phase=phase, 
                                         full=full,
                                         cycle=cycle)

        for u in range(self.size):
            x,y = self.pos[u]
            color = node_colors[u]
            Graph.draw_node(self.scale, canvas, x, y, color)
            canvas.create_text(x*self.scale, y*self.scale, text=node_values[u])

        canvas.update()

    # def display(self):
    #     assert self.canvas is not None
    #     self.draw_board(self.canvas)

class RotHM(games4e.StochasticGame):
    def create_empty_state(board):
        return {'hands': [[random.randint(0, 7) for _ in range(2)] for _ in range(2)],
                'to_move': 0,
                'scores': [0, 0],
                'board': {
                    'cards': [None]*board.size,
                    'owners': [None]*board.size}}


    def example_state():
        return {'hands': [[1, 2], [3, 4]],
                'to_move': 0,
                'scores': [0, 0], 
                'board': {
                    'cards': [None, None, 1, 2, None, None, None, None, None], 
                    'owners': [None, None, 0, 1, None, None, None, None, None, None, None]}}

    def example_state_2():
        return {'hands': [[2, 7, 2], [3, 4]],
        'to_move': 0,
        'scores': [8, 1], 
        'board': {
            'cards': [None, 6, 5, 4, None, 6, 2, 3, None, None, None, 7, 5, None, None, None], 
            'owners': [None, 0, 1, 1, None, 0, 0, 1, None, None, None, 0, None, None, None, None]}}

    # Hopefully faster than `deepcopy`
    # Given more time, would love to do some diff-based m[[state['to_move']]]ethod that avoids the need to make copies, but this is very low effort and affords a great speedup.
    @staticmethod
    def copy_state(state):
        res = {'hands': [x.copy() for x in state['hands']],
               'to_move': state['to_move'],
               'scores': state['scores'].copy(),
               'board': {
                    'cards': state['board']['cards'].copy(),
                    'owners': state['board']['owners'].copy()
               }}
        return res

    def example_move():
        return (16, # position
                1  # card
                )

    def __init__(self, board):
        self.board = board
        # self.size = board.size # for ease
        # self.initial = self.__class__.example_state() # TODO: TMP
        self.initial = self.__class__.create_empty_state(board)
        pass

    def chances(self, state):
        return range(8)

    def probability(self, chance):
        return 1/8

    def outcome(self, state, chance):
        # new_state = copy.deepcopy(state)
        new_state = RotHM.copy_state(state)
        player = state['to_move']
        new_state['hands'][player].append(chance)
        return new_state

    def actions(self, state):
        actions = []
        player = state['to_move']

        for spot,card in enumerate(state['board']['cards']):
            if card is None:
                for c in set(state['hands'][player]):
                    actions.append((spot, c))

        return actions

    def result(self, state, move):
        # assert is_valid_move(state, move)
        u,card = move
        player = state['to_move']
        # scoring_events = []
        score_change = 0

        new_state = RotHM.copy_state(state)
        new_state['board']['cards'][u] = card

        # check for pairwise score increments
        for v in self.board.adj[u]:
            neighbor_card = state['board']['cards'][v]
            if neighbor_card == card:
                # print("Phase pair")
                # scoring_events.append(('phase', card, v))
                score_change += 1
                new_state['board']['owners'][u] = player
                new_state['board']['owners'][v] = player
            if neighbor_card == (card + 4) % 8:
                # print("Full moon pair")
                # scoring_events.append(('full', card, v))
                score_change += 2
                new_state['board']['owners'][u] = player
                new_state['board']['owners'][v] = player

        # lunar cycles           
        # every node must also remember, for every direction, a list of cycle lengths
        # if state['to_move'] == 1: score_change *= -1
        # chains = self.check_chains(new_state, u)
        inc_chains = self.check_chains(new_state, u, direction='increase')
        dec_chains = self.check_chains(new_state, u, direction='decrease')
        # print(f"Chains found: {inc_chains}, {dec_chains}")

        inc_chains = self.__class__.deduplicate_chains(inc_chains)
        dec_chains = self.__class__.deduplicate_chains(dec_chains)

        inc_encodings = [self.__class__.chain_to_bitset(ch) for ch in inc_chains]
        dec_encodings = [self.__class__.chain_to_bitset(ch) for ch in dec_chains]

        # stitch ascending and descending chains
        def stitch_chains(inc_chains, dec_chains):
            stitched_chains = []
            for inc,inc_enc in zip(inc_chains, inc_encodings):
                for dec,dec_enc in zip(dec_chains, dec_encodings):
                    if inc_enc & dec_enc != 1 << u: continue
                    stitched_chains.append(dec[::-1] + inc[1:])
            return stitched_chains

        # pulled this out to see profiling results
        stitched_chains = stitch_chains(inc_chains, dec_chains)
        
        # print(stitched_chains)
        for ch in stitched_chains:
            if len(ch) >= 3:
                # print(f"Lunar cycle of length {len(ch)}")
                score_change += len(ch)
                for v in ch:
                    new_state['board']['owners'][v] = player

        new_state['hands'][player].remove(card)
        # new_state['hands'][player].append(random.randint(0, 7)) # done in `outcome()`
        new_state['scores'][player] += score_change
        new_state['to_move'] = 1 - player

        return new_state

    # find all (non-looping) sequential chains passing through this node
    # note: in the case of a loop, won't get caught forever, but may duplicate some chains
    def check_chains(self, state, u, ignore_accum=[], direction=None):
        if u in ignore_accum: return []
        c = state['board']['cards'][u]
        chains = [[u]]
        for v in self.board.adj[u]:
            if direction is None or direction == 'increase':
                if (c + 1) % 8 == state['board']['cards'][v]:
                    for chain in self.check_chains(state, v, ignore_accum=ignore_accum+[u], direction='increase'):
                        chains.append([u] + chain)
            if direction is None or direction == 'decrease':
                if (c - 1) % 8 == state['board']['cards'][v]:
                    for chain in self.check_chains(state, v, ignore_accum=ignore_accum+[u], direction='decrease'):
                        chains.append([u] + chain)
        return chains

    @classmethod
    def deduplicate_chains(cls, chains):
        # DONE: remove reordering duplicates
        unique_chains = []
        chain_membership_seen = set()
        for ch in chains:
            # chain_membership = tuple(sorted())
            chain_membership = cls.chain_to_bitset(ch) # little bitsets
            if chain_membership in chain_membership_seen: continue
            
            chain_membership_seen.add(chain_membership)
            unique_chains.append(ch)

        chains = unique_chains
        chain_encodings = [cls.chain_to_bitset(ch) for ch in chains]

        # TODO: think again: should this step be done only after the cartesian product?
        # Think hard because this may cause a large slowdown
        # remove subset duplicates
        deduped_chains = []
        # dominated = set() # not necessary, but hopefully gives a small efficiency boost, especially in a game with long chains
        for i,x in enumerate(chain_encodings):
            for j,y in enumerate(chain_encodings):
                if i == j: continue
                # if j in dominated: continue
                if x & ~y == 0: # x \subseteq y
                    # dominated.add(x)
                    break
            else: # x \nsubseteq y \forall y \neq x \in `chains`
                deduped_chains.append(chains[i])

        return deduped_chains

    @classmethod
    def chain_to_bitset(cls, chain):
        # assert max(Counter(chain).values()) <= 1
        # return reduce(or_, (1 << v for v in chain))
        return sum(1 << v for v in chain)


    def utility(self, state, player):
        util = state['scores'][0] - state['scores'][1] + state['board']['owners'].count(0) - state['board']['owners'].count(1) 
        return util if player == 0 else -util

    # def terminal_test(self, state):
    #     return all(x is not None for x in state['board']['cards'])

    def to_move(self, state):
        return state['to_move']

    def display(self, state):
        # print(state)
        assert self.canvas is not None
        self.board.draw_board(self.canvas, state)
        pass

    def compute_utility(self, board, move, player):
        pass

def main():
    window_root = tk.Tk()
    window_root.title('Rise of the Half Moon')
    canvas = tk.Canvas(window_root, width=500, height=500, bg=bg_color)
    canvas.pack()

    edge_length = None
    while edge_length is None:
        try:
            edge_length = int(input("Input a board size (small positive integer, e.g. 3): "))
        except ValueError:
            print("no")
            continue
        if edge_length <= 0:
            print("no")
            edge_length = None
            continue

    g = Graph.example_board(edge_length=edge_length) # holds board connectivity data
    game = RotHM(g)
    game.canvas = canvas
    canvas.delete('all')

    agent_name = None
    agents = {'random': games4e.random_player,
              'greedy': homemade_agents.greedy_player,
              'emm': homemade_agents.expect_min_max_player,
              'mcts': games4e.mcts_player,
              'query': games4e.query_player,
              }
    while agent_name is None:
        print("Select an agent. Options:")
        for name in agents.keys():
            print(f"- {name}")

        agent_requested = input("> ").strip().lower()
        if agent_requested not in agents.keys():
            print("no")
            continue

        agent_name = agent_requested
            

    result = game.play_game(games4e.query_player, 
                            agents[agent_name])

    scores = result['scores'].copy()
    for i,_ in enumerate(scores):
        scores[i] += result['board']['owners'].count(i)
    
    print(f"Final scores (including territory): {scores}")
    input("Press enter to quit. ")

if __name__ == '__main__':
    main()