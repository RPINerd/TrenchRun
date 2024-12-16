"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.event import Event

    from trench import Game

import pygame

import config as cfg
from render import draw_text_centre, draw_text_right
from utils import timeit


class Screen:

    """"""

    def __init__(self, game: Game):
        self.game = game

    def handle_events(self):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass


class MainMenuScreen(Screen):

    """"""

    def __init__(self, game: Game):
        super().__init__(game)
        # Initialize game-specific variables and objects

    def handle_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.set_screen(GameplayScreen(self.game))
                elif event.key == pygame.K_q:
                    self.game.violent_death = not self.game.violent_death
                    pass
                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False

    def update(self, dt):
        # Update game logic and handle user input
        # Example: Move player, update enemies, check for collisions
        pass

    def render(self, surface):

        def render_intro_text(surface):
            centre = cfg.CANVAS_CENTER
            draw_text_centre(surface, "Star Wars", 190, 58, cfg.INTRO_TEXT_COLOUR)
            draw_text_centre(surface, "Press Space to begin your attack run", 340, 24, cfg.INTRO_TEXT_COLOUR)
            draw_text_centre(surface, "Use Cursor Keys to move", 420, 19, cfg.INTRO_TEXT_COLOUR)
            draw_text_centre(surface, "Use Space to launch Proton Torpedo", 440, 19, cfg.INTRO_TEXT_COLOUR)
            draw_text_right(surface, cfg.VERSION, cfg.CANVAS_WIDTH - 16, 14, 14, cfg.INTRO_TEXT_COLOUR)

            x1 = centre[0] - 160
            y1 = centre[1] + (185 if self.game.violent_death else 205)
            x2 = centre[0] + 160
            y2 = centre[1] + 225
            # TODO method unique to codeskulptor, need to implement
            surface.draw_polygon(((x1, y1), (x2, y1), (x2, y2), (x1, y2)), 1, "Black", "Black")
            draw_text_centre(surface, "Press 'Q' to turn " + ("OFF" if self.game.violent_death else "ON") + " flashing colours", 520, 18, cfg.WARNING_TEXT_COLOUR)
            if self.game.violent_death:
                draw_text_centre(surface, "Note: this game contains flashing colours which are not suitable for sufferers of epilepsy", 500, 18, cfg.WARNING_TEXT_COLOUR)

        def render_stars(surface):
            star_colours = []
            for shade in range(8, 16):
                component = hex(16 * shade)
                colour = "#" + component + component + component
                star_colours.append(colour)

            i = 0
            l = len(star_colours)
            for star in stars:
                # TODO method unique to codeskulptor, need to implement
                surface.draw_circle(star, 1, 1, star_colours[i % l])
                i += 1

        render_stars(surface)
        render_deathstar(surface)
        render_intro_text(surface)


class GameplayScreen(Screen):

    """"""

    def __init__(self, game: Game):
        super().__init__(game)
        """Initialize game-specific variables and objects"""
        self.game.game_mode = cfg.MODE_GAME
        self.game.pos = [0, 0, 0]
        self.game.vel = [0, 0, cfg.FORWARD_VELOCITY_MS]
        self.game.acc = [0, 0, 0]
        self.game.pt_pos = []
        self.game.pt_launch_position = -1
        self.game.reached_launch_position = False
        self.game.dead = False
        self.game.current_barrier_index = 0
        self.game.explosion_countdown = 0
        self.game.barriers = create_barriers()
        set_message("Use the Force")

    def handle_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.game.acc[0] = -cfg.ACCELERATION_MSS
                elif event.key == pygame.K_RIGHT:
                    self.game.acc[0] = cfg.ACCELERATION_MSS
                elif event.key == pygame.K_UP:
                    self.game.acc[1] = -cfg.ACCELERATION_MSS
                elif event.key == pygame.K_DOWN:
                    self.game.acc[1] = cfg.ACCELERATION_MSS
                elif event.key == pygame.K_SPACE:
                    launch_proton_torpedoes()
                elif event.key == pygame.K_ESCAPE:
                    self.game.set_screen(MainMenuScreen(self.game))

    def update(self, dt):
        # Update game logic and handle user input
        # Example: Move player, update enemies, check for collisions
        pass

    def render(self, surface):
        # Render the game state on the provided surface
        # Example: Draw player, enemies, background, UI elements
        pass

    @timeit
    def create_barriers() -> list:
        """
        Creates all of the barriers that appear in the game

        Each Barrier is represented by three elements:
        Start Position - the distance along the trench that the barrier starts
        Length - the length of the barrier
        Blocks - an array of 9 ints, either 1 or 0, that indicate which blocks in a 3x3 square appear in the barrier.

        The Barriers are placed in a list which is sequenced by the Start Position of the Barriers.
        This allows the rendering and collision code to consider only the barriers immediately surrounding the ship

        Args:
            None

        Returns:
            list: A list of all the barriers in the game
        """
        barriers = []

        # Determine Start Position and Last Position
        position = 150.0
        limit = cfg.LAUNCH_POSITION_M - 150
        while position < limit:
            # Create a totally solid barrier
            blocks = [1] * 9

            # Punch a number of empty blocks in the barrier, adjusted by distance to exhaust port
            empty_blocks = int((1.0 - (position / limit)) * 8) + 2
            for i in range(0, empty_blocks):
                blocks[random.randrange(9)] = 0

            # Calculate a random length
            length = random.randrange(5) + 5
            barriers.append((position, length, blocks))
            position += length
            position += 40 + random.randrange(30)

        return barriers
