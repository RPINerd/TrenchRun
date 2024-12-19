import time

import config as cfg

# Proton Torpedo Variables
pt_pos = []
pt_launch_position = 0

# Exhaust Port in Range
reached_launch_position = False

# Message
message = ""
message_delay = 0
message_tick = 0

# Stars
stars = []

# Victory
explosion_countdown = 0
particles = []

# Game State
game_mode = cfg.MODE_INTRO
dead = False
violent_death = True

# Actual FPS
last_time = 0
fps = 60


# Sets the current message. The message appears for 3 seconds.
def set_message(new_message):
    global message, message_delay, message_tick
    message = new_message
    message_delay = 3
    message_tick = 0


def generate_messages():
    global reached_launch_position

    if not reached_launch_position and is_close_to_launch_position():
        reached_launch_position = True
        set_message("You're all clear kid, now let's\nblow this thing and go home")


def update_time():
    global last_time, message_delay, fps
    t = time.time()
    if last_time > 0:
        delta = (t - last_time)
        fps = 1.0 / delta
        if message_delay > 0:
            message_delay -= delta
    last_time = t
