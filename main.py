import pygame
import sys
from environment import WumpusEnvironment
from agent import EnhancedAgent
from models import Position, Direction


class WumpusGame:
    def __init__(self):
        pygame.init()
        self.cell_size = 80
        self.cave_cols = 4
        self.cave_rows = 4
        self.legend_width = 420
        self.left_offset = 40  # Add left margin
        self.width = self.left_offset + self.cell_size * self.cave_cols + self.legend_width
        self.height = max(self.cell_size * self.cave_rows + 40, 600)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Wumpus World")
        self.env = WumpusEnvironment()
        self.agent = EnhancedAgent()
        # Set agent position and direction to match environment
        self.agent.x = 1
        self.agent.y = 1
        self.agent.dir = Direction.EAST
        self.font = pygame.font.Font(None, 36)
        self.wumpus_dead = False

    def draw_symbol(self, symbol, surface, cx, cy, *, wumpus_dead=False):
        """
        Draws a symbol at (cx, cy) on the given surface.
        symbol: str, one of 'breeze', 'stench', 'glitter', 'pit', 'wumpus', 'gold', 'agent', 'pit_x', 'wumpus_x', 'wumpus_dead_x'
        """
        if symbol == 'breeze':
            pygame.draw.circle(surface, (0, 200, 255), (cx-15, cy), 10, 2)
        elif symbol == 'stench' and not wumpus_dead:
            pygame.draw.rect(surface, (0, 200, 0), (cx-8, cy-23, 16, 16), 2)
        elif symbol == 'glitter':
            pygame.draw.polygon(surface, (255, 215, 0), [
                (cx+15, cy-10), (cx+25, cy), (cx+15, cy+10), (cx+5, cy)
            ], 0)
        elif symbol == 'pit':
            pygame.draw.circle(surface, (0, 0, 0), (cx, cy), 18, 2)
        elif symbol == 'wumpus':
            pygame.draw.circle(surface, (128, 0, 128), (cx, cy), 18, 0)
        elif symbol == 'gold':
            pygame.draw.polygon(surface, (255, 215, 0), [
                (cx, cy-15), (cx+15, cy), (cx, cy+15), (cx-15, cy)
            ], 0)
        elif symbol == 'agent':
            pygame.draw.circle(surface, (255, 0, 0), (cx, cy), 20)
        elif symbol == 'pit_x':
            pygame.draw.line(surface, (200,0,0), (cx-20, cy-20), (cx+20, cy+20), 3)
            pygame.draw.line(surface, (200,0,0), (cx+20, cy-20), (cx-20, cy+20), 3)
        elif symbol == 'wumpus_x':
            pygame.draw.line(surface, (128,0,128), (cx-20, cy-20), (cx+20, cy+20), 3)
            pygame.draw.line(surface, (128,0,128), (cx+20, cy-20), (cx-20, cy+20), 3)
        elif symbol == 'wumpus_dead_x':
            pygame.draw.line(surface, (0,0,0), (cx-20, cy-20), (cx+20, cy+20), 4)
            pygame.draw.line(surface, (0,0,0), (cx+20, cy-20), (cx-20, cy+20), 4)

    def draw_legend(self):
        legend_items = [
            ('breeze', 'Breeze: There is a pit in an adjacent cell'),
            ('stench', 'Stench: There is a Wumpus in an adjacent cell'),
            ('glitter', 'Glitter: There is gold in this cell'),
            ('pit', 'Pit: Deadly pit'),
            ('pit_x', 'Inferred Pit: Agent suspects a pit'),
            ('wumpus', 'Wumpus: The Wumpus is here'),
            ('wumpus_x', 'Inferred Wumpus: Agent suspects the Wumpus'),
            ('wumpus_dead_x', 'Dead Wumpus: Wumpus was killed here'),
            ('gold', 'Gold: The gold'),
            ('agent', 'Agent: You'),
        ]
        legend_x = self.left_offset + self.cell_size * self.cave_cols + 40
        legend_y = 40
        header_font = pygame.font.Font(None, 28)
        explanation_font = pygame.font.Font(None, 20)
        header = header_font.render("Legend", True, (0,0,0))
        self.screen.blit(header, (legend_x, legend_y))
        explanation = explanation_font.render("Symbols and their meaning:", True, (0,0,0))
        self.screen.blit(explanation, (legend_x, legend_y + 28))
        for i, (symbol, label) in enumerate(legend_items):
            cy = legend_y + 65 + i * 44
            cx = legend_x + 20
            self.draw_symbol(symbol, self.screen, cx, cy, wumpus_dead=self.wumpus_dead)
            text = explanation_font.render(label, True, (0,0,0))
            self.screen.blit(text, (cx + 50, cy - 12))

    def draw(self):
        self.screen.fill((255, 255, 255))
        # Draw score at the top center of the cave
        score = getattr(self.agent, 'performance', 0)
        score_text = self.font.render(f"Score: {score}", True, (0, 0, 0))
        score_x = self.left_offset + (self.cell_size * self.cave_cols) // 2 - score_text.get_width() // 2
        score_y = 5
        self.screen.blit(score_text, (score_x, score_y))
        # Draw cave grid and contents
        for x in range(self.cave_cols):
            for y in range(self.cave_rows):
                rect = pygame.Rect(self.left_offset + x * self.cell_size, y * self.cell_size + 40,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                # Only show perceptions for visited cells
                if (x+1, y+1) in self.agent.visited:
                    pos = Position(x=x+1, y=y+1)
                    perception = self.env.get_perception(pos)
                    cx = self.left_offset + x * self.cell_size + self.cell_size // 2
                    cy = (self.cave_rows - 1 - y) * self.cell_size + self.cell_size // 2 + 40
                    if perception.breeze:
                        self.draw_symbol('breeze', self.screen, cx, cy, wumpus_dead=self.wumpus_dead)
                    if perception.stench and not self.wumpus_dead:
                        self.draw_symbol('stench', self.screen, cx, cy, wumpus_dead=self.wumpus_dead)
                    if perception.glitter:
                        self.draw_symbol('glitter', self.screen, cx, cy, wumpus_dead=self.wumpus_dead)
                # Show inferred pits (red X) and inferred wumpus (purple X)
                cell = (x+1, y+1)
                cx = self.left_offset + x * self.cell_size + self.cell_size // 2
                cy = (self.cave_rows - 1 - y) * self.cell_size + self.cell_size // 2 + 40
                if cell in getattr(self.agent, 'unsafe', set()):
                    self.draw_symbol('pit_x', self.screen, cx, cy)
                if self.agent.wumpus_inferred and self.agent.wumpus_location is not None:
                    wx, wy, _ = self.agent.wumpus_location
                    if (x+1, y+1) == (wx, wy) and not self.wumpus_dead:
                        self.draw_symbol('wumpus_x', self.screen, cx, cy)
        # Draw a black X where the Wumpus was killed, if known
        if self.wumpus_dead and self.agent.wumpus_location is not None:
            wx, wy, _ = self.agent.wumpus_location
            cx = self.left_offset + (wx-1) * self.cell_size + self.cell_size // 2
            cy = (self.cave_rows - wy) * self.cell_size + self.cell_size // 2 + 40
            self.draw_symbol('wumpus_dead_x', self.screen, cx, cy)
        pos_x, pos_y = self.agent.x, self.agent.y
        x = self.left_offset + (pos_x - 1) * self.cell_size + self.cell_size // 2
        y = (self.cave_rows - pos_y) * self.cell_size + self.cell_size // 2 + 40
        self.draw_symbol('agent', self.screen, x, y)
        self.draw_legend()
        pygame.display.flip()

    def draw_full_cave(self):
        self.screen.fill((255, 255, 255))
        # Draw score at the top center of the cave
        score = getattr(self.agent, 'performance', 0)
        score_text = self.font.render(f"Score: {score}", True, (0, 0, 0))
        score_x = self.left_offset + (self.cell_size * self.cave_cols) // 2 - score_text.get_width() // 2
        score_y = 5
        self.screen.blit(score_text, (score_x, score_y))
        for x in range(self.cave_cols):
            for y in range(self.cave_rows):
                rect = pygame.Rect(self.left_offset + x * self.cell_size, y * self.cell_size + 40,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                pos = Position(x=x+1, y=y+1)
                cx = self.left_offset + x * self.cell_size + self.cell_size // 2
                cy = (self.cave_rows - 1 - y) * self.cell_size + self.cell_size // 2 + 40
                # Show all features
                cell = (x+1, y+1)
                feature = self.env.grid.get(cell)
                if feature is not None:
                    if hasattr(feature, 'name'):
                        if feature.name == 'WUMPUS':
                            self.draw_symbol('wumpus', self.screen, cx, cy)
                        elif feature.name == 'PIT':
                            self.draw_symbol('pit', self.screen, cx, cy)
                        elif feature.name == 'GOLD':
                            self.draw_symbol('gold', self.screen, cx, cy)
                # Show all sensor inputs
                perception = self.env.get_perception(pos)
                if perception.breeze:
                    self.draw_symbol('breeze', self.screen, cx, cy)
                if perception.stench:
                    self.draw_symbol('stench', self.screen, cx, cy)
                if perception.glitter:
                    self.draw_symbol('glitter', self.screen, cx, cy)
        # Draw agent's last position
        pos_x, pos_y = self.agent.x, self.agent.y
        x = self.left_offset + (pos_x - 1) * self.cell_size + self.cell_size // 2
        y = (self.cave_rows - pos_y) * self.cell_size + self.cell_size // 2 + 40
        self.draw_symbol('agent', self.screen, x, y)
        self.draw_legend()
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        bump = False
        scream = False
        death_message = None
        died = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Map arrow keys to direct move actions
                    if event.key == pygame.K_UP:
                        action = "MOVE_NORTH"
                    elif event.key == pygame.K_RIGHT:
                        action = "MOVE_EAST"
                    elif event.key == pygame.K_DOWN:
                        action = "MOVE_SOUTH"
                    elif event.key == pygame.K_LEFT:
                        action = "MOVE_WEST"
                    elif event.key == pygame.K_SPACE:
                        pos = Position(x=self.agent.x, y=self.agent.y)
                        perception = self.env.get_perception(pos)
                        action = self.agent.choose_action(perception, bump, scream)
                    else:
                        action = None
                    if action:
                        bump, scream, died, death_type, climbed_out = self.agent.update_position(action, self.env)
                        if scream:
                            self.wumpus_dead = True
                        elif died:
                            if death_type == 'pit':
                                death_message = "You fell into a pit!"
                            elif death_type == 'wumpus':
                                death_message = "You were eaten by the Wumpus!"
                            else:
                                death_message = "You died!"
                            running = False
                        elif climbed_out:
                            if self.agent.has_gold:
                                death_message = "You escaped with the gold!"
                            else:
                                death_message = "You climbed out without the gold."
                            running = False
            self.draw()
            clock.tick(60)
        if death_message:
            self.draw_full_cave()
            msg = self.font.render(death_message, True, (255, 0, 0))
            self.screen.blit(msg, (50, 200))
            pygame.display.flip()
            # Wait for any key before closing
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                        waiting = False
        pygame.quit()


def main():
    game = WumpusGame()
    game.run()


if __name__ == "__main__":
    main()
