import tkinter as tk

root = tk.Tk()
root.title('vis test')
canvas = tk.Canvas(root, width=500, height=500, bg='gray')
canvas.pack()

bg_color = 'gray'
white_color = 'white'
black_color = 'black'
pen_thickness = 3
node_radius = 20

def draw_node(x, y):
    canvas.create_oval(x-node_radius, x-node_radius, x+node_radius, x+node_radius, fill=bg_color, width=pen_thickness)

def draw_edge(x0, y0, x1, y1):
    canvas.create_line(x0, y0, x1, y1, width=pen_thickness)

draw_edge(100, 100, 200, 200)
draw_node(100, 100)
draw_node(105, 100)
