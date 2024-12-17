"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens import MainMenuScreen
import pygame

import config as cfg


def message(msg: str) -> None:
    print(msg)


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
    centre = cfg.CANVAS_CENTER
    text_centre(surface, "Star Wars", 190, 58, cfg.INTRO_TEXT_COLOUR)
    text_centre(surface, "Press Space to begin your attack run", 340, 24, cfg.INTRO_TEXT_COLOUR)
    text_centre(surface, "Use Cursor Keys to move", 420, 19, cfg.INTRO_TEXT_COLOUR)
    text_centre(surface, "Use Space to launch Proton Torpedo", 440, 19, cfg.INTRO_TEXT_COLOUR)
    text_right(surface, cfg.VERSION, cfg.CANVAS_WIDTH - 16, 14, 14, cfg.INTRO_TEXT_COLOUR)

    x1 = centre[0] - 160
    y1 = centre[1] + (185 if self.game.violent_death else 205)
    x2 = centre[0] + 160
    y2 = centre[1] + 225
    # TODO method unique to codeskulptor, need to implement
    pygame.draw.polygon(surface, "Black", ((x1, y1), (x2, y1), (x2, y2), (x1, y2)), 1)
    text_centre(surface, "Press 'Q' to turn " + ("OFF" if self.game.violent_death else "ON") + " flashing colours", 520, 18, cfg.WARNING_TEXT_COLOUR)
    if self.game.violent_death:
        text_centre(surface, "Note: this game contains flashing colours which are not suitable for sufferers of epilepsy", 500, 18, cfg.WARNING_TEXT_COLOUR)


def text_centre(screen, text, y, size, colour):
    font = pygame.font.Font(cfg.FONT_STYLE, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(center=(cfg.CANVAS_WIDTH // 2, y))
    screen.blit(text_surface, text_rect)


def text_right(screen, text, x, y, size, colour):
    font = pygame.font.Font(cfg.FONT_STYLE, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(topright=(x, y))
    screen.blit(text_surface, text_rect)


def render_death(canvas):
    # Displays the Death sequence. If the flashing colours are enabled, then a red rectangle is drawn onto the screen every other frame.
    global message_tick
    if dead:
        if violent_death and (message_tick % 2 == 0):
            canvas.draw_polygon(((0, 0), (cfg.CANVAS_WIDTH, 0), (cfg.CANVAS_WIDTH, cfg.CANVAS_HEIGHT), (0, cfg.CANVAS_HEIGHT)), 1, "Red", "Red")
        message_tick += 1


def render_trench(canvas):
    # Draws the trench. Firstly, four lines are drawn from the player's z position towards the end of the trench.
    # Secondly, a rectangle is drawn at the end of the trench.
    # Thirdly, the lines along the wall are drawn.
    tw = cfg.TRENCH_WIDTH_M // 2
    th = cfg.TRENCH_HEIGHT_M // 2
    trench = ([-tw, -th], [tw, -th], [tw, th], [-tw, th])
    trench_p = []
    for t in trench:
        near = list(t)
        near.append(pos[2])
        far = list(t)
        far.append(cfg.TRENCH_LENGTH_M)
        near_p = project(near)
        far_p = project(far)
        canvas.draw_line(near_p, far_p, cfg.LINE_WIDTH, cfg.TRENCH_COLOUR)
        trench_p.append(far_p)

    # Draw far wall
    trench_p.append(trench_p[0])
    canvas.draw_polyline(trench_p, cfg.LINE_WIDTH, cfg.TRENCH_COLOUR)

    # Draw vertical walls
    distance = (int(pos[2] + cfg.TRENCH_WALL_INTERVAL_M) // cfg.TRENCH_WALL_INTERVAL_M) * cfg.TRENCH_WALL_INTERVAL_M
    limit = min(pos[2] + cfg.FAR_PLANE_M, cfg.TRENCH_LENGTH_M)
    while distance < limit:
        for side in [-1, 1]:
            p1 = project((side * tw, -th, distance))
            p2 = project((side * tw, th, distance))
            canvas.draw_line(p1, p2, cfg.LINE_WIDTH, cfg.TRENCH_COLOUR)
        distance += cfg.TRENCH_WALL_INTERVAL_M


def render_barrier(canvas, barrier):
    # Draws a single barrier.
    n = barrier[0]            # Barrier Start Position
    f = n + barrier[1]        # Barrier End Position
    m = barrier[2]            # Barrier Block Array
    w = cfg.TRENCH_WIDTH_M / 3.0    # Block Width
    h = cfg.TRENCH_HEIGHT_M / 3.0   # Block Height
    hw = w / 2.0                # Block Half Width
    hh = h / 2.0                # Block Half Height

    # Calculate the colour of the blocks, based on base colour and distance.
    # The barrier's base colour is taken from its start position.
    distance = 1.0 - 0.9 * (n - pos[2]) / cfg.FAR_PLANE_M
    base_colour = cfg.BARRIER_COLOURS[n % len(cfg.BARRIER_COLOURS)]
    colour = "#"
    for component in range(0, 3):
        colour += hex(base_colour[component] * distance)

    i = 0					# Block Index ( 0 to 8 )
    for y in range(-1, 2):
        for x in range(-1, 2):
            if m[i] == 1:  # Test if Block is present
                px = x * w  # Coordinates at the centre of the block
                py = y * h
                cube = (  # Define a tuple containing the coordinates for this cube. They are indexed by BLOCK_VERTEX.
                    (px - hw, py - hh, n),
                    (px + hw, py - hh, n),
                    (px + hw, py + hh, n),
                    (px - hw, py + hh, n),
                    (px - hw, py - hh, f),
                    (px + hw, py - hh, f),
                    (px + hw, py + hh, f),
                    (px - hw, py + hh, f)
                )

                # Project the 3d coordinates into 2d canvas coordinates
                cube_p = []
                for p in cube:
                    cube_p.append(project(p))

                # Draw the lines
                for vi in cfg.BLOCK_VERTEX:
                    canvas.draw_line(cube_p[vi[0]], cube_p[vi[1]], cfg.LINE_WIDTH, colour)
            i += 1


def render_barriers(canvas):
    # Draws all of the visible barriers. The game remembers the first visible barrier (current_barrier_index),
    # so that each frame it doesn't need to go through the entire list of barriers to get the first that is visible.
    # The visible barriers are always inserted at the front of their own list, which ensures that they are drawn back to front.
    global current_barrier_index
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
        render_barrier(canvas, barrier)


def render_exhaust_port(canvas):
    if reached_launch_position:
        y = cfg.TRENCH_HEIGHT_M / 2
        z = cfg.EXHAUST_PORT_POSITION_M
        w = cfg.EXHAUST_PORT_WIDTH_M
        hw = w / 2
        hole = ((-hw, y, z - hw), (hw, y, z - hw), (hw, y, z + hw), (-hw, y, z + hw))
        coords = []
        for p in hole:
            coords.append(project(p))
        coords.append(coords[0])
        canvas.draw_polyline(coords, cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)

        canvas.draw_line(project((-w, y, z)), project((-hw, y, z)), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)
        canvas.draw_line(project((w, y, z)), project((hw, y, z)), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)
        canvas.draw_line(project((0, y, z - w)), project((0, y, z - hw)), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)
        canvas.draw_line(project((0, y, z + w)), project((0, y, z + hw)), cfg.LINE_WIDTH, cfg.EXHAUST_PORT_COLOUR)


def render_torpedo(canvas, pos):
    centre = project(pos)
    edge = project([pos[0] - cfg.PROTON_TORPEDO_RADIUS_M, pos[1], pos[2]])
    radius = centre[0] - edge[0]
    canvas.draw_circle(centre, radius, cfg.LINE_WIDTH, cfg.TORPEDO_COLOUR)


def render_torpedoes(canvas):
    if len(pt_pos) > 0:
        for p in pt_pos:
            render_torpedo(canvas, p)


def render_distance(canvas):
    distance = int(get_distance_to_launch_position())
    if distance > 0:
        distance_str = str(distance)
        while len(distance_str) < 5:
            distance_str = "0" + distance_str
        distance_str += "m"
        draw_text_centre(canvas, distance_str, cfg.CANVAS_HEIGHT - 4, 29, cfg.DISTANCE_COLOUR)


def render_message(canvas):
    global message_delay
    if (message_delay > 0):
        y = cfg.CANVAS_HEIGHT // 2 + 90
        for line in message.split("\n"):
            draw_text_centre(canvas, line, y, 35, "White")
            y += 45
