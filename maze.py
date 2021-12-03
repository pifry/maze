import random
import sys
from pathlib import Path
from scipy.spatial.transform import Rotation as R
import numpy as np
import stl

sys.setrecursionlimit(10000)

class Node:

    class Edge:
        def __init__(self, a, b) -> None:
            self.a = a
            self.b = b
            self.connected = False
            self.visited = False
        
        def another_node(self, node):
            return self.a if self.b is node else self.b 

    N = 0
    S = 1
    E = 2
    W = 3
    U = 4
    D = 5

    PLANES = ['xz', 'xz', 'yz', 'yz', 'xy', 'xy']

    def __init__(self) -> None:
        #self.N, self.S, self.E, self.W = None, None, None, None
        self.edges = [None, None, None, None, None, None]
        self.visited = False
        self.char = " "

    def existing_edges(self):
        return [edge for edge in self.edges if edge]

    def unvisited_edges(self):
        return [edge for edge in self.existing_edges() if not edge.another_node(self).visited]


class TextNode(Node):
    def __repr__(self) -> str:
        ret_str = "|" if not self.edges[Node.W] or not self.edges[Node.W].connected else " "
        ret_str += "\033[4m" if not self.edges[Node.S] or not self.edges[Node.S].connected else ""
        if self.edges[Node.D]:
            ret_str += self.char if not self.edges[Node.D].connected else "O"
        else:
            ret_str += self.char
        ret_str += "\033[0m" if not self.edges[Node.S] or not self.edges[Node.S].connected else ""
        return ret_str


def connect_horizontal(node_a, node_b):
    node_a.edges[Node.E] = Node.Edge(node_a, node_b)
    node_b.edges[Node.W] = node_a.edges[Node.E]

def connect_vertical(node_a, node_b):
    node_a.edges[Node.S] = Node.Edge(node_a, node_b)
    node_b.edges[Node.N] = node_a.edges[Node.S]

def connect_updown(node_a, node_b):
    node_a.edges[Node.D] = Node.Edge(node_a, node_b)
    node_b.edges[Node.U] = node_a.edges[Node.D]


class Maze:
    def __init__(self, x_size, y_size, z_size=1, start=(0,0,0), end=(-1,-1,-1), deadend_char=" ") -> None:
        self.__build_graph__(x_size, y_size, z_size)
        self.start_node = self.graph[start[2]][start[1]][start[0]]
        self.end_node = self.graph[end[2]][end[1]][end[0]]
        self.deadend_char = deadend_char

        self.start_node.char = 's'
        self.end_node.char = 'e'
        self.__build_maze__(self.start_node)

    def __build_graph__(self, x_size, y_size, z_size):
        self.graph = [[[ TextNode() for node in range(x_size) ] for line in range(y_size)] for flore in range(z_size)]

        for z in range(len(self.graph)):
            for y in range(len(self.graph[0])):
                for x in range(len(self.graph[0][0])-1):
                    connect_horizontal(self.graph[z][y][x], self.graph[z][y][x+1])

        for z in range(len(self.graph)):
            for y in range(len(self.graph[0])-1):
                for x in range(len(self.graph[0][0])):
                    connect_vertical(self.graph[z][y][x], self.graph[z][y+1][x])
        
        for z in range(len(self.graph)-1):
            for y in range(len(self.graph[0])):
                for x in range(len(self.graph[0][0])):
                    connect_updown(self.graph[z][y][x], self.graph[z+1][y][x])
    
    def __build_maze__(self, node):
        node.visited = True
        if not node:
            return
        if node == self.end_node:
            return
        
        edges = node.unvisited_edges()
        if not edges:
            node.char = self.deadend_char
        while edges:
            edge = random.choice(edges)
            edge.connected = True
            self.__build_maze__(edge.another_node(node))
            edges = node.unvisited_edges()   
               
        return

    def __repr__(self) -> str:
        ret = ""
        for floor in self.graph:
            for i in range(len(floor[0])):
                ret += " _"
            ret += "\n"
            for line in floor:
                for node in line:
                    ret += str(node)
                ret += "|\n"
        return ret

    TXT_FORMATS = ['svg']
    BIN_FORMATS = ['stl']

    def save(self, filename):
        ext = Path(filename).suffix[1:]
        mode = 'w' if ext in self.TXT_FORMATS else 'wb'
        with open(filename, mode) as file:
            getattr(self, f'save_{ext}')(file)

    def save_svg(self, file):
        x_size = len(self.graph[0][0])
        y_size = len(self.graph[0])
        z_size = len(self.graph)

        file.write(f'<svg viewBox="0 0 {x_size * 10} {y_size * 10}" xmlns="http://www.w3.org/2000/svg" style="background-color:white">\n')
        file.write(f'<line x1="0" y1="0" x2="{x_size * 10}" y2="0" stroke="#40a1fb" />\n')
        file.write(f'<line x1="0" y1="{y_size * 10}" x2="{x_size * 10}" y2="{y_size * 10}" stroke="#40a1fb" />\n')
        file.write(f'<line x1="0" y1="0" x2="0" y2="{y_size * 10}" stroke="#40a1fb" />\n')
        file.write(f'<line x1="{x_size * 10}" y1="0" x2="{x_size * 10}" y2="{y_size * 10}" stroke="#40a1fb" />\n')

        for floor_no, floor in enumerate(self.graph):
            for line_no, line in enumerate(floor):
                for node_no, node in enumerate(line):
                    if node.edges[Node.W] and not node.edges[Node.W].connected:
                        file.write(f'<line x1="{0 + node_no * 10}" y1="{0 + line_no * 10}" x2="{0 + node_no * 10}" y2="{10 + line_no * 10}" stroke="#40a1fb" stroke-linecap="round" />\n')
                    if node.edges[Node.S] and not node.edges[Node.S].connected:
                        file.write(f'<line x1="{0 + node_no * 10}" y1="{10 + line_no * 10}" x2="{10 + node_no * 10}" y2="{10 + line_no * 10}" stroke="#40a1fb" stroke-linecap="round" />\n')

        file.write('</svg>\n')

    def save_stl(self, file):
        solid = stl.Solid(name="Maze")

        node_size = 10
        wall_half_thick = 1
        corridor_half_width = node_size/2 - wall_half_thick

        for floor_no, floor in enumerate(self.graph):
            for line_no, line in enumerate(floor):
                for node_no, node in enumerate(line):
                    for edge_no, edge in enumerate(node.edges):
                        if edge and not edge.connected:
                            plane = Node.PLANES[edge_no]
                            z = -corridor_half_width if edge_no % 2 else corridor_half_width
                            add_rect(solid, 
                                (node_no*node_size,line_no*node_size,floor_no*node_size), 
                                (0,0,z),
                                (corridor_half_width, corridor_half_width, corridor_half_width, corridor_half_width), 
                                plane=plane)

        solid.write_ascii(file)


def add_rect(solid, node_position, local_position, rect, flipped=False, plane='xy'):
    x,y,z = local_position
    wl,wr,hu,hd = rect

    top_left = [x-wl, y-hu, z]
    top_right = [x+wr, y-hu, z]
    bot_left = [x-wl, y+hd, z]
    bot_right = [x+wr, y+hd, z]

    normal = (0,0,-1) if flipped else (0,0,1)

    if plane == 'xy':
        #r = R.identity()
        r = R.from_rotvec(np.pi * np.array([1, 0, 0]))
    elif plane == 'xz':
        r = R.from_rotvec(np.pi/2 * np.array([1, 0, 0]))
        normal = (0,-1,0) if flipped else (0,1,0)
    elif plane == 'yz':
        r = R.from_rotvec(np.pi/2 * np.array([0, 1, 0]))
        normal = (-1,0,0) if flipped else (1,0,0)

    top_left = np.add(node_position, r.apply(top_left))
    top_right = np.add(node_position, r.apply(top_right))
    bot_left = np.add(node_position, r.apply(bot_left))
    bot_right = np.add(node_position, r.apply(bot_right))
    normal = r.apply(normal)

    solid.add_facet(normal, [bot_left,bot_right,top_right])
    solid.add_facet(normal, [bot_left,top_right,top_left])


maze = Maze(15,15,1)
print(maze)
maze.save('maze.svg')


