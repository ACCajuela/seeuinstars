
import math

from puzzles.base import BasePuzzle


class MarsGravityPuzzle(BasePuzzle):
    # Physical constants
    MARS_GRAVITY = 3.71
    EARTH_GRAVITY = 9.81

    # Simulation settings
    TIME_STEP = 0.02
    MAX_TIME = 30.0

    # Rover patrol area (meters)
    ROVER_MIN_X = 15.0
    ROVER_MAX_X = 25.0
    ROVER_SPEED = 1.0
    ROVER_WIDTH = 4.0

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        # Ada's position and velocity
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0

        self.time = 0.0
        self.flight_time = 0.0

        self.launched = False
        self.completed = False
        self.status = "ready"

        self.gravity = self.MARS_GRAVITY
        self.max_height = 0.0

        # Rover position represents its center.
        self.rover_x = 20.0
        self.rover_direction = 1

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------

    def update(self, action):
        action_type = action.get("type")

        if action_type == "launch":
            if self.status != "ready":
                return

            velocity = float(action.get("velocity", 0))
            angle = float(action.get("angle", 45))

            if not math.isfinite(velocity):
                raise ValueError("Velocity must be finite.")

            if not 0 <= velocity <= 30:
                raise ValueError(
                    "Velocity must be between 0 and 30 m/s."
                )

            if not math.isfinite(angle):
                raise ValueError("Angle must be finite.")

            if not 0 <= angle <= 90:
                raise ValueError(
                    "Angle must be between 0 and 90 degrees."
                )

            angle_rad = math.radians(angle)

            self.vx = velocity * math.cos(angle_rad)
            self.vy = velocity * math.sin(angle_rad)

            self.launched = True
            self.status = "flying"

        elif action_type == "tick":
            dt = float(action.get("dt", self.TIME_STEP))

            if not math.isfinite(dt):
                raise ValueError("Time step must be finite.")

            if not 0 < dt <= self.TIME_STEP:
                raise ValueError(
                    "Invalid simulation time step."
                )

            self.step(dt)

    # --------------------------------------------------------
    # Rover movement
    # --------------------------------------------------------

    def move_rover(self, dt):
        remaining = self.ROVER_SPEED * dt

        while remaining > 0:
            boundary = (
                self.ROVER_MAX_X
                if self.rover_direction > 0
                else self.ROVER_MIN_X
            )

            distance = abs(boundary - self.rover_x)

            if remaining < distance:
                self.rover_x += (
                    self.rover_direction * remaining
                )
                break

            self.rover_x = boundary
            remaining -= distance
            self.rover_direction *= -1

    # --------------------------------------------------------
    # Physics simulation
    # --------------------------------------------------------

    def step(self, dt):
        if self.status not in ("ready", "flying"):
            return

        # Rover moves even before Ada jumps.
        self.move_rover(dt)
        self.time += dt

        if not self.launched:
            return

        # Constant-acceleration ballistic motion.
        self.x += self.vx * dt
        self.y += (
            self.vy * dt
            - 0.5 * self.gravity * dt**2
        )

        self.vy -= self.gravity * dt
        self.flight_time += dt

        self.max_height = max(
            self.max_height,
            self.y
        )

        # Landing detection
        if self.y <= 0:
            self.y = 0.0
            self.launched = False

            half_width = self.ROVER_WIDTH / 2

            rover_left = self.rover_x - half_width
            rover_right = self.rover_x + half_width

            if rover_left <= self.x <= rover_right:
                self.status = "success"
                self.completed = True

            elif self.x < rover_left:
                self.status = "too_short"

            else:
                self.status = "too_far"

        elif self.flight_time >= self.MAX_TIME:
            self.launched = False
            self.status = "timeout"

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def validate(self):
        return self.completed

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "time": self.time,
            "flight_time": self.flight_time,
            "gravity": self.gravity,
            "max_height": self.max_height,

            "rover_x": self.rover_x,
            "rover_direction": self.rover_direction,
            "rover_speed": self.ROVER_SPEED,
            "rover_width": self.ROVER_WIDTH,
            "rover_min_x": self.ROVER_MIN_X,
            "rover_max_x": self.ROVER_MAX_X,

            "launched": self.launched,
            "completed": self.completed,
            "status": self.status,
        }
