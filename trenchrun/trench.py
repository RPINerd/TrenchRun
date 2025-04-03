"""
"""

import config as cfg
import pygame
from screens import MainMenuScreen, Screen
from utils import create_stars


class Game:

    """The primary class containing all game logic and state"""

    def __init__(self) -> None:
        """
        Initialize the game

        Initialize pygame module, game window, set up the starting screen, and call a few helper
        initialization methods
        """
        pygame.init()
        pygame.display.set_caption("Star Wars")
        self.screen = pygame.display.set_mode((cfg.CANVAS_WIDTH, cfg.CANVAS_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running: bool = True
        self.active_screen: Screen = MainMenuScreen(self)

        self.stars: list = create_stars()
        self.violent_death: bool = False

    def run(self) -> None:
        """Main game loop"""
        while self.running:
            self.screen.fill((0, 0, 0))
            self.clock.tick(60)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.active_screen.handle_events(events)
            self.active_screen.update()
            self.active_screen.render(self.screen)

            pygame.display.flip()

    def set_screen(self, screen: Screen) -> None:
        """Set a new active screen to be rendering"""
        self.active_screen = screen


if __name__ == "__main__":
    game = Game()
    game.run()
