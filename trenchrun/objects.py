"""Classes for the player ship and the torpedoes."""
import config as cfg


class PlayerShip:

    """Class for the players craft."""

    def __init__(self) -> None:
        """Create the player ship, initializing all positions and speeds to zero."""
        # Player positions are x, y, z (left/right, up/down, forward/back)
        self.position: list[float] = [0.0, 0.0, 0.0]
        self.velocity: list[float] = [0.0, 0.0, cfg.FORWARD_VELOCITY_MS]
        self.acceleration: list[float] = [0.0, 0.0]

        self.dead: bool = False
        self.torpedos_launched: bool = False
        self.reached_launch_zone: bool = False
        self.movement_factor: float = cfg.FPS

    def travel(self) -> str | None:
        """Move the player ship forward down trench, and then on axis depending on acceleration."""
        # Pull up at the end of the trench
        if self.position[2] >= cfg.EXHAUST_POSITION:
            self.acceleration[1] = -cfg.ACCELERATION_MSS
            if not self.torpedos_launched:
                return "You forgot to launch your torpedoes!"

        # When reaching the launch position, play Solo's line
        if self._in_launch_range() and not self.reached_launch_zone:
            self.reached_launch_zone = True
            return "You're all clear kid, now let's\nblow this thing and go home!"

        # Slow down time when in the launch zone
        if self.reached_launch_zone and not self.torpedos_launched:
            self.movement_factor *= 4

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

        return None

    def steer(self, key_type: int, key: int) -> None:
        """Handle axis movement."""
        if key in cfg.HORIZONTAL_KEYS:
            self.acceleration[0] = cfg.HORIZONTAL_KEYS[key] * key_type
        elif key in cfg.VERTICAL_KEYS:
            self.acceleration[1] = cfg.VERTICAL_KEYS[key] * key_type
        else:
            raise ValueError(f"Invalid key: {key}")

    def _in_launch_range(self) -> bool:
        """Check if the ship is in range to launch torpedoes."""
        return self.position[2] >= cfg.LAUNCH_POSITION and self.position[2] <= cfg.EXHAUST_POSITION
