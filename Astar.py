from queue import PriorityQueue
import pygame
from pathfinder_visualizer import Grid, Node
from time import sleep


class AstarNode:
    def __init__(self, score: int, node: Node, count: int) -> None:
        self.score = score
        self.node = node
        self.count = count

    def __lt__(self, other):
        if self.score < other.score:
            return True
        if self.score == other.score:
            if self.count < other.count:
                return True
        return False


def heuristic(p1: int, p2: int) -> int: # Calculate the distance from current point to end point. Used as the heuristic for algorithm
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from: dict[Node, Node], current: Node, draw: callable) -> None:
    # Go back through the path from the end node and draw it 
    while current in came_from:
        current = came_from[current]
        current.makePath()
        draw()


def algorithm(draw: callable, grid: Grid, start: Node, end: Node) -> None:
    count = 0 # Used as a tie breaker for the __lt__ method in AstarNode
    open_set = PriorityQueue()
    open_set.put(AstarNode(0, start, count)) # Add the staring node
    came_from = {} # Dict for tracking what Node has what parent
    cost_score = {node: float('inf') for row in grid.getGrid() for node in row} # The cost to get to that Node
    cost_score[start] = 0
    heuristic_score = {node: float('inf') for row in grid.getGrid() for node in row} # The score of heuristic and cost
    heuristic_score[start] = heuristic(start.getPos(), end.getPos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get().node # get the Node object at the top of the PQ
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.makeEnd()
            start.makeStart()
            return

        for neighbor in current.neighbors:
            temp_cost_score = cost_score[current] + 1

            if temp_cost_score < cost_score[neighbor]: # See if it's faster to get to the neighbor Node from the current Node than the previus path to that Node
                came_from[neighbor] = current # Set the parent Node of the neighbour to be the current Node
                cost_score[neighbor] = temp_cost_score # Update the cost to get to that Node
                heuristic_score[neighbor] = temp_cost_score + heuristic(neighbor.getPos(), end.getPos()) # Update heuristic score to be the cost score + the heuristic
                if neighbor not in open_set_hash: # If we have not already looked at that Node
                    count += 1
                    open_set.put(AstarNode(heuristic_score[neighbor], neighbor, count)) # Add neighbour to the PQ
                    open_set_hash.add(neighbor) # Add neightbour to the set of open Nodes
                    neighbor.makeOpen()

        draw()

        if current != start:
            current.makeClosed() # Close Node when we are done looking at it