from __future__ import annotations
import pygame
# import Astar
import Dijkstra

# Set up pygame
WIN_WIDTH = 800
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_WIDTH))
pygame.display.set_caption('Path finding visualization')

# Create global dict for rgb color values to use throughout the program
COLORS = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 255, 0),
    "YELLOW": (255, 255, 0),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 165 ,0),
    "GREY": (128, 128, 128),
    "TURQUOISE": (64, 224, 208)
}


class Node:
    def __init__(self, row: int, col: int, width: int, total_rows: int) -> None:
        self.row = row
        self.col = col
        self.width = width
        self.color = COLORS["WHITE"]
        self.type = None
        self.total_rows = total_rows

    def getPos(self) -> tuple[int, int]:
        return self.row, self.col

    def isClosed(self) -> bool:
        return self.type == "closed"

    def isOpen(self) -> bool:
        return self.type == "open"

    def isBarrier(self) -> bool:
        return self.type == "barrier"

    def isStart(self) -> bool:
        return self.type == "start"

    def isEnd(self) -> bool:
        return self.type == "end"

    def reset(self) -> None:
        self.color = COLORS["WHITE"]
        self.type = None

    def makeClosed(self) -> None:
        self.color = COLORS["RED"]
        self.type = "closed"

    def makeOpen(self) -> None:
        self.color = COLORS["GREEN"]
        self.type = "open"

    def makeBarrier(self) -> None:
        self.color = COLORS["BLACK"]
        self.type = "barrier"

    def makeStart(self) -> None:
        self.color = COLORS["ORANGE"]
        self.type = "start"

    def makeEnd(self) -> None:
        self.color = COLORS["TURQUOISE"]
        self.type = "end"

    def makePath(self) -> None:
        self.color = COLORS["PURPLE"]
        self.type = "path"

    def draw(self, surface: pygame.Surface) -> None:
        x = self.col * self.width
        y = self.row * self.width
        pygame.draw.rect(surface, self.color, (x, y, self.width, self.width))

    def update_neighbors(self, grid: list[list[Node]], total_rows: int) -> None:
        """
        Add nodes to a list if they are neighbouring and not barriers.
        Used to see what nodes can be checked from that current node (the edges)
        """
        self.neighbors = []
        if self.row < total_rows - 1 and not grid[self.row+1][self.col].isBarrier():  # down
            self.neighbors.append(grid[self.row+1][self.col])
        if self.row > 0 and not grid[self.row-1][self.col].isBarrier():  # up
            self.neighbors.append(grid[self.row-1][self.col])
        if self.col < total_rows - 1 and not grid[self.row][self.col+1].isBarrier():  # right
            self.neighbors.append(grid[self.row][self.col+1])
        if self.col > 0 and not grid[self.row][self.col-1].isBarrier():  # left
            self.neighbors.append(grid[self.row][self.col-1])


class Grid:
    def __init__(self, rows: int, width: int) -> None:
        self.rows = rows
        self.width = width
        self.cell_size = width // rows
        self.makeGrid()
    
    def makeGrid(self) -> None:
        self.grid = [[Node(i, j, self.cell_size, self.rows) for j in range(self.rows)] for i in range(self.rows)]

    def draw(self, surface: pygame.Surface) -> None:
        for i in range(self.rows):
            pygame.draw.line(surface, COLORS["GREY"], (0, i * self.cell_size), (self.width, i * self.cell_size))
            pygame.draw.line(surface, COLORS["GREY"], (i * self.cell_size, 0), (i * self.cell_size, self.width))

    def getGrid(self) -> list[list[Node]]:
        return self.grid


def draw(surface: pygame.Surface, grid: Grid) -> None:
    surface.fill(COLORS["WHITE"])

    for row in grid.getGrid():
        for node in row:
            node.draw(surface)

    grid.draw(surface)

    pygame.display.update()

def getClickedPos(pos: tuple[int, int], rows: int, width: int) -> tuple[int, int]:
    cell_size = width // rows
    x, y = pos

    row = y // cell_size
    col = x // cell_size

    return row, col

def run(algorithm: callable[callable, Grid, Node, Node]) -> None:
    ROWS = 50
    grid = Grid(ROWS, WIN_WIDTH)
    width = WIN_WIDTH
    surface = WIN
    
    start = None
    end = None

    pygame.init()
    run = True
    clock = pygame.time.Clock()
    
    while run:
        clock.tick(60)
        draw(surface, grid)
        for event in pygame.event.get():
            # Check if window is closed
            if event.type == pygame.QUIT:
                run = False

            # Take care of drawing
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                node = grid.getGrid()[row][col]
                if not start:
                    start = node
                    start.makeStart()
                elif not end and node != start:
                    end = node
                    end.makeEnd()
                elif node != start and node != end:
                    node.makeBarrier()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                node = grid.getGrid()[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None
            
            # Run pathfinding algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid.getGrid():
                        for node in row:
                            node.update_neighbors(grid.getGrid(), ROWS)

                    algorithm(lambda: draw(surface, grid), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = Grid(ROWS, width)
    pygame.quit()


if __name__ == "__main__":
    run(Dijkstra.algorithm)