import random
from models import Position, Feature, Direction, Perception
from typing import Dict, Tuple

class WumpusEnvironment:
    def __init__(self, size: int = 4):
        self.size = size
        self.grid: Dict[Tuple[int, int], Feature] = {}
        self.init_grid()

    def init_grid(self):
        positions = [(x, y) for x in range(1, self.size + 1)
                     for y in range(1, self.size + 1) if (x, y) != (1, 1)]
        random.shuffle(positions)
        # Place Wumpus
        x, y = positions.pop()
        self.grid[(x, y)] = Feature.WUMPUS
        # Place Gold
        x, y = positions.pop()
        self.grid[(x, y)] = Feature.GOLD
        # Place 3 Pits
        for _ in range(3):
            x, y = positions.pop()
            self.grid[(x, y)] = Feature.PIT

    def get_perception(self, pos: Position) -> Perception:
        p = Perception()
        x, y = pos.x, pos.y
        adjacent = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for ax, ay in adjacent:
            if (ax, ay) in self.grid:
                if self.grid[(ax, ay)] == Feature.WUMPUS:
                    p.stench = True
                elif self.grid[(ax, ay)] == Feature.PIT:
                    p.breeze = True
        if (x, y) in self.grid and self.grid[(x, y)] == Feature.GOLD:
            p.glitter = True
        return p

    def is_terminal(self, pos: Position) -> bool:
        if (pos.x, pos.y) in self.grid:
            return self.grid[(pos.x, pos.y)] in [Feature.WUMPUS, Feature.PIT]
        return False

    def move(self, x, y, direction):
        # direction: 0=EAST, 1=NORTH, 2=WEST, 3=SOUTH
        dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][direction]
        nx, ny = x + dx, y + dy
        bump = not (1 <= nx <= self.size and 1 <= ny <= self.size)
        if bump:
            nx, ny = x, y
        return nx, ny, bump

    def shoot(self, x, y, direction):
        # direction: 0=EAST, 1=NORTH, 2=WEST, 3=SOUTH
        dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][direction.value if hasattr(direction, 'value') else direction]
        tx, ty = x + dx, y + dy
        while 1 <= tx <= self.size and 1 <= ty <= self.size:
            if (tx, ty) in self.grid and self.grid[(tx, ty)].name == 'WUMPUS':
                # Remove the Wumpus from the grid
                del self.grid[(tx, ty)]
                return True  # Scream
            tx += dx
            ty += dy
        return False
