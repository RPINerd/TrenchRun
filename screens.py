"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.event import Event

    from trench import Game

import math

import pygame

import config as cfg
import render
import utils


class Screen:

    """"""

    def __init__(self, game: Game):
        self.game = game

    def handle_events(self):
        pass

    def update(self):
        pass

    def render(self, surface):
        pass


class MainMenuScreen(Screen):

    """"""

    def __init__(self: Screen, game: Game):
        super().__init__(game)
        # TODO on init draw the screen, then only redraw on event Q
        # Initialize game-specific variables and objects

    def handle_events(self: MainMenuScreen, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.set_screen(GameplayScreen(self.game))
                elif event.key == pygame.K_q:
                    self.game.violent_death = not self.game.violent_death
                    pass
                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False

    def update(self: MainMenuScreen) -> None:
        # Update game logic and handle user input
        # Example: Move player, update enemies, check for collisions
        pass

    def render(self: MainMenuScreen, surface: pygame.Surface) -> None:
        render.stars(self.game.stars, surface)
        render.deathstar(surface)
        render.intro_text(self, surface)


class GameplayScreen(Screen):

    """"""

    def __init__(self, game: Game) -> None:
        """Initialize game-specific variables and objects"""
        super().__init__(game)
        self.game.game_mode = cfg.MODE_GAME
        # TODO maybe make local to just self, only applies to current game
        self.game.pos = [0.0, 0.0, 0.0]
        self.game.vel = [0.0, 0.0, cfg.FORWARD_VELOCITY_MS]
        self.game.acc = [0.0, 0.0, 0.0]
        self.game.pt_pos = []
        self.game.pt_launch_position = -1
        self.game.reached_launch_position = False
        self.game.dead = False
        self.game.current_barrier_index = 0
        self.game.explosion_countdown = 0
        self.game.barriers = utils.create_barriers()
        render.message("Use the Force")

    def handle_events(self, events: list[Event]) -> None:
        """"""
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
                    self.launch_proton_torpedoes()
                elif event.key == pygame.K_ESCAPE:
                    self.game.set_screen(MainMenuScreen(self.game))

    def update(self) -> None:
        """"""
        if not self.game.dead:
            self.move_ship()
            self.move_torpedoes()
            self.constrain_ship()
            self.check_for_collisions()
            # self.generate_messages()
            if self.game.pos[2] > cfg.TRENCH_LENGTH_M + 60:
                self.game.game_mode = cfg.MODE_VICTORY if self.game.explosion_countdown > 0 else cfg.MODE_INTRO

    def render(self, surface: pygame.Surface) -> None:
        """"""
        # TODO only render when dead
        render.death(surface, self.game.dead, self.game.violent_death)

        render.trench(surface, self.game.pos)
        render.barriers(surface, self.game.barriers, self.game.current_barrier_index, self.game.pos)

        if self.game.reached_launch_position:
            render.exhaust_port(surface, self.game.pos)
            render.torpedoes(surface)

        render.distance(surface, self.get_distance_to_launch_position())
        # render.message(surface)

    def move_ship(self) -> None:
        """"""
        # Pull up at the end of the Trench
        if self.game.pos[2] > cfg.EXHAUST_PORT_POSITION_M:
            self.game.acc[1] = -cfg.ACCELERATION_MSS
            if self.game.pt_launch_position < 0:
                render.message("You forgot to fire your torpedoes")
                self.game.pt_launch_position = 0

        # Slow down when poised to launch torpedo
        factor = float(cfg.FPS)
        if self.game.pt_launch_position < 0 and self.is_close_to_launch_position():
            factor *= 4

        for i in range(0, 3):
            self.game.pos[i] += self.game.vel[i] / factor
            if self.game.acc[i] != 0:
                self.game.vel[i] += self.game.acc[i] / factor
                if self.game.vel[i] < -cfg.VELOCITY_MAX_MS:
                    self.game.vel[i] = -cfg.VELOCITY_MAX_MS
                elif self.game.vel[i] > cfg.VELOCITY_MAX_MS:
                    self.game.vel[i] = cfg.VELOCITY_MAX_MS
            elif i < 2:
                self.game.vel[i] *= cfg.VELOCITY_DAMPEN

    def move_torpedoes(self) -> None:
        """Move the Proton Torpedoes down the trench"""
        if len(self.game.pt_pos) > 0:
            hit = False
            bullseye = False
            for p in self.game.pt_pos:
                # Check if the torpedo has reached the point at which it dives towards the floor of the trench
                if p[2] - self.game.pt_launch_position >= cfg.PROTON_TORPEDO_RANGE_M:
                    p[1] += cfg.PROTON_TORPEDO_VELOCITY_MS * 0.5 / cfg.FPS
                else:
                    p[2] += cfg.PROTON_TORPEDO_VELOCITY_MS / cfg.FPS

                # Check if the torpedo has hit the floor of the trench
                if p[1] > cfg.TRENCH_HEIGHT_M / 2:
                    hw = cfg.EXHAUST_PORT_WIDTH_M / 2
                    z = cfg.EXHAUST_PORT_POSITION_M
                    ex1 = -hw
                    ex2 = hw
                    ez1 = z - hw
                    ez2 = z + hw
                    # Check if torpedo entirely fit within the exhaust port
                    if p[0] - cfg.PROTON_TORPEDO_RADIUS_M >= ex1 and \
                        p[0] + cfg.PROTON_TORPEDO_RADIUS_M <= ex2 and \
                        p[2] - cfg.PROTON_TORPEDO_RADIUS_M >= ez1 and \
                        p[2] + cfg.PROTON_TORPEDO_RADIUS_M <= ez2:
                        bullseye = True
                    hit = True
            if hit:
                self.game.pt_pos = []		# Delete the torpedos
                if bullseye:
                    render.message("Great shot kid - That was one in a million")
                    self.game.explosion_countdown = 180
                else:
                    render.message("Negative - It just impacted off the surface")

    def constrain_ship(self) -> None:
        """Keep ship within the trench"""
        tw = cfg.TRENCH_WIDTH_M // 2
        th = cfg.TRENCH_HEIGHT_M // 2

        # Keep the ship within the horizontal span of the trench
        m = cfg.SHIP_WIDTH_M / 2
        if self.game.pos[0] < (-tw + m):
            self.game.pos[0] = -tw + m
        elif self.game.pos[0] > (tw - m):
            self.game.pos[0] = tw - m

        # Keep the ship within the vertical span of the trench
        m = cfg.SHIP_HEIGHT_M / 2
        # Allow the ship to leave the trench after it has launched the torpedoes
        if self.game.pos[1] < (-th + m) and self.game.pt_launch_position < 0:
            self.game.pos[1] = -th + m
        elif self.game.pos[1] > (th - m):
            self.game.pos[1] = th - m

    def check_for_collisions(self) -> None:
        """Determine whether the ship has collided with any blocks"""
        if self.game.current_barrier_index >= len(self.game.barriers):
            return

        barrier = self.game.barriers[self.game.current_barrier_index]

        # Check if we are in the same Z position as the barrier
        if self.game.pos[2] > barrier[0] and self.game.pos[2] < barrier[0] + barrier[1]:
            # Calculate the area that our ship occupies
            x1 = self.game.pos[0] - cfg.SHIP_WIDTH_M / 2.0
            x2 = x1 + cfg.SHIP_WIDTH_M
            y1 = self.game.pos[1] - cfg.SHIP_HEIGHT_M / 2.0
            y2 = y1 + cfg.SHIP_HEIGHT_M

            # Calculate block size
            bw = cfg.TRENCH_WIDTH_M / 3.0
            bh = cfg.TRENCH_HEIGHT_M / 3.0
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
                                render.message("Game Over")
                                self.game.dead = True

    def get_distance_to_launch_position(self) -> float:
        """Calculate the distance to the launch position"""
        return cfg.LAUNCH_POSITION_M - self.game.pos[2]

    def is_close_to_launch_position(self) -> bool:
        """Indicates whether the ship is 'close' to the launch position."""
        return math.fabs(self.get_distance_to_launch_position()) < 100.0

    def launch_proton_torpedoes(self) -> None:
        """
        Fire the Proton Torpedoes

        If the torpedoes have not already been launched, they are spawned slightly under the ship
        """
        if self.game.pt_launch_position < 0 and self.is_close_to_launch_position():
            pt_pos.append([self.game.pos[0] - cfg.PROTON_TORPEDO_SPAN_M, self.game.pos[1] + 1, self.game.pos[2]])
            pt_pos.append([self.game.pos[0] + cfg.PROTON_TORPEDO_SPAN_M, self.game.pos[1] + 1, self.game.pos[2]])
            self.game.pt_launch_position = self.game.pos[2]
