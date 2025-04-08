"""Classes for the player ship and the torpedoes."""
import config as cfg


class Torpedos:

    """Class for the torpedoes."""

    def __init__(self, center_position: list[float]) -> None:
        """Create the torpedoes, initializing all positions and speeds to zero."""
        self.position: list[float] = [center_position[0], center_position[1] + 2, center_position[2]]
        self.launch_position: tuple[float, float, float] = (center_position[0], center_position[1], center_position[2])
        self.velocity: float = cfg.PROTON_TORPEDO_VELOCITY_MS
        self.range: float = cfg.TORPEDO_RANGE
        self.span: float = cfg.TORPEDO_SPAN
        self.radius: float = cfg.TORPEDO_RADIUS

        self.impact: bool = False
        self.bullseye: bool = False

    def __repr__(self) -> str:
        """Return a string representation of the torpedoes."""
        torpstat = """
        Torpedos
        Position: {0}
        Launch Position: {1}
        Velocity: {2}
        Range: {3}
        Span: {4}
        Radius: {5}

        Impact: {6}
        Bullseye: {7}"""
        return torpstat.format(
            self.position,
            self.launch_position,
            self.velocity,
            self.range,
            self.span,
            self.radius,
            self.impact,
            self.bullseye
        )

    def _check_ontarget(self) -> None:
        """Check if the torpedoes have entered the exhaust port."""
        exhaust_radius = cfg.EXHAUST_WIDTH / 2
        exhaust_z_limits = [
            cfg.EXHAUST_POSITION - exhaust_radius + cfg.TORPEDO_RADIUS,
            cfg.EXHAUST_POSITION + exhaust_radius - cfg.TORPEDO_RADIUS
            ]

        if self.position[2] < exhaust_z_limits[0] or self.position[2] > exhaust_z_limits[1]:
            return

        # TODO need to check x alignment of torpedos!
        self.bullseye = True

    def travel(self) -> None:
        """Move the torpedoes forward, if at their range limit also drop them down."""
        self.position[2] += self.velocity / cfg.FPS
        self.range -= self.velocity / cfg.FPS
        if self.range <= 0:
            self.position[1] -= (self.velocity * 3) / cfg.FPS

    def check_impact(self) -> None:
        """Check if the torpedoes have either hit the floor or entered the exhaust port"""
        if self.position[1] > -cfg.TRENCH_HEIGHT // 2:
            return

        self.impact = True
        self._check_ontarget()

    def bullseye_check(self) -> str | None:
        """Check if the torpedoes have hit the exhaust port."""
        if not self.impact:
            return None

        if self.bullseye:
            return "Great shot kid!\nThat was one in a million!"

        return "Negative - It just impacted off the surface.."


class PlayerShip:

    """Class for the players craft."""

    def __init__(self) -> None:
        """
        Create the player ship, initializing all positions and speeds to zero.

        Player position within the trech is a list[x, y, z] (left/right, up/down, forward/back)
        """
        self.position: list[float] = [0.0, 0.0, 0.0]
        self.velocity: list[float] = [0.0, 0.0, cfg.FORWARD_VELOCITY_MS]
        self.acceleration: list[float] = [0.0, 0.0]

        self.wingspan: float = cfg.SHIP_WIDTH_M
        self.height: float = cfg.SHIP_HEIGHT_M

        self.dead: bool = False
        self.torpedos_launched: bool = False
        self.reached_launch_zone: bool = False
        self.movement_factor: float = cfg.FPS

    def __repr__(self) -> str:
        """Return a string representation of the player ship."""
        shipstat = """
        Player Ship
        Position: {0}
        Velocity: {1}
        Acceleration: {2}

        Torpedos Launched: {3}
        Reached Launch Zone: {4}
        Movement Factor: {5}"""
        return shipstat.format(
            self.position,
            self.velocity,
            self.acceleration,
            self.torpedos_launched,
            self.reached_launch_zone,
            self.movement_factor
        )

    def _in_launch_range(self) -> bool:
        """Check if the ship is in range to launch torpedoes."""
        return self.position[2] >= cfg.LAUNCH_POSITION and self.position[2] <= cfg.EXHAUST_POSITION

    def _boundary_enforcement(self) -> None:
        """
        Keep ship within the trench

        The trench origin point is at the center of the screen, so bounds checking
        needs to use the half-width and half-height of the trench
        """
        trench_halfwidth = cfg.TRENCH_WIDTH // 2
        trench_halfheight = cfg.TRENCH_HEIGHT // 2
        ship_halfwidth = self.wingspan // 2
        ship_halfheight = self.height // 2

        # Horizontal bounds checking
        if self.position[0] < (-trench_halfwidth + ship_halfwidth):
            self.position[0] = -trench_halfwidth + ship_halfwidth
        elif self.position[0] > (trench_halfwidth - ship_halfwidth):
            self.position[0] = trench_halfwidth - ship_halfwidth

        # Vertical bounds checking, allowing ship to leave after torpedo launch
        if self.position[1] < (-trench_halfheight + ship_halfheight) and not self.torpedos_launched:
            self.position[1] = -trench_halfheight + ship_halfheight
        elif self.position[1] > (trench_halfheight - ship_halfheight):
            self.position[1] = trench_halfheight - ship_halfheight

    def get_position(self) -> tuple[float, float, float]:
        """Get the x, y, and z coordinates of the ship."""
        return self.position[0], self.position[1], self.position[2]

    def get_xy(self) -> tuple[float, float]:
        """Get the x and y coordinates of the ship."""
        return self.position[0], self.position[1]

    def get_distance(self) -> float:
        """Get the distance from the ship to the launch zone."""
        return cfg.EXHAUST_POSITION - self.position[2]

    def travel(self) -> str | None:
        """Move the player ship forward down trench, and then on axis depending on acceleration."""
        status_message = None
        # Pull up at the end of the trench
        if self.position[2] >= cfg.EXHAUST_POSITION:
            self.acceleration[1] = -cfg.ACCELERATION_MSS
            if not self.torpedos_launched:
                status_message = "You forgot to fire the torpedoes!\nPull up, pull up!"

        # When reaching the launch position, play Solo's line
        if self._in_launch_range() and not self.reached_launch_zone:
            self.reached_launch_zone = True
            self.movement_factor *= 4
            status_message = "You're all clear kid, now let's\nblow this thing and go home!"

        self.position[2] += self.velocity[2] / self.movement_factor

        for axis in range(2):
            self.position[axis] += self.velocity[axis] / self.movement_factor

            # Dampen the velocity if there is no acceleration (acts essentially as friction)
            if self.acceleration[axis] == 0:
                self.velocity[axis] *= cfg.VELOCITY_DAMPEN
                continue

            self.velocity[axis] += self.acceleration[axis] / self.movement_factor

            # Cap the velocity at the maximum
            if self.velocity[axis] > cfg.VELOCITY_MAX_MS:
                self.velocity[axis] = cfg.VELOCITY_MAX_MS
            elif self.velocity[axis] < -cfg.VELOCITY_MAX_MS:
                self.velocity[axis] = -cfg.VELOCITY_MAX_MS

        self._boundary_enforcement()
        return status_message

    def steer(self, key_type: int, key: int) -> None:
        """Handle axis movement."""
        if key in cfg.HORIZONTAL_KEYS:
            self.acceleration[0] = cfg.HORIZONTAL_KEYS[key] * key_type
        elif key in cfg.VERTICAL_KEYS:
            self.acceleration[1] = cfg.VERTICAL_KEYS[key] * key_type
        else:
            raise ValueError(f"Invalid key: {key}")

    def launch_torpedos(self) -> Torpedos | None:
        """"""
        if self.torpedos_launched:
            return None
        if not self._in_launch_range():
            return None
        self.movement_factor = cfg.FPS
        self.torpedos_launched = True
        return Torpedos(self.get_position())
