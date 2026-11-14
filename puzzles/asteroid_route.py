
import math

from puzzles.base import BasePuzzle


class AsteroidRoutePuzzle(BasePuzzle):
    """
    Orbital transfer puzzle.

    Units:
        Distance: astronomical units (AU)
        Time: years
        Velocity: AU/year

    The spacecraft begins in a circular orbit at
    Mars' orbital radius.

    A launch represents an instantaneous tangential
    orbital maneuver.

    The Sun is the central gravitational body.
    """

    SOLAR_MU = 4 * math.pi ** 2

    START_RADIUS = 1.524
    TARGET_RADIUS = 2.5
    TARGET_TOLERANCE = 0.1

    TIME_STEP = 0.001
    MAX_TIME = 5.0

    SUN_COLLISION_RADIUS = 0.01

    def __init__(self):
        super().__init__()
        self.reset()

    # ========================================================
    # Initial conditions
    # ========================================================

    def reset(self):

        self.x = self.START_RADIUS
        self.y = 0.0

        self.circular_speed = math.sqrt(
            self.SOLAR_MU / self.START_RADIUS
        )

        self.vx = 0.0
        self.vy = self.circular_speed

        self.time = 0.0

        self.max_radius = self.START_RADIUS
        self.min_radius = self.START_RADIUS

        self.trajectory = [
            (self.x, self.y)
        ]

        self.launched = False
        self.completed = False
        self.status = "ready"

        self.previous_radial_velocity = 0.0

    # ========================================================
    # Actions
    # ========================================================

    def update(self, action):

        action_type = action.get("type")

        if action_type == "launch":

            if self.launched:
                return

            velocity = float(
                action.get(
                    "velocity",
                    self.circular_speed
                )
            )

            if velocity < 0:
                raise ValueError(
                    "Velocity cannot be negative."
                )

            # The maneuver changes tangential velocity.
            # The spacecraft already has orbital motion.
            self.vx = 0.0
            self.vy = velocity

            self.launched = True
            self.status = "flying"

            self.previous_radial_velocity = 0.0

        elif action_type == "tick":

            if not self.launched:
                return

            if self.status != "flying":
                return

            dt = float(
                action.get(
                    "dt",
                    self.TIME_STEP
                )
            )

            if dt <= 0:
                return

            self.integrate(dt)

        elif action_type == "reset":

            self.reset()

    # ========================================================
    # Gravity
    # ========================================================

    def acceleration(self, x, y):

        radius_squared = x * x + y * y

        if radius_squared == 0:
            return 0.0, 0.0

        radius = math.sqrt(radius_squared)

        factor = (
            -self.SOLAR_MU
            / (radius_squared * radius)
        )

        return factor * x, factor * y

    # ========================================================
    # Numerical integration
    # ========================================================

    def integrate(self, dt):

        ax, ay = self.acceleration(
            self.x,
            self.y
        )

        # Velocity-Verlet position update.
        new_x = (
            self.x
            + self.vx * dt
            + 0.5 * ax * dt * dt
        )

        new_y = (
            self.y
            + self.vy * dt
            + 0.5 * ay * dt * dt
        )

        new_ax, new_ay = self.acceleration(
            new_x,
            new_y
        )

        # Velocity-Verlet velocity update.
        new_vx = (
            self.vx
            + 0.5 * (ax + new_ax) * dt
        )

        new_vy = (
            self.vy
            + 0.5 * (ay + new_ay) * dt
        )

        self.x = new_x
        self.y = new_y

        self.vx = new_vx
        self.vy = new_vy

        self.time += dt

        radius = math.hypot(
            self.x,
            self.y
        )

        self.max_radius = max(
            self.max_radius,
            radius
        )

        self.min_radius = min(
            self.min_radius,
            radius
        )

        self.trajectory.append(
            (self.x, self.y)
        )

        # ----------------------------------------------------
        # Collision
        # ----------------------------------------------------

        if radius <= self.SUN_COLLISION_RADIUS:

            self.status = "collision"
            self.completed = False
            return

        # ----------------------------------------------------
        # Escape
        # ----------------------------------------------------

        speed_squared = (
            self.vx ** 2
            + self.vy ** 2
        )

        specific_energy = (
            speed_squared / 2
            - self.SOLAR_MU / radius
        )

        if specific_energy >= 0:

            self.status = "escape"
            self.completed = False
            return

        # ----------------------------------------------------
        # Detect first aphelion
        # ----------------------------------------------------

        radial_velocity = (
            self.x * self.vx
            + self.y * self.vy
        ) / radius

        if (
            self.previous_radial_velocity > 0
            and radial_velocity <= 0
        ):

            self.evaluate_transfer()
            return

        self.previous_radial_velocity = (
            radial_velocity
        )

        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------

        if self.time >= self.MAX_TIME:

            self.status = "timeout"
            self.completed = False

    # ========================================================
    # Transfer validation
    # ========================================================

    def evaluate_transfer(self):

        difference = abs(
            self.max_radius
            - self.TARGET_RADIUS
        )

        if difference <= self.TARGET_TOLERANCE:

            self.status = "success"
            self.completed = True

        elif self.max_radius < self.TARGET_RADIUS:

            self.status = "too_short"
            self.completed = False

        else:

            self.status = "too_far"
            self.completed = False

    def validate(self):
        return self.completed

    # ========================================================
    # State
    # ========================================================

    def get_state(self):

        radius = math.hypot(
            self.x,
            self.y
        )

        return {
            "x": self.x,
            "y": self.y,

            "vx": self.vx,
            "vy": self.vy,

            "time": self.time,

            "radius": radius,

            "max_radius": self.max_radius,
            "min_radius": self.min_radius,

            "start_radius": self.START_RADIUS,
            "target_radius": self.TARGET_RADIUS,
            "target_tolerance": self.TARGET_TOLERANCE,

            "circular_speed": self.circular_speed,

            "trajectory": self.trajectory.copy(),

            "launched": self.launched,
            "completed": self.completed,
            "status": self.status,
        }
