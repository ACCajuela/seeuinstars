
import math

from puzzles.base import BasePuzzle


class TimeDilationPuzzle(BasePuzzle):
    """
    ASTRA — Chapter 5: Time Dilation

    Special relativity puzzle using the Lorentz factor.

    The spacecraft travels at a constant velocity
    relative to Earth's inertial reference frame.

    Acceleration, gravitational time dilation,
    and turnaround effects are not modeled.

    Units:
        velocity: fraction of light speed (v/c)
        duration: years measured on Earth
        ship_time: years of proper time
    """

    MAX_VELOCITY = 0.99
    MAX_DURATION = 30.0

    TARGET_DIFFERENCE = 4.0
    TARGET_TOLERANCE = 0.15

    def __init__(self):
        super().__init__()
        self.reset()

    # ========================================================
    # Initial state
    # ========================================================

    def reset(self):

        self.velocity = 0.0
        self.duration = 10.0

        self.earth_time = 0.0
        self.ship_time = 0.0
        self.time_difference = 0.0

        self.gamma = 1.0

        self.elapsed_earth_time = 0.0
        self.elapsed_ship_time = 0.0

        self.running = False
        self.completed = False
        self.status = "ready"

        self.calculate()

    # ========================================================
    # Relativity calculations
    # ========================================================

    def calculate(self):

        beta = self.velocity

        self.gamma = (
            1.0 / math.sqrt(1.0 - beta ** 2)
        )

        self.earth_time = self.duration

        self.ship_time = (
            self.duration / self.gamma
        )

        self.time_difference = (
            self.earth_time - self.ship_time
        )

    # ========================================================
    # Actions
    # ========================================================

    def update(self, action):

        action_type = action.get("type")

        if action_type == "adjust":

            if self.running:
                return

            parameter = action.get("parameter")
            value = float(action.get("value", 0.0))

            if parameter == "velocity":

                self.velocity = max(
                    0.0,
                    min(self.MAX_VELOCITY, value)
                )

            elif parameter == "duration":

                self.duration = max(
                    0.0,
                    min(self.MAX_DURATION, value)
                )

            else:
                raise ValueError(
                    f"Unknown parameter: {parameter}"
                )

            self.completed = False
            self.status = "adjusting"

            self.elapsed_earth_time = 0.0
            self.elapsed_ship_time = 0.0

            self.calculate()

        elif action_type == "start":

            self.calculate()

            self.elapsed_earth_time = 0.0
            self.elapsed_ship_time = 0.0

            self.completed = False
            self.running = True
            self.status = "running"

            if self.duration <= 0:
                self.finish()

        elif action_type == "tick":

            if not self.running:
                return

            dt = float(
                action.get("dt", 0.0)
            )

            if dt <= 0:
                return

            remaining = (
                self.duration
                - self.elapsed_earth_time
            )

            step = min(dt, remaining)

            self.elapsed_earth_time += step

            self.elapsed_ship_time += (
                step / self.gamma
            )

            if (
                self.elapsed_earth_time
                >= self.duration - 1e-9
            ):
                self.finish()

        elif action_type == "reset":

            self.reset()

    # ========================================================
    # Validation
    # ========================================================

    def finish(self):

        self.running = False

        difference = (
            self.elapsed_earth_time
            - self.elapsed_ship_time
        )

        error = abs(
            difference
            - self.TARGET_DIFFERENCE
        )

        if error <= self.TARGET_TOLERANCE:

            self.completed = True
            self.status = "success"

        elif difference < self.TARGET_DIFFERENCE:

            self.completed = False
            self.status = "insufficient_dilation"

        else:

            self.completed = False
            self.status = "excessive_dilation"

    def validate(self):
        return self.completed

    # ========================================================
    # State
    # ========================================================

    def get_state(self):

        return {
            "velocity": self.velocity,
            "duration": self.duration,

            "gamma": self.gamma,

            "earth_time": self.earth_time,
            "ship_time": self.ship_time,

            "time_difference": self.time_difference,

            "elapsed_earth_time":
                self.elapsed_earth_time,

            "elapsed_ship_time":
                self.elapsed_ship_time,

            "target_difference":
                self.TARGET_DIFFERENCE,

            "target_tolerance":
                self.TARGET_TOLERANCE,

            "running": self.running,
            "completed": self.completed,
            "status": self.status,
        }
