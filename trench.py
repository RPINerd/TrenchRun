"""
"""
import random

import pygame

import config as cfg
from screens import MainMenuScreen, Screen
from utils import timeit


class Game:

    """The primary class containing all game logic and state"""

    def __init__(self):
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

        stars: list = create_stars()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000  # Delta time in seconds
            events = pygame.event.get()

            self.active_screen.handle_events(events)
            self.active_screen.update(dt)
            self.active_screen.render(self.screen)

            pygame.display.flip()

    def set_screen(self, screen: Screen) -> None:
        """Set a new active screen to be rendering"""
        self.active_screen = screen


@timeit
def create_stars(star_count: int = 300) -> list[tuple[int, int]]:
    """
    Create a list of random star positions

    Args:
        star_count (int): The number of stars to create; default is 300

    Returns:
        list: A list of star position tuples
    """
    stars: list[tuple[int, int]] = []
    for _ in range(star_count):
        x: int = random.randrange(cfg.CANVAS_WIDTH)
        y: int = random.randrange(cfg.CANVAS_HEIGHT)
        stars.append((x, y))

    return stars


if __name__ == "__main__":
    game = Game()
    game.run()
