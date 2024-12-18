import math
import random
import time

import config as cfg

# Ship Variables
pos = []
vel = []
acc = []

# Proton Torpedo Variables
pt_pos = []
pt_launch_position = 0

# Exhaust Port in Range
reached_launch_position = False

# Trench Barriers
barriers = []
current_barrier_index = 0

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


def create_particles():
    global particles

    radius = cfg.DEATH_STAR_RADIUS
    particles = []
    for _ in range(0, 500):
        a = random.random() * 2 * math.pi
        m = random.random()
        x = math.sin(a) * m * radius
        y = math.cos(a) * m * radius
        particles.append([x, y])


def render_particles(canvas):
    c = cfg.CANVAS_CENTER
    for p in particles:
        x = p[0] + c[0]
        y = p[1] + c[1]
        canvas.draw_circle((x, y), 1, 1, cfg.PARTICLE_COLOUR)


def move_particles():
    c = cfg.CANVAS_CENTER
    for p in particles:
        x = p[0] + c[0]
        y = p[1] + c[1]
        if x >= 0 and x < cfg.CANVAS_WIDTH and y >= 0 and y < cfg.CANVAS_HEIGHT:
            v = 1.1
            p[0] *= v
            p[1] *= v


def render_victory(canvas):
    global game_mode, explosion_countdown

    render_stars(canvas)
    if explosion_countdown <= 0:
        if explosion_countdown > -160:
            base_colour = (64, 32, 16)
            factor = -explosion_countdown / 10.0
            colour = "#"
            for c in range(0, 3):
                colour += hex(base_colour[c] * factor)
            render_deathstar(canvas, colour)
        elif explosion_countdown == -160:
            create_particles()
        elif explosion_countdown > -400:
            render_particles(canvas)
            move_particles()
        else:
            game_mode = cfg.MODE_INTRO
    else:
        render_deathstar(canvas)
    explosion_countdown -= 1


def update_time():
    global last_time, message_delay, fps
    t = time.time()
    if last_time > 0:
        delta = (t - last_time)
        fps = 1.0 / delta
        if message_delay > 0:
            message_delay -= delta
    last_time = t
