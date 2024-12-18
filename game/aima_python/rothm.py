# import sys
# sys.path.insert(0, "./aima_python")
# print(sys.path)

import copy
import random
import tkinter as tk
# from aima_python import utils4e
# print('ligma')
# from aima_python import games4e
# import aima_python.games4e as games4e
import games4e
from collections import defaultdict

bg_color = 'white'
white_color = 'lightblue'
black_color = 'pink'
pen_thickness = 3
node_radius = 20

class Graph:
    def __init__(self, n):
        self.size = n
        self.adj = defaultdict(set)
        self.pos = {}
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
    def example_board():
        g = Graph(9)

        scale = 2
        x_off,y_off = 50*scale,50*scale
        spacing = 50*scale
        for i in range(9):
            g.set_pos(i, x_off + (i % 3)*spacing, y_off + (i // 3)*spacing)
            if i % 3 < 2:
                g.add_edge(i, i+1)
            if i // 3 < 2:
                g.add_edge(i, i+3)
        return g

    def draw_node(canvas, x, y, color=bg_color):
        canvas.create_oval(x-node_radius, y-node_radius, 
                           x+node_radius, y+node_radius, fill=color, width=pen_thickness)

    def draw_edge(canvas, x0, y0, x1, y1):
        canvas.create_line(x0, y0, x1, y1, width=pen_thickness)

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
                Graph.draw_edge(canvas, 
                                         x_u, y_u, 
                                         x_v, y_v)

        for u in range(self.size):
            x,y = self.pos[u]
            color = node_colors[u]
            Graph.draw_node(canvas, x, y, color)
            canvas.create_text(x, y, text=node_values[u])

    # def display(self):
    #     assert self.canvas is not None
    #     self.draw_board(self.canvas)

class DeterministicRotHM(games4e.Game):
    def example_state():
        return {'hands': [[1, 2, 3], [3, 4, 5]],
                'to_move': 0,
                'scores': [0, 0], 
                'board': {
                    'cards': [None, None, 1, 2, None, None, None, None, None], 
                    'owners': [None, None, 0, 1, None, None, None, None, None, None, None]}}

    def example_move():
        return (16, # position
                1  # card
                )

    def __init__(self, board):
        self.board = board
        self.size = board.size # for ease
        self.initial = self.__class__.example_state() # TODO: TMP
        pass

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
        scoring_events = []
        score_change = 0

        new_state = copy.deepcopy(state)
        new_state['board']['cards'][u] = card

        # check for pairwise score increments
        for v in self.board.adj[u]:
            neighbor_card = state['board']['cards'][v]
            if neighbor_card == card:
                print("Phase pair")
                scoring_events.append(('phase', card, v))
                score_change += 1
                new_state['board']['owners'][u] = player
                new_state['board']['owners'][v] = player
            if neighbor_card == (card + 4) % 8:
                print("Full moon pair")
                scoring_events.append(('full', card, v))
                score_change += 2
                new_state['board']['owners'][u] = player
                new_state['board']['owners'][v] = player

        # lunar cycles           
        # every node must also remember, for every direction, a list of cycle lengths
        # if state['to_move'] == 1: score_change *= -1
        # chains = self.check_chains(new_state, u)
        inc_chains = self.check_chains(new_state, u, direction='increase')
        dec_chains = self.check_chains(new_state, u, direction='decrease')
        print(f"Chains found: {inc_chains}, {dec_chains}")
        # TODO: deduplicate chains
        # # bulletproof but icky method
        # chains_deduped = {tuple(sorted(ch, key=new_state['board']['cards'].__getitem__)) for ch in chains if len(ch) >= 3}
        # print(chains_deduped)
        
        # # DONE: remove reordering duplicates
        # deduped_chains = []
        # chain_membership_seen = set()
        # for ch in chains:
        #     # chain_membership = tuple(sorted())
        #     chain_membership = sum(1 << v for v in ch) # little bitsets
        #     if chain_membership in chain_membership_seen: continue
            
        #     chain_membership_seen.add(chain_membership)
        #     deduped_chains.append(ch)

        # chains,deduped_chains = deduped_chains,[]
        # chain_encodings = [sum(1 << v for v in ch) for ch in chains]

        # for i in range(len(chain_encodings)):
        #     x = chain_encodings[i]
        #     for j in range(len(chain_encodings)):
        #         y = chain_encodings[j]
        #         if x == j: continue
        #         if x & ~j == 0: # x \subseteq j
        #             break
        #     else: # x \nsubseteq y \forall y \neq x \in `chains`
        #         deduped_chains.append(chains[i])

        # # TODO: remove prefix/suffix duplicates
        # # TODO: remove any chains that are subsets of other chains
        # # for ch1 in deduped_chains:
        # #     enc1 = sum(1 << v for v in ch1)
        # #     for ch2 in deduped_chains:
        # #         enc2 = sum(1 << v for v in ch2)
        # #         if enc2

        inc_chains = self.__class__.deduplicate_chains(inc_chains)
        dec_chains = self.__class__.deduplicate_chains(dec_chains)

        inc_encodings = [self.__class__.chain_to_bitset(ch) for ch in inc_chains]
        dec_encodings = [self.__class__.chain_to_bitset(ch) for ch in dec_chains]

        # TODO: stitch ascending and descending chains
        stitched_chains = []
        for inc,inc_enc in zip(inc_chains, inc_encodings):
            for dec,dec_enc in zip(dec_chains, dec_encodings):
                if inc_enc & dec_enc != 1 << u: continue
                stitched_chains.append(dec[::-1] + inc[1:])
        
        print(stitched_chains)
        for ch in stitched_chains:
            if len(ch) >= 3:
                print(f"Lunar cycle of length {len(ch)}")
                score_change += len(ch)
                for v in ch:
                    new_state['board']['owners'][v] = player

        new_state['hands'][player].remove(card)
        new_state['hands'][player].append(random.randint(0, 7))
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

        deduped_chains = []
        for i,x in enumerate(chain_encodings):
            for j,y in enumerate(chain_encodings):
                if i == j: continue
                if x & ~y == 0: # x \subseteq y
                    break
            else: # x \nsubseteq y \forall y \neq x \in `chains`
                deduped_chains.append(chains[i])

        return deduped_chains

    @classmethod
    def chain_to_bitset(cls, chain):
        # assert max(Counter(chain).values()) <= 1
        return sum(1 << v for v in chain)


    def utility(self, state, player):
        if player == 0:
            return state['scores'][0] - state['scores'][1]
        else:
            return state['scores'][1] - state['scores'][0]

    # def terminal_test(self, state):
    #     return all(x is not None for x in state['board']['cards'])

    def to_move(self, state):
        return state['to_move']

    def display(self, state):
        print(state)
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

    g = Graph.example_board() # holds board connectivity data
    # g.canvas = canvas
    # g.draw_board(canvas)
    # input()
    # g.draw_board(canvas, DeterministicRotHM.example_state())
    # g.display()

    game = DeterministicRotHM(g)
    game.canvas = canvas
    game.play_game(games4e.query_player, games4e.random_player)
    # game.play_game(games4e.query_player, games4e.query_player)

if __name__ == '__main__':
    main()