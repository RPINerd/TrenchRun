""""""
import config as cfg


class Torpedos:

    """Class for the torpedoes."""

    def __init__(self) -> None:
        """Create the torpedoes, initializing all positions and speeds to zero."""
        self.l_torpedo: list[float] = [0.0, 0.0, 0.0]
        self.r_torpedo: list[float] = [0.0, 0.0, 0.0]
        self.launch_position: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.velocity: float = cfg.PROTON_TORPEDO_VELOCITY_MS
        self.range: float = cfg.TORPEDO_RANGE
        self.span: float = cfg.TORPEDO_SPAN
        self.radius: float = cfg.TORPEDO_RADIUS

        self.launched: bool = False
        self.impact: bool = False
        self.bullseye: bool = False

    def __repr__(self) -> str:
        """Return a string representation of the torpedoes."""
        torpstat = """
        Torpedos
        Left Torpedo: {0}
        Right Torpedo: {1}
        Launch Position: {2}
        Velocity: {3}
        Range: {4}
        Span: {5}
        Radius: {6}

        Launched: {7}
        Impact: {8}
        Bullseye: {9}"""
        return torpstat.format(
            self.l_torpedo,
            self.r_torpedo,
            self.launch_position,
            self.velocity,
            self.range,
            self.span,
            self.radius,
            self.launched,
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

        if self.l_torpedo[2] < exhaust_z_limits[0] or self.l_torpedo[2] > exhaust_z_limits[1]:
            return

        # TODO need to check x alignment of torpedos!
        self.bullseye = True

    def fire(self, position: tuple[float, float, float]) -> None:
        """
        Launch the torpedos from the current position of the ship

        Args:
            position (tuple): The position of the ship
        """
        if self.launched:
            return
        self.launched = True
        self.launch_position = (position[0], position[1], position[2])
        self.l_torpedo = [position[0] - self.span / 2, position[1], position[2]]
        self.r_torpedo = [position[0] + self.span / 2, position[1], position[2]]

    def travel(self) -> None:
        """Move the torpedoes forward, if at their range limit also drop them down."""
        if self.impact:
            return

        for torpedo in (self.l_torpedo, self.r_torpedo):
            torpedo[2] += self.velocity / cfg.FPS
            self.range -= self.velocity / cfg.FPS
            if self.range <= 0:
                torpedo[1] -= (self.velocity * 0.3) / cfg.FPS

    def check_impact(self) -> None:
        """Check if the torpedoes have either hit the floor or entered the exhaust port"""
        if self.l_torpedo[1] > -cfg.TRENCH_HEIGHT // 2:
            return

        # self.l_torpedo: list[float] = [0.0, 0.0, 0.0]
        # self.r_torpedo: list[float] = [0.0, 0.0, 0.0]
        self.impact = True
        self._check_ontarget()

    def bullseye_check(self) -> str | None:
        """Check if the torpedoes have hit the exhaust port."""
        if not self.impact:
            return None

        if self.bullseye:
            return "Great shot kid!\nThat was one in a million!"

        return "Negative - It just impacted off the surface.."
