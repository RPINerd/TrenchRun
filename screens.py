"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.event import Event

    from trench import Game

import random

import pygame

import config as cfg
import render
from utils import timeit


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
        self.game.barriers = self.create_barriers()
        render.message("Use the Force")

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

    def update(self):
        if not self.game.dead:
            self.move_ship()
            self.move_torpedoes()
            self.constrain_ship()
            self.check_for_collisions()
            self.generate_messages()

    def render(self, surface):
        render.death(surface)
        render.trench(surface)
        render.barriers(surface)
        render.exhaust_port(surface)
        render.torpedoes(surface)
        render.distance(surface)
        render.message(surface)

    @timeit
    def create_barriers(self) -> list:
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

    def move_ship():
        global pos, vel, acc, pt_launch_position

        # Pull up at the end of the Trench
        if pos[2] > cfg.EXHAUST_PORT_POSITION_M:
            acc[1] = -cfg.ACCELERATION_MSS
            if pt_launch_position < 0:
                set_message("You forgot to fire your torpedoes")
                pt_launch_position = 0

        # Slow down when poised to launch torpedo
        factor = float(fps)
        if pt_launch_position < 0 and is_close_to_launch_position():
            factor *= 4

        for i in range(0, 3):
            pos[i] += vel[i] / factor
            if acc[i] != 0:
                vel[i] += acc[i] / factor
                if vel[i] < -cfg.VELOCITY_MAX_MS:
                    vel[i] = -cfg.VELOCITY_MAX_MS
                elif vel[i] > cfg.VELOCITY_MAX_MS:
                    vel[i] = cfg.VELOCITY_MAX_MS
            elif i < 2:
                vel[i] *= cfg.VELOCITY_DAMPEN

    def move_torpedoes():
        global pt_pos, explosion_countdown
        if len(pt_pos) > 0:
            hit = False
            bullseye = False
            for p in pt_pos:
                # Check if the torpedo has reached the point at which it dives towards the floor of the trench
                if p[2] - pt_launch_position >= cfg.PROTON_TORPEDO_RANGE_M:
                    p[1] += cfg.PROTON_TORPEDO_VELOCITY_MS * 0.5 / fps
                else:
                    p[2] += cfg.PROTON_TORPEDO_VELOCITY_MS / fps

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
                pt_pos = []		# Delete the torpedos
                if bullseye:
                    set_message("Great shot kid - That was one in a million")
                    explosion_countdown = 180
                else:
                    set_message("Negative - It just impacted off the surface")

    def constrain_ship():
        """Keep ship within the trench"""
        tw = cfg.TRENCH_WIDTH_M // 2
        th = cfg.TRENCH_HEIGHT_M // 2

        # Keep the ship within the horizontal span of the trench
        m = cfg.SHIP_WIDTH_M / 2
        if pos[0] < (-tw + m):
            pos[0] = -tw + m
        elif pos[0] > (tw - m):
            pos[0] = tw - m

        # Keep the ship within the vertical span of the trench
        m = cfg.SHIP_HEIGHT_M / 2
        if pos[1] < (-th + m) and pt_launch_position < 0:		# Allow the ship to leave the trench after it has launched the torpedoes
            pos[1] = -th + m
        elif pos[1] > (th - m):
            pos[1] = th - m

    def check_for_collisions():
        """Determine whether the ship has collided with any blocks"""
        global dead

        if current_barrier_index < len(barriers):
            barrier = barriers[current_barrier_index]

            # Check if we are in the same Z position as the barrier
            if pos[2] > barrier[0] and pos[2] < barrier[0] + barrier[1]:
                # Calculate the area that our ship occupies
                x1 = pos[0] - cfg.SHIP_WIDTH_M / 2.0
                x2 = x1 + cfg.SHIP_WIDTH_M
                y1 = pos[1] - cfg.SHIP_HEIGHT_M / 2.0
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
                                    set_message("Game Over")
                                    dead = True
