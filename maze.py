import random
import sys

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


    def __init__(self) -> None:
        self.N, self.S, self.E, self.W = None, None, None, None
        self.visited = False
        self.char = " "

    def edges(self):
        return [edge for edge in [self.N, self.S, self.E, self.W] if edge]

    def unvisited_edges(self):
        return [edge for edge in self.edges() if not edge.another_node(self).visited]


class TextNode(Node):
    def __repr__(self) -> str:
        ret_str = "|" if not self.W or not self.W.connected else " "
        ret_str += "\033[4m" if not self.S or not self.S.connected else ""
        ret_str += self.char
        ret_str += "\033[0m" if not self.S or not self.S.connected else ""
        return ret_str


def connect_horizontal(node_a, node_b):
    node_a.E = Node.Edge(node_a, node_b)
    node_b.W = node_a.E

def connect_vertical(node_a, node_b):
    node_a.S = Node.Edge(node_a, node_b)
    node_b.N = node_a.S


class Maze:
    def __init__(self, x_size, y_size, start=(0,0), end=(-1,-1), deadend_char=" ") -> None:
        self.__build_graph__(x_size, y_size)
        self.start_node = self.graph[start[1]][start[0]]
        self.end_node = self.graph[end[1]][end[0]]
        self.deadend_char = deadend_char

        self.start_node.char = 's'
        self.end_node.char = 'e'
        self.__build_maze__(self.start_node)

    def __build_graph__(self, x_size, y_size):
        self.graph = [[ TextNode() for node in range(x_size) ] for line in range(y_size)]

        for y in range(len(self.graph)):
            for x in range(len(self.graph[0])-1):
                connect_horizontal(self.graph[y][x], self.graph[y][x+1])

        for y in range(len(self.graph)-1):
            for x in range(len(self.graph[0])):
                connect_vertical(self.graph[y][x], self.graph[y+1][x])
    
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
        for i in range(len(self.graph[0])):
            ret += " _"
        ret += "\n"
        for line in self.graph:
            for node in line:
                ret += str(node)
            ret += "|\n"
        return ret


maze = Maze(30, 30)
print(maze)
