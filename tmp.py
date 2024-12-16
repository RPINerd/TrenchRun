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


def get_distance_to_launch_position():
    return cfg.LAUNCH_POSITION_M - pos[2]


# Indicates whether the ship is 'close' to the launch position.
def is_close_to_launch_position():
    return math.fabs(get_distance_to_launch_position()) < 100.0


# Fire the Proton Torpedoes, if they haven't already been launched.
# They are initially positioned slightly under the ship.
def launch_proton_torpedoes():
    global pt_launch_position

    if pt_launch_position < 0 and is_close_to_launch_position():
        pt_pos.append([pos[0] - cfg.PROTON_TORPEDO_SPAN_M, pos[1] + 1, pos[2]])
        pt_pos.append([pos[0] + cfg.PROTON_TORPEDO_SPAN_M, pos[1] + 1, pos[2]])
        pt_launch_position = pos[2]


# Sets the current message. The message appears for 3 seconds.
def set_message(new_message):
    global message, message_delay, message_tick
    message = new_message
    message_delay = 3
    message_tick = 0


# Projects a 3d point into a 2d canvas coordinate. The 3d coordinates are based on +x -> right, +y -> down +z -> away.
# The origin of the 3d coordinate system is the ship's initial position in the middle of the start of the trench.
def project(point):
    distance = point[2] - pos[2]
    distance = max(cfg.NEAR_PLANE_M, distance)
    x = (point[0] - pos[0]) / (distance + cfg.NEAR_PLANE_M)
    y = (point[1] - pos[1]) / (distance + cfg.NEAR_PLANE_M)
    x *= cfg.SCALE_WIDTH
    y *= cfg.SCALE_HEIGHT
    x += (cfg.CANVAS_WIDTH // 2)
    y += (cfg.CANVAS_HEIGHT // 2)
    return (x, y)


# Displays the Death sequence. If the flashing colours are enabled, then a red rectangle is drawn onto the screen every other frame.
def render_death(canvas):
    global message_tick
    if dead:
        if violent_death and (message_tick % 2 == 0):
            canvas.draw_polygon(((0, 0), (cfg.CANVAS_WIDTH, 0), (cfg.CANVAS_WIDTH, cfg.CANVAS_HEIGHT), (0, cfg.CANVAS_HEIGHT)), 1, "Red", "Red")
        message_tick += 1


# Draws the trench. Firstly, four lines are drawn from the player's z position towards the end of the trench.
# Secondly, a rectangle is drawn at the end of the trench.
# Thirdly, the lines along the wall are drawn.
def render_trench(canvas):
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


# Draws a single barrier.
def render_barrier(canvas, barrier):
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


# Draws all of the visible barriers. The game remembers the first visible barrier (current_barrier_index),
# so that each frame it doesn't need to go through the entire list of barriers to get the first that is visible.
# The visible barriers are always inserted at the front of their own list, which ensures that they are drawn back to front.
def render_barriers(canvas):
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


# Keep the ship within the bounds of the trench.
def constrain_ship():
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


# Determine whether the ship has collided with any blocks
def check_for_collisions():
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


def generate_messages():
    global reached_launch_position

    if not reached_launch_position and is_close_to_launch_position():
        reached_launch_position = True
        set_message("You're all clear kid, now let's\nblow this thing and go home")


# This is the main game processing function.
def render_game(canvas):
    global game_mode

    if not dead:
        move_ship()
        move_torpedoes()
        constrain_ship()
        check_for_collisions()
        generate_messages()
    elif message_delay <= 0:
        game_mode = cfg.MODE_INTRO
    render_death(canvas)
    render_trench(canvas)
    render_barriers(canvas)
    render_exhaust_port(canvas)
    render_torpedoes(canvas)
    render_distance(canvas)
    render_message(canvas)

    if pos[2] > cfg.TRENCH_LENGTH_M + 60:
        game_mode = cfg.MODE_VICTORY if explosion_countdown > 0 else cfg.MODE_INTRO


def render_deathstar(canvas, fill_colour=None):
    centre = cfg.CANVAS_CENTER
    radius = cfg.DEATH_STAR_RADIUS
    if fill_colour == None:
        canvas.draw_circle(centre, radius, cfg.LINE_WIDTH, cfg.DEATH_STAR_COLOUR, "Black")
        canvas.draw_circle((centre[0] - radius * 0.35, centre[1] - radius * 0.5), radius * 0.2, cfg.LINE_WIDTH, cfg.DEATH_STAR_COLOUR)
        canvas.draw_line((centre[0] - radius, centre[1] - 3), (centre[0] + radius, centre[1] - 3), cfg.LINE_WIDTH, cfg.DEATH_STAR_COLOUR)
        canvas.draw_line((centre[0] - radius, centre[1] + 3), (centre[0] + radius, centre[1] + 3), cfg.LINE_WIDTH, cfg.DEATH_STAR_COLOUR)
    else:
        canvas.draw_circle(centre, radius, 1, fill_colour, fill_colour)


def create_particles():
    global particles

    radius = cfg.DEATH_STAR_RADIUS
    particles = []
    for i in range(0, 500):
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
