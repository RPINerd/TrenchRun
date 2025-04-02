"""Functions for rendering specific elements of the game."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens import MainMenuScreen
import config as cfg
import pygame
import utils


def message(surface: pygame.Surface, msg: str) -> None:
    """"""
    print(msg)
    # global message_delay
    # if (message_delay > 0):
    y = cfg.CANVAS_HEIGHT // 2 + 90
    for line in msg.split("\n"):
        text_centre(surface, line, y, 35, "White")
        y += 45


def stars(stars: list, surface: pygame.Surface) -> None:
    """
    Draws stars on the given surface.

    Args:
        stars (list): A list of star positions, where each position is a tuple (x, y).
        surface (pygame.Surface): The surface on which to draw the stars.

    Returns:
        None
    """
    star_colours = []
    for shade in range(8, 16):
        component = 16 * shade
        colour = (component, component, component)
        star_colours.append(colour)

    colour_len = len(star_colours)
    for i, star in enumerate(stars):
        colour = star_colours[i % colour_len]
        pygame.draw.circle(surface, colour, star, 1, 1)


def deathstar(surface: pygame.Surface, fill_colour: tuple[int, int, int] | None = None) -> None:
    """
    Draws the Death Star seen on the intro screen.

    Args:
        surface (pygame.Surface): The surface on which to draw the Death Star.
        fill_colour (tuple, optional): The fill colour for the Death Star. Defaults to None.

    Returns:
        None
    """
    centre = cfg.CANVAS_CENTER
    radius = cfg.DEATH_STAR_RADIUS
    if fill_colour is None:
        position_a = (centre[0] - radius * 0.35, centre[1] - radius * 0.5)
        position_b = (centre[0] - radius, centre[1] - 3)
        position_c = (centre[0] + radius, centre[1] - 3)
        position_d = (centre[0] - radius, centre[1] + 3)
        position_e = (centre[0] + radius, centre[1] + 3)
        pygame.draw.circle(surface, cfg.DEATH_STAR_COLOUR, centre, radius, cfg.LINE_WIDTH)
        pygame.draw.circle(surface, cfg.DEATH_STAR_COLOUR, position_a, radius * 0.2, cfg.LINE_WIDTH)
        pygame.draw.line(surface, cfg.DEATH_STAR_COLOUR, position_b, position_c, cfg.LINE_WIDTH)
        pygame.draw.line(surface, cfg.DEATH_STAR_COLOUR, position_d, position_e, cfg.LINE_WIDTH)
    else:
        pygame.draw.circle(surface, fill_colour, centre, radius)


def intro_text(self: MainMenuScreen, surface: pygame.Surface) -> None:
    """
    Render the intro screen text

    Args:
        surface (pygame.Surface): The surface on which to render the text

    Returns:
        None
    """
    centre = cfg.CANVAS_CENTER
    text_centre(surface, "Star Wars", 190, 58, cfg.INTRO_TEXT_COLOUR)
    text_centre(surface, "Press Space to begin your attack run", 340, 24, cfg.INTRO_TEXT_COLOUR)
    text_centre(surface, "Use Cursor Keys to move", 420, 19, cfg.INTRO_TEXT_COLOUR)
    text_centre(surface, "Use Space to launch Proton Torpedo", 440, 19, cfg.INTRO_TEXT_COLOUR)
    text_right(surface, cfg.VERSION, (cfg.CANVAS_WIDTH - 16, 14), 14, cfg.INTRO_TEXT_COLOUR)

    x1 = centre[0] - 160
    y1 = centre[1] + (185 if self.game.violent_death else 205)
    x2 = centre[0] + 160
    y2 = centre[1] + 225
    pygame.draw.polygon(surface, "Black", ((x1, y1), (x2, y1), (x2, y2), (x1, y2)), 1)
    flash_warning = "Note: this game contains flashing colours which are not suitable for sufferers of epilepsy"
    flash_text = f"Press 'Q' to turn {'OFF' if self.game.violent_death else 'ON'} flashing colours"
    text_centre(surface, flash_text, 520, 18, cfg.WARNING_TEXT_COLOUR)
    if self.game.violent_death:
        text_centre(surface, flash_warning, 500, 18, cfg.WARNING_TEXT_COLOUR)


def text_centre(screen: pygame.Surface, text: str, y: int, size: int, colour: str) -> None:
    """
    Render given text into the centre of the screen

    Args:
        screen (pygame.Surface): The surface on which to render the text
        text (str): The text to render
        y (int): The y-coordinate of the text
        size (int): The font size
        colour (str): The colour of the text

    Returns:
        None
    """
    font = pygame.font.Font(cfg.FONT_STYLE, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(center=(cfg.CANVAS_WIDTH // 2, y))
    screen.blit(text_surface, text_rect)


def text_right(screen: pygame.Surface, text: str, coords: tuple[int, int], size: int, colour: str) -> None:
    """
    Render given text with the top right corner at the given coordinates

    Args:
        screen (pygame.Surface): The surface on which to render the text
        text (str): The text to render
        coords (tuple[int, int]): The (x, y) coordinates of the text
        size (int): The font size
        colour (str): The colour of the text

    Returns:
        None
    """
    font = pygame.font.Font(cfg.FONT_STYLE, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(topright=coords)
    screen.blit(text_surface, text_rect)


def death(surface: pygame.Surface, dead: bool, violent_death: bool) -> None:
    """
    Display death sequence

    If the flashing colours are enabled, then a red rectangle is drawn onto the screen every other frame.

    Args:
        surface (pygame.Surface): The surface on which to draw the death sequence
        dead (bool): Whether the player is dead
        violent_death (bool): Whether to display flashing colours

    Returns:
        None
    """
    # Displays the Death sequence.
    message_tick = pygame.time.get_ticks()
    if dead:
        if violent_death and (message_tick % 2 == 0):
            pygame.draw.polygon(
                surface,
                "Red",
                (
                    (0, 0),
                    (cfg.CANVAS_WIDTH, 0),
                    (cfg.CANVAS_WIDTH, cfg.CANVAS_HEIGHT),
                    (0, cfg.CANVAS_HEIGHT)
                ),
                1)
        message_tick += 1


def trench(surface: pygame.Surface, pos: tuple[float, float, float]) -> None:
    """
    Render the trench

    Four lines are drawn from the player's z position towards the end of the trench.
    Then a rectangle is drawn at the end of the trench.
    Finally, the lines along the wall are drawn.

    Args:
        surface (pygame.Surface): The surface on which to draw the trench
        pos (tuple): The player's position in 3D space

    Returns:
        None
    """
    tw = cfg.TRENCH_WIDTH // 2
    th = cfg.TRENCH_HEIGHT // 2
    trench = ([-tw, -th], [tw, -th], [tw, th], [-tw, th])
    trench_p: list[tuple[float, float]] = []
    for t in trench:
        near = list(t)
        near.append(pos[2])
        far = list(t)
        far.append(cfg.TRENCH_LENGTH)
        near_p = utils.project(near, pos)
        far_p = utils.project(far, pos)
        pygame.draw.line(surface, cfg.TRENCH_COLOUR, near_p, far_p, cfg.LINE_WIDTH)
        trench_p.append(far_p)

    # Draw far wall
    trench_p.append(trench_p[0])
    pygame.draw.lines(surface, cfg.TRENCH_COLOUR, False, trench_p, cfg.LINE_WIDTH)

    # Draw vertical walls
    distance = (int(pos[2] + cfg.WALL_INTERVAL) // cfg.WALL_INTERVAL) * cfg.WALL_INTERVAL
    limit = min(pos[2] + cfg.FAR_PLANE_M, cfg.TRENCH_LENGTH)
    while distance < limit:
        for side in [-1, 1]:
            p1 = utils.project((side * tw, -th, distance), pos)
            p2 = utils.project((side * tw, th, distance), pos)
            pygame.draw.line(surface, cfg.TRENCH_COLOUR, p1, p2, cfg.LINE_WIDTH)
        distance += cfg.WALL_INTERVAL


def render_barrier(surface: pygame.Surface, pos: tuple[float, float, float], barrier: tuple[float, int, list[int]]) -> None:
    """
    Render a single barrier.

    Args:
        surface (pygame.Surface): The surface on which to draw the barrier.
        barrier (tuple): A tuple containing the barrier's start position, length, and block array.

    Returns:
        None
    """
    barrier_start = barrier[0]
    barrier_end = barrier_start + barrier[1]
    block_array = barrier[2]
    block_width = cfg.TRENCH_WIDTH / 3.0
    block_height = cfg.TRENCH_HEIGHT / 3.0
    block_half_width = block_width / 2.0
    block_half_height = block_height / 2.0

    # Calculate the colour of the blocks, based on base colour and distance.
    # The barrier's base colour is taken from its start position.
    distance = 1.0 - 0.9 * (barrier_start - pos[2]) / cfg.FAR_PLANE_M
    base_colour = cfg.BARRIER_COLOURS[int(barrier_start % len(cfg.BARRIER_COLOURS))]
    colour = "#"
    for component in range(0, 3):
        colour += utils.hex(base_colour[component] * distance)

    i = 0  # Block Index ( 0 to 8 )
    for y in range(-1, 2):
        for x in range(-1, 2):
            if block_array[i] == 0:
                i += 1
                continue
            px = x * block_width  # Coordinates at the centre of the block
            py = y * block_height
            # Define a tuple containing the coordinates for this cube. They are indexed by BLOCK_VERTEX.
            cube = (
                (px - block_half_width, py - block_half_height, barrier_start),
                (px + block_half_width, py - block_half_height, barrier_start),
                (px + block_half_width, py + block_half_height, barrier_start),
                (px - block_half_width, py + block_half_height, barrier_start),
                (px - block_half_width, py - block_half_height, barrier_end),
                (px + block_half_width, py - block_half_height, barrier_end),
                (px + block_half_width, py + block_half_height, barrier_end),
                (px - block_half_width, py + block_half_height, barrier_end)
            )

            # Project the 3d coordinates into 2d canvas coordinates
            cube_p = []
            for p in cube:
                cube_p.append(utils.project(p, pos))

            # Draw the lines
            for vi in cfg.BLOCK_VERTEX:
                pygame.draw.line(surface, colour, cube_p[vi[0]], cube_p[vi[1]], cfg.LINE_WIDTH)
            i += 1


def barriers(
    surface: pygame.Surface,
    barriers: list[tuple[float, int, list[int]]],
    current_barrier_index: int,
    pos: tuple[float, float, float]) -> None:
    """
    Draws all of the visible barriers.

    The game remembers the first visible barrier (current_barrier_index), so that each frame it
    doesn't need to go through the entire list of barriers to get the first that is visible.
    The visible barriers are always inserted at the front of their own list, which ensures that they are drawn back to front.

    Args:
        surface (pygame.Surface): The surface on which to draw the barriers.
        barriers (list): A list of all the barriers in the game.
        current_barrier_index (int): The index of the first visible barrier.
        pos (tuple): The player's position in 3D space.

    Returns:
        None
    """
    visible_barriers = []

    index = current_barrier_index
    while index < len(barriers):
        barrier = barriers[index]
        index += 1
        visible = (barrier[0] + barrier[1] - pos[2]) > cfg.NEAR_PLANE_M
        visible = visible and (barrier[0] - pos[2] < cfg.FAR_PLANE_M)
        if visible:
            visible_barriers.insert(0, barrier)
        elif pos[2] > barrier[0]:
            current_barrier_index = index
        else:
            break

    for barrier in visible_barriers:
        render_barrier(surface, pos, barrier)


def exhaust_port(surface: pygame.Surface, pos: tuple[float, float, float]) -> None:
    """
    Render the exhaust port

    Args:
        surface (pygame.Surface): The surface on which to draw the exhaust port
        pos (tuple): The player's position in 3D space

    Returns:
        None
    """
    y = cfg.TRENCH_HEIGHT / 2
    z = cfg.EXHAUST_POSITION
    w = cfg.EXHAUST_WIDTH
    hw = w / 2
    hole = ((-hw, y, z - hw), (hw, y, z - hw), (hw, y, z + hw), (-hw, y, z + hw))
    coords = []
    for p in hole:
        coords.append(utils.project(p, pos))
    coords.append(coords[0])
    surface.draw_polyline(coords, cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)

    surface.draw_line(utils.project((-w, y, z), pos), utils.project((-hw, y, z), pos), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)
    surface.draw_line(utils.project((w, y, z), pos), utils.project((hw, y, z), pos), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)
    surface.draw_line(utils.project((0, y, z - w), pos), utils.project((0, y, z - hw), pos), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)
    surface.draw_line(utils.project((0, y, z + w), pos), utils.project((0, y, z + hw), pos), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)


def torpedoes(surface: pygame.Surface, pt_pos: list[tuple[float, float, float]]) -> None:
    """
    Render the proton torpedoes

    The torpedoes are drawn as circles on the screen, with their size determined by the distance from the player.

    Args:
        surface (pygame.Surface): The surface on which to draw the torpedoes
        pt_pos (list): A list of positions of the torpedoes in 3D space

    Returns:
        None
    """
    def render_torpedo(surface: pygame.Surface, pos: tuple[float, float, float]) -> None:
        """
        Render an individual torpedo

        Args:
            surface (pygame.Surface): The surface on which to draw the torpedo
            pos (tuple): The position of the torpedo in 3D space

        Returns:
            None
        """
        centre = utils.project(pos)
        edge = utils.project([pos[0] - cfg.TORPEDO_RADIUS, pos[1], pos[2]])
        radius = centre[0] - edge[0]
        pygame.draw.circle(surface, cfg.TORPEDO_COLOUR, centre, radius, cfg.LINE_WIDTH)

    if len(pt_pos) > 0:
        for p in pt_pos:
            render_torpedo(surface, p)


def distance(surface: pygame.Surface, distance: int | float) -> None:
    """"""
    if distance > 0:
        distance_str = str(distance)
        while len(distance_str) < 5:
            distance_str = "0" + distance_str
        distance_str += "m"
        text_centre(surface, distance_str, cfg.CANVAS_HEIGHT - 4, 24, cfg.DISTANCE_COLOUR)


def particles(surface: pygame.Surface, particles: list[list[float, float]]) -> None:
    """"""
    c = cfg.CANVAS_CENTER
    for p in particles:
        x = p[0] + c[0]
        y = p[1] + c[1]
        pygame.draw.circle(surface, cfg.PARTICLE_COLOUR, (x, y), 1, 1)
