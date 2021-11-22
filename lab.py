import random
import sys

sys.setrecursionlimit(1500)

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


    def __repr__(self) -> str:
        return ("|" if not self.W or not self.W.connected else " ") + ("_" if not self.S or not self.S.connected else " ")


def connect_horizontal(node_a, node_b):
    node_a.E = Node.Edge(node_a, node_b)
    node_b.W = node_a.E

def connect_vertical(node_a, node_b):
    node_a.S = Node.Edge(node_a, node_b)
    node_b.N = node_a.S

lab_dimension = 40

l = [[ Node() for node in range(lab_dimension) ] for line in range(lab_dimension)]

for y in range(len(l)):
    for x in range(len(l[0])-1):
        connect_horizontal(l[y][x], l[y][x+1])

for y in range(len(l)-1):
    for x in range(len(l[0])):
        connect_vertical(l[y][x], l[y+1][x])

def print_lab(lab):
    for i in range(len(lab[0])):
        print(" _", end="")
    print("")
    for line in lab:
        for node in line:
            print(node, end="")
        print("|")

start_node = l[0][0]
end_node = l[-1][-1]

print(end_node == l[-1][-1])

def traverse(node):
    global l
    node.visited = True
    if not node:
        return False
    if node == end_node:
        return True
    edges = [edge for edge in [node.N, node.S, node.W, node.E] if edge and not edge.another_node(node).visited]
    random.shuffle(edges)
    for edge in edges:
        if traverse(edge.another_node(node)):
            edge.connected = True
            return True
        else:
            edge.connected = True if random.randrange(10) < 7 else False
    return False

def visited_percent(lab):
    visited = 0
    for line in lab:
        for node in line:
            if node.visited:
                visited += 1
    return visited / (len(lab) * len(lab[0])) * 100

def next_unvisited(lab):
    for line in lab:
        for node in line:
            if not node.visited:
                return node

traverse(start_node)
while visited_percent(l) < 99:
    traverse(next_unvisited(l))

print_lab(l)
print(visited_percent(l))