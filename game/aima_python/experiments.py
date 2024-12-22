import tkinter as tk
import rothm
from rothm import Graph, RotHM
import homemade_agents
import games4e
from tqdm.auto import tqdm
import collections

bg_color = 'white'
white_color = 'lightblue'
black_color = 'pink'
pen_thickness = 3
node_radius = 15

def asymmetry_experiment():
    window_root = tk.Tk()
    window_root.title('Rise of the Half Moon')
    canvas = tk.Canvas(window_root, width=500, height=500, bg=bg_color)
    canvas.pack()

    for edge_len in range(1,7):
        all_scores = []
        for game_num in tqdm(range(100000)):
            g = Graph.example_board(edge_length=edge_len) # holds board connectivity data
            g.scale = 2
            game = RotHM(g)
            game.canvas = canvas
            canvas.delete('all')

            result = game.play_game(games4e.random_player, games4e.random_player)

            scores = result['scores'].copy()
            for i,_ in enumerate(scores):
                scores[i] += result['board']['owners'].count(i)

            all_scores.append(scores)

        winners = collections.Counter()
        for x,y in all_scores:
            if x > y: winners[0] += 1
            if x < y: winners[1] += 1
            if x == y: winners['tie'] += 1

        print(f"${edge_len} \\times {edge_len}$ & {winners[0]} & {winners[1]} & {winners['tie']} \\\\")

def mcts_vs_expectiminimax():
    window_root = tk.Tk()
    window_root.title('Rise of the Half Moon')
    canvas = tk.Canvas(window_root, width=500, height=500, bg=bg_color)
    canvas.pack()

    # players = {'mcts': games4e.mcts_player, 'emm': homemade_agents.expect_min_max_player}
    players = {'mcts': games4e.mcts_player, 'emm': homemade_agents.greedy_player}


    for edge_len in range(5,6):
        winners = {'mcts': 0, 'emm': 0, 'tie': 0}
        for i in range(2):
            if i == 0: p = ['emm', 'mcts']
            else: p = ['mcts', 'emm']

            for game_num in tqdm(range(10)):
                g = Graph.example_board(edge_length=edge_len) # holds board connectivity data
                g.scale = 2
                game = RotHM(g)
                game.canvas = canvas
                canvas.delete('all')

                result = game.play_game(players[p[0]], players[p[1]])

                scores = result['scores'].copy()
                for i,_ in enumerate(scores):
                    scores[i] += result['board']['owners'].count(i)

                if scores[0] == scores[1]:
                    winners['tie'] += 1
                elif scores[0] > scores[1]:
                    winners[p[0]] += 1
                elif scores[0] < scores[1]:
                    winners[p[1]] += 1

        print(f"${edge_len} \\times {edge_len}$ & {winners['emm']} & {winners['mcts']} & {winners['tie']} \\\\")

# Test all pairs of agents against each other
def free_for_all():
    window_root = tk.Tk()
    window_root.title('Rise of the Half Moon')
    canvas = tk.Canvas(window_root, width=500, height=500, bg=bg_color)
    canvas.pack()

    edge_len = 3
    players = {'random': games4e.random_player,
               'greedy': homemade_agents.greedy_player,
               'mcts': games4e.mcts_player,
               'emm': homemade_agents.expect_min_max_player}
    player_names = list(players.keys())
    results = [[None]*4 for _ in range(4)] # scuffed but quick

    for p0 in range(len(players)):
        for p1 in range(p0):
            p_names = [player_names[p0], player_names[p1]] # strings representing who's up
            winners = {p_names[0]: 0, p_names[1]: 0, 'tie': 0}

            for i in range(2):
                if i == 0: p = p_names
                else: p = list(reversed(p_names))

                for _ in tqdm(range(100)):
                    g = Graph.example_board(edge_length=edge_len) # holds board connectivity data
                    g.scale = 2
                    game = RotHM(g)
                    game.canvas = canvas
                    canvas.delete('all')

                    result = game.play_game(players[p[0]], players[p[1]])

                    scores = result['scores'].copy()
                    for i,_ in enumerate(scores):
                        scores[i] += result['board']['owners'].count(i)

                    if scores[0] == scores[1]:
                        winners['tie'] += 1
                    elif scores[0] > scores[1]:
                        winners[p[0]] += 1
                    elif scores[0] < scores[1]:
                        winners[p[1]] += 1
                        
            print(winners)
            results[p0][p1] = winners
            # print(f"${edge_len} \\times {edge_len}$ & {winners['emm']} & {winners['mcts']} & {winners['tie']} \\\\")
    print(results)

if __name__ == '__main__':
    print("Running experiment: 'free_for_all'")
    free_for_all()