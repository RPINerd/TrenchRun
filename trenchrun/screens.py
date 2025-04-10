"""Holds classes representing each game state (Main Menu, Gameplay, Victory)"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.event import Event
    from trench import Game

import config as cfg
import objects
import pygame
import render
import utils
from icecream import ic


class Screen:

    """Generic Base Class for Screens"""

    def __init__(self, game: Game) -> None:
        """"""
        self.game = game

    def handle_events(self) -> None:
        """"""
        pass

    def update(self) -> None:
        """"""
        pass

    def render(self, surface: pygame.Surface) -> None:
        """"""
        pass


class MainMenuScreen(Screen):

    """
    Start Screen

    The initial screen that the player sees when the game is launched

    Attributes:
        game (Game): The game object containing the game state and logic
    """

    def __init__(self: Screen, game: Game) -> None:
        """"""
        super().__init__(game)
        # TODO on init draw the screen, then only redraw on event Q
        # Initialize game-specific variables and objects

    def handle_events(self: MainMenuScreen, events: list[Event]) -> None:
        """"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.set_screen(GameplayScreen(self.game))
                elif event.key == pygame.K_q:
                    self.game.violent_death = not self.game.violent_death
                    pass
                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False
                elif event.key == pygame.K_v:
                    self.game.set_screen(VictoryScreen(self.game))

    def update(self: MainMenuScreen) -> None:
        """"""
        pass

    def render(self: MainMenuScreen, surface: pygame.Surface) -> None:
        """"""
        render.stars(self.game.stars, surface)
        render.deathstar(surface)
        render.intro_text(self, surface)


class GameplayScreen(Screen):

    """
    The Core Game

    The main game screen where the player controls the ship and fires torpedoes

    Attributes:
        game (Game): The game object containing the game state and logic
    """

    def __init__(self, game: Game) -> None:
        """Initialize game-specific variables and objects"""
        super().__init__(game)
        self.ship = objects.PlayerShip()
        self.torpedos = objects.Torpedos()
        self.pos: list[float] = [0.0, 0.0, 0.0]
        self.vel: list[float] = [0.0, 0.0, cfg.FORWARD_VELOCITY_MS]
        self.acc: list[float] = [0.0, 0.0, 0.0]
        self.pt_pos: list[list[float]] = []
        self.pt_launch_position: list[float, float, float] = [0.0, 0.0, -1.0]
        self.reached_launch_position: bool = False
        self.dead: bool = False
        self.current_barrier_index: int = 0
        self.bullseye: bool = False
        self.barriers = utils.create_barriers()

        self.message = {"text": "Use the Force", "timer": 120}  # Timer is in frames (120 frames of message display)

        self.debug = True

    def handle_events(self, events: list[Event]) -> None:
        """"""
        for event in events:
            if event.type in {pygame.KEYDOWN, pygame.KEYUP} and event.key in cfg.MOVEMENT_KEYS:
                key_type = 1 if event.type == pygame.KEYDOWN else 0
                self.ship.steer(key_type, event.key)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.ship.reached_launch_zone:
                    self.torpedos.fire(self.ship.get_position())
                elif event.key == pygame.K_ESCAPE:
                    self.game.set_screen(MainMenuScreen(self.game))

    def update(self) -> None:
        """"""
        if self.dead:
            self.game.set_screen(MainMenuScreen(self.game))

        if (self.pos[2] > cfg.TRENCH_LENGTH + 60) and (self.bullseye):
            self.game.set_screen(VictoryScreen(self.game))

        # ic(self.ship)
        travel_event = self.ship.travel()
        if travel_event:
            self._create_message(travel_event)
        self.check_for_collisions()
        ic(self.torpedos)
        if self.torpedos.launched:
            # ic(self.torpedos.range)
            self.torpedos.travel()
            self.torpedos.check_impact()
            impact_outcome = self.torpedos.bullseye_check()
            if impact_outcome:
                self._create_message(impact_outcome)

        if self.message["timer"] > 0:
            render.message(self.game.screen, self.message["text"])
            self.message["timer"] -= 1

    def render(self, surface: pygame.Surface) -> None:
        """"""
        current_position = self.ship.get_position()
        # TODO only render when dead
        render.death(surface, self.dead, self.game.violent_death)

        render.trench(surface, current_position)
        render.barriers(surface, self.barriers, self.current_barrier_index, current_position)

        render.exhaust_port(surface, current_position)
        if self.torpedos.launched:
            ic(self.torpedos)
            render.torpedoes(surface, self.torpedos)

        render.distance(surface, int(self.ship.get_distance()))

        if self.debug:
            render.debug(surface, self.ship.get_position())

    def move_torpedoes(self) -> None:
        """Move the Proton Torpedoes down the trench"""
        hit = False
        bullseye = False

        for p in self.pt_pos:
            # Check if the torpedo has reached the point at which it dives towards the floor of the trench
            if p[2] - self.pt_launch_position[2] >= cfg.TORPEDO_RANGE:
                p[1] += cfg.PROTON_TORPEDO_VELOCITY_MS * 0.5 / cfg.FPS
            else:
                p[2] += cfg.PROTON_TORPEDO_VELOCITY_MS / cfg.FPS

            # Check if the torpedo has hit the floor of the trench
            if p[1] > cfg.TRENCH_HEIGHT / 2:
                hw = cfg.EXHAUST_WIDTH / 2
                z = cfg.EXHAUST_POSITION
                ex1 = -hw
                ex2 = hw
                ez1 = z - hw
                ez2 = z + hw
                # Check if torpedo entirely fit within the exhaust port
                if p[0] - cfg.TORPEDO_RADIUS >= ex1 and \
                    p[0] + cfg.TORPEDO_RADIUS <= ex2 and \
                    p[2] - cfg.TORPEDO_RADIUS >= ez1 and \
                    p[2] + cfg.TORPEDO_RADIUS <= ez2:
                    bullseye = True
                hit = True
        if hit:
            self.pt_pos = []  # Delete the torpedos
            if bullseye:
                self._create_message("Great shot kid - That was one in a million!")
                self.bullseye = True
            else:
                self._create_message("Negative - It just impacted off the surface..")
                # TODO Game over screen

    def check_for_collisions(self) -> None:
        """Determine whether the ship has collided with any blocks"""
        # TODO borked, but works if you never move
        if self.current_barrier_index >= len(self.barriers):
            return

        barrier: tuple[int, int, list[int]] = self.barriers[self.current_barrier_index]

        # Check if we are in the same Z position as the barrier
        if self.pos[2] > barrier[0] and self.pos[2] < barrier[0] + barrier[1]:

            # Calculate the area that our ship occupies
            x1 = self.pos[0] - cfg.SHIP_WIDTH_M / 2.0
            x2 = x1 + cfg.SHIP_WIDTH_M
            y1 = self.pos[1] - cfg.SHIP_HEIGHT_M / 2.0
            y2 = y1 + cfg.SHIP_HEIGHT_M

            # Calculate block size
            bw = cfg.TRENCH_WIDTH / 3.0
            bh = cfg.TRENCH_HEIGHT / 3.0
            bhw = bw / 2.0
            bhh = bh / 2.0
            for by in range(-1, 2):
                by1 = by * bh - bhh
                by2 = by1 + bh

                # Check to see whether we intersect vertically
                if y1 < by2 and y2 > by1:
                    for bx in range(-1, 2):
                        block_index = (by + 1) * 3 + bx + 1
                        if barrier[2][block_index] == 1:
                            bx1 = bx * bw - bhw
                            bx2 = bx1 + bw

                            # Check to see whether we intersect horizontally
                            if x1 < bx2 and x2 > bx1:
                                self._create_message("Game Over", 1200)
                                self.dead = True

    def _create_message(self, text: str, time: int = 120) -> None:
        """Create a message to be displayed on the screen"""
        self.message["text"] = text
        self.message["timer"] = time


class VictoryScreen(Screen):

    """"""

    def __init__(self, game: Game) -> None:
        """"""
        super().__init__(game)
        self.explosion_countdown = 180
        self.particles = utils.create_particles()

    def handle_events(self, events: list[Event]) -> None:
        """Allow the user to return to the main menu with ESC"""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.set_screen(MainMenuScreen(self.game))

    def update(self) -> None:
        """On each update, decrement the explosion countdown"""
        self.explosion_countdown -= 1

    def render(self, surface: pygame.Surface) -> None:
        """Render the victory animation"""
        render.stars(self.game.stars, surface)
        if self.explosion_countdown <= 0:
            if self.explosion_countdown > -160:
                base_colour = (64, 32, 16)
                factor = -self.explosion_countdown / 10.0
                colour = "#"
                for c in range(0, 3):
                    colour += utils.hex(base_colour[c] * factor)
                render.deathstar(surface, colour)
            elif self.explosion_countdown == -160:
                self.particles = utils.create_particles()
            elif self.explosion_countdown > -400:
                render.particles(surface, self.particles)
                self.particles = utils.move_particles(self.particles)
            else:
                self.game.set_screen(MainMenuScreen(self.game))
        else:
            render.deathstar(surface)
