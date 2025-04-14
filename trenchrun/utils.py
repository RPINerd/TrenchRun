"""
"""
import logging
import math
import random
import time

import config as cfg

logging.basicConfig(level=logging.INFO)


def timeit(func: callable) -> callable:
    """Wrapper to measure the execution time of a function"""
    def wrapper(*args, **kwargs):  #noqa
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def hex(n: int | float) -> str:
    """
    Convert an int to a hex string

    Args:
        n (int): The number to convert (0-255)

    Returns:
        str: The hex string
    """
    n = min(int(n), 255)
    d1 = cfg.HEX_DIGITS[n // 16]
    d2 = cfg.HEX_DIGITS[n % 16]
    return d1 + d2


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


@timeit
def create_barriers() -> list[tuple[float, float, list[int]]]:
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
    limit = cfg.LAUNCH_POSITION - 150
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


@timeit
def create_particles() -> list:
    """
    Create a list of particles that represent the Death Star explosion

    Args:
        None

    Returns:
        list: A list of particle positions
    """
    radius = cfg.DEATH_STAR_RADIUS
    particles: list[list[float, float]] = []
    for _ in range(0, 500):
        a = random.random() * 2 * math.pi
        m = random.random()
        x = math.sin(a) * m * radius
        y = math.cos(a) * m * radius
        particles.append([x, y])

    return particles


# @timeit
def move_particles(particles: list[list[float, float]]) -> list[list[float, float]]:
    """
    Move the particles of the Death Star explosion

    Args:
        particles (list): A list of particle positions

    Returns:
        list: A list of updated particle positions
    """
    c = cfg.CANVAS_CENTER
    for p in particles:
        x = p[0] + c[0]
        y = p[1] + c[1]
        if x >= 0 and x < cfg.CANVAS_WIDTH and y >= 0 and y < cfg.CANVAS_HEIGHT:
            v = 1.1
            p[0] *= v
            p[1] *= v

    return particles


def project(point: tuple[float, float, float], pos: tuple[float, float, float]) -> tuple[float, float]:
    """
    Project a 3D point into a 2D canvas coordinate

    The 3d coordinates are based on +x -> right, +y -> down +z -> away. The origin of the
    3d coordinate system is the ship's initial position in the middle of the start of the trench.

    Args:
        point (tuple): The 3D point to project
        pos (tuple): Current position of the ship

    Returns:
        tuple: The 2D canvas coordinates
    """
    distance = point[2] - pos[2]
    distance = max(cfg.NEAR_PLANE_M, distance)
    x = (point[0] - pos[0]) / (distance + cfg.NEAR_PLANE_M)
    y = (point[1] - pos[1]) / (distance + cfg.NEAR_PLANE_M)
    x *= cfg.SCALE_WIDTH
    y *= cfg.SCALE_HEIGHT
    x += (cfg.CANVAS_WIDTH // 2)
    y += (cfg.CANVAS_HEIGHT // 2)

    return (x, y)
