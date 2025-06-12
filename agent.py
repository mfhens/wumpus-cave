from models import Position, Direction, GameState, Perception
from environment import WumpusEnvironment
import random
import heapq

class EnhancedAgent:
    def __init__(self, risk_prob=0.25, risk_threshold=5):
        self.risk_prob = risk_prob
        self.risk_threshold = risk_threshold
        self.reset()

    def reset(self):
        self.x, self.y = 1, 1
        self.dir = Direction.EAST
        self.has_gold = False
        self.arrow = True
        self.performance = 0
        self.safe = {(1, 1)}
        self.visited = set()
        self.unknown = {(x, y) for x in range(1, 5) for y in range(1, 5)} - {(1, 1)}
        self.unsafe = set()
        self.wumpus_inferred = False
        self.wumpus_location = None
        self.risky_target = None

    def neighbors(self, x, y):
        for d, (dx, dy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
            nx, ny = x + dx, y + dy
            if 1 <= nx <= 4 and 1 <= ny <= 4:
                yield nx, ny, d

    def a_star(self, start, goal, allow_unknown=False):
        def manhattan(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        frontier = [(0 + manhattan(start, goal), 0, start, [])]
        visited = {start: 0}
        while frontier:
            _, g, current, path = heapq.heappop(frontier)
            if current == goal:
                return path
            for nx, ny, _ in self.neighbors(*current):
                if (nx, ny) in self.unsafe:
                    continue
                if allow_unknown or (nx, ny) in self.safe:
                    ng = g + 1
                    if (nx, ny) not in visited or ng < visited[(nx, ny)]:
                        visited[(nx, ny)] = ng
                        heapq.heappush(frontier, (ng + manhattan((nx, ny), goal), ng, (nx, ny), path + [(nx, ny)]))
        return None

    def choose_action(self, perception: Perception, bump=False, scream=False) -> str:
        self.visited.add((self.x, self.y))
        self.unknown.discard((self.x, self.y))
        stench, breeze, glitter = perception.stench, perception.breeze, perception.glitter

        if breeze:
            potentials = [(nx, ny) for nx, ny, _ in self.neighbors(self.x, self.y) if (nx, ny) in self.unknown]
            if len(potentials) == 1:
                self.unsafe.add(potentials[0])
                self.unknown.discard(potentials[0])

        if stench and self.arrow and not self.wumpus_inferred:
            potentials = [(nx, ny, d) for nx, ny, d in self.neighbors(self.x, self.y) if (nx, ny) in self.unknown]
            if len(potentials) == 1:
                self.wumpus_inferred = True
                self.wumpus_location = potentials[0]
        if self.wumpus_inferred and self.arrow and self.wumpus_location is not None:
            wx, wy, wd = self.wumpus_location
            # Move to the cell facing the Wumpus and shoot
            if (self.x, self.y) == (wx, wy):
                return "SHOOT"
            # Move towards the inferred Wumpus location
            if wx > self.x:
                return "MOVE_EAST"
            elif wx < self.x:
                return "MOVE_WEST"
            elif wy > self.y:
                return "MOVE_NORTH"
            elif wy < self.y:
                return "MOVE_SOUTH"

        if not stench and not breeze:
            for nx, ny, _ in self.neighbors(self.x, self.y):
                if (nx, ny) not in self.unsafe:
                    self.safe.add((nx, ny))
                    self.unknown.discard((nx, ny))

        if scream:
            self.arrow = False
            self.wumpus_inferred = False
            for x in range(1, 5):
                for y in range(1, 5):
                    self.safe.add((x, y))

        if glitter and not self.has_gold:
            self.has_gold = True
            return "GRAB"
        if self.has_gold:
            path = self.a_star((self.x, self.y), (1, 1))
            if path:
                nx, ny = path[0]
                if nx > self.x:
                    return "MOVE_EAST"
                elif nx < self.x:
                    return "MOVE_WEST"
                elif ny > self.y:
                    return "MOVE_NORTH"
                elif ny < self.y:
                    return "MOVE_SOUTH"
            return "CLIMB"

        # Prefer safe frontier, but if none, backtrack to last visited square with safe moves
        safe_frontier = [cell for cell in self.safe if cell not in self.visited]
        if safe_frontier:
            safe_frontier.sort(key=lambda c: abs(self.x - c[0]) + abs(self.y - c[1]))
            target = safe_frontier[0]
            path = self.a_star((self.x, self.y), target)
            if path:
                nx, ny = path[0]
                if nx > self.x:
                    return "MOVE_EAST"
                elif nx < self.x:
                    return "MOVE_WEST"
                elif ny > self.y:
                    return "MOVE_NORTH"
                elif ny < self.y:
                    return "MOVE_SOUTH"
        # If no safe moves from current square, backtrack to last visited square with unvisited safe neighbors
        for prev in reversed(list(self.visited)):
            unvisited_safe = [n for n in self.neighbors(*prev) if (n[0], n[1]) in self.safe and (n[0], n[1]) not in self.visited]
            if unvisited_safe:
                path = self.a_star((self.x, self.y), prev)
                if path:
                    nx, ny = path[0]
                    if nx > self.x:
                        return "MOVE_EAST"
                    elif nx < self.x:
                        return "MOVE_WEST"
                    elif ny > self.y:
                        return "MOVE_NORTH"
                    elif ny < self.y:
                        return "MOVE_SOUTH"
        # If no unknowns left or all are unsafe, or no way to backtrack, take a risk
        risky_candidates = [cell for cell in self.unknown if cell not in self.unsafe]
        if risky_candidates:
            risky_candidates.sort(key=lambda c: abs(self.x - c[0]) + abs(self.y - c[1]))
            target = risky_candidates[0]
            path = self.a_star((self.x, self.y), target, allow_unknown=True)
            if path:
                nx, ny = path[0]
                if nx > self.x:
                    return "MOVE_EAST"
                elif nx < self.x:
                    return "MOVE_WEST"
                elif ny > self.y:
                    return "MOVE_NORTH"
                elif ny < self.y:
                    return "MOVE_SOUTH"
        # If no unknowns left or all are unsafe, climb out
        return "CLIMB"

    def update_position(self, action, environment):
        bump = scream = False
        died = False
        death_type = None
        climbed_out = False
        # Direct move actions
        if action == "MOVE_NORTH":
            nx, ny, bump = environment.move(self.x, self.y, 1)
            self.x, self.y = nx, ny
            self.performance -= 1
            if bump:
                self.performance -= 1
        elif action == "MOVE_EAST":
            nx, ny, bump = environment.move(self.x, self.y, 0)
            self.x, self.y = nx, ny
            self.performance -= 1
            if bump:
                self.performance -= 1
        elif action == "MOVE_SOUTH":
            nx, ny, bump = environment.move(self.x, self.y, 3)
            self.x, self.y = nx, ny
            self.performance -= 1
            if bump:
                self.performance -= 1
        elif action == "MOVE_WEST":
            nx, ny, bump = environment.move(self.x, self.y, 2)
            self.x, self.y = nx, ny
            self.performance -= 1
            if bump:
                self.performance -= 1
        elif action == "SHOOT" and self.arrow:
            self.arrow = False
            scream = environment.shoot(self.x, self.y, self.dir)
            self.performance -= 10
        elif action == "GRAB":
            self.has_gold = True
            self.performance += 1000
        elif action == "CLIMB":
            # Climb out if at start
            if (self.x, self.y) == (1, 1):
                climbed_out = True
                if self.has_gold:
                    self.performance += 0  # Already rewarded for gold
                else:
                    self.performance -= 1  # Penalty for climbing out without gold
        # Check for death by pit or wumpus
        if hasattr(environment, 'grid'):
            cell = environment.grid.get((self.x, self.y))
            if cell is not None:
                if hasattr(cell, 'name') and cell.name == 'PIT':
                    died = True
                    death_type = 'pit'
                    self.performance -= 1000
                elif hasattr(cell, 'name') and cell.name == 'WUMPUS':
                    died = True
                    death_type = 'wumpus'
                    self.performance -= 1000
        return bump, scream, died, death_type, climbed_out
