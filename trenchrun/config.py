"""
Hardcoded configuration settings for the game.

All distances or sizes are in meters unless otherwise specified.
"""
import configparser
from pathlib import Path

# Load settings from the ini file
config_parser = configparser.ConfigParser()
ini_file = Path(__file__).parent / "settings.ini"
try:
    config_parser.read(ini_file)
except FileNotFoundError:
    raise FileNotFoundError(f"Settings ini file not found! Please check the file path: {ini_file}")
except configparser.Error as e:
    raise configparser.Error(f"Error reading the ini file: {e}")


def get_setting(section: str, key: str, fallback: str) -> str:
    """
    Helper function to get values from the ini file with a fallback

    Args:
        section (str): The section of the ini file
        key (str): The key in the section
        fallback (str): The fallback value if the key is not found
    Returns:
        str: The value from the ini file or the fallback value
    """
    return config_parser.get(section, key, fallback=fallback)


VERSION = "1.6_dev"


# Window Settings
FPS = int(get_setting("Game", "FPS", "60"))
CANVAS_WIDTH = int(get_setting("Display", "ResolutionX", "1024"))
CANVAS_HEIGHT = int(get_setting("Display", "ResolutionY", "768"))
CANVAS_CENTER_X = CANVAS_WIDTH // 2
CANVAS_CENTER_Y = CANVAS_HEIGHT // 2
CANVAS_CENTER = (CANVAS_CENTER_X, CANVAS_CENTER_Y)
FONT_STYLE = "font/DeathStar.ttf"

# Trench Settings
TRENCH_LENGTH = int(get_setting("Game", "TrenchLength", "1500"))
TRENCH_WIDTH = 10
TRENCH_HEIGHT = 10
WALL_INTERVAL = 20
EXHAUST_POSITION = TRENCH_LENGTH - 100
EXHAUST_WIDTH = TRENCH_WIDTH / 3.0

# Torpedo Settings
TORPEDO_RANGE = 100
TORPEDO_RADIUS = 0.25
TORPEDO_SPAN = 0.7
LAUNCH_POSITION = EXHAUST_POSITION - TORPEDO_RANGE

# Parameters for rendering
DEATH_STAR_RADIUS = CANVAS_HEIGHT * 0.4
LINE_WIDTH = 2
NEAR_PLANE_M = 0.1
FAR_PLANE_M = 180.0
SCALE_WIDTH = CANVAS_WIDTH / 2
SCALE_HEIGHT = CANVAS_HEIGHT / 2


# Ship Size (dictates collision detection)
SHIP_WIDTH_M = 1.6
SHIP_HEIGHT_M = 0.8

# Speeds and feeds
FORWARD_VELOCITY_MS = 60.0
PROTON_TORPEDO_VELOCITY_MS = FORWARD_VELOCITY_MS * 1.1
VELOCITY_MAX_MS = 15.0
VELOCITY_DAMPEN = 0.85
ACCELERATION_MSS = 60.0

# Colors
DEATH_STAR_COLOUR = (170, 170, 170)
TRENCH_COLOUR = (221, 221, 221)
TORPEDO_COLOUR = (20, 40, 255)
DISTANCE_COLOUR = (190, 10, 10)
EXHAUST_PORT_COLOUR = (110, 110, 140)
INTRO_TEXT_COLOUR = (245, 188, 0)
WARNING_TEXT_COLOUR = (190, 10, 10)
PARTICLE_COLOUR = (255, 255, 255)
BARRIER_COLOURS = ((240, 0, 0), (240, 185, 0), (0, 240, 0), (240, 240, 0), (0, 240, 240), (240, 0, 240))

BLOCK_VERTEX = ((0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 5), (2, 6), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4), (0, 2), (1, 3))

HEX_DIGITS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
