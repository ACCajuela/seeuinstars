
import math

from puzzles.base import BasePuzzle


class SolarSailPuzzle(BasePuzzle):
    """
    ASTRA — Chapter 7: Solar Sail

    Simplified heliocentric orbital simulation.

    Units:
        Distance: AU
        Time: years
        Velocity: AU/year
        Acceleration: AU/year²

    The solar sail follows an ideal reflective model.
    Sail acceleration is amplified for gameplay.

    Includes a numerically tested reference maneuver
    for reaching Vera's spacecraft.
    """

    SOLAR_MU = 4.0 * math.pi**2

    TIME_STEP = 0.001
    MAX_TIME = 8.0

    START_RADIUS = 2.5

    TARGET_RADIUS = 2.65
    TARGET_ANGLE = 0.18

    SAIL_ACCELERATION_1_AU = 12.0
    MAX_SAIL_ANGLE = 85.0

    DOCKING_DISTANCE = 0.025
    DOCKING_SPEED = 0.12

    COLLISION_DISTANCE = 0.008
    SUN_COLLISION_RADIUS = 0.05

    # Reference solution:
    # Five sail orientations followed by coasting.
    #
    # Each phase lasts 5/6 simulated years.
    # None means the sail is retracted.
    #
    # Approximate rendezvous: 4.76 years.
    REFERENCE_PHASE_DURATION = 5.0 / 6.0

    REFERENCE_ANGLES = (
        -55.018,
        1.582,
        83.209,
        -2.880,
        53.477,
        None
    )

    def __init__(self):
        self.reset()

    # ========================================================
    # Initial conditions
    # ========================================================

    def reset(self):

        self.completed = False
        self.status = "ready"

        self.time = 0.0
        self.launched = False

        self.sail_angle = 0.0
        self.sail_deployed = False

        self.autopilot = False
        self.reference_phase = 0

        # Ada: initial circular orbit.
        r = self.START_RADIUS

        self.x = r
        self.y = 0.0

        self.vx = 0.0
        self.vy = math.sqrt(
            self.SOLAR_MU / r
        )

        # Vera: circular orbit ahead of Ada.
        r = self.TARGET_RADIUS
        angle = self.TARGET_ANGLE

        self.target_x = (
            r * math.cos(angle)
        )

        self.target_y = (
            r * math.sin(angle)
        )

        target_speed = math.sqrt(
            self.SOLAR_MU / r
        )

        self.target_vx = (
            -target_speed * math.sin(angle)
        )

        self.target_vy = (
            target_speed * math.cos(angle)
        )

        self.trajectory = [
            (self.x, self.y)
        ]

        self.target_trajectory = [
            (self.target_x, self.target_y)
        ]

        self.closest_distance = float("inf")
        self.closest_relative_speed = float("inf")

        self.update_relative_state()

        self.closest_distance = self.distance
        self.closest_relative_speed = self.relative_speed

    # ========================================================
    # Player actions
    # ========================================================

    def update(self, action):

        action_type = action.get("type")

        if action_type == "reset":

            self.reset()

        elif action_type == "adjust":

            if self.status in ("ready", "flying"):

                self.autopilot = False

                angle = float(
                    action.get(
                        "angle",
                        self.sail_angle
                    )
                )

                self.sail_angle = max(
                    -self.MAX_SAIL_ANGLE,
                    min(
                        self.MAX_SAIL_ANGLE,
                        angle
                    )
                )

        elif action_type == "deploy":

            if self.status in ("ready", "flying"):

                self.autopilot = False
                self.sail_deployed = True

        elif action_type == "retract":

            if self.status in ("ready", "flying"):

                self.autopilot = False
                self.sail_deployed = False

        elif action_type == "launch":

            if self.status == "ready":

                self.launched = True
                self.status = "flying"

        elif action_type == "autopilot":

            # Reference mode is primarily for calibration.
            # It must start from the original conditions.
            if self.status == "ready":

                self.autopilot = True
                self.reference_phase = 0

                self.apply_reference_phase()

                self.launched = True
                self.status = "flying"

        elif action_type == "tick":

            if self.status == "flying":

                dt = float(
                    action.get(
                        "dt",
                        self.TIME_STEP
                    )
                )

                if math.isfinite(dt) and dt > 0:
                    self.step(dt)

        return self.get_state()

    # ========================================================
    # Reference maneuver
    # ========================================================

    def apply_reference_phase(self):

        phase = min(
            self.reference_phase,
            len(self.REFERENCE_ANGLES) - 1
        )

        angle = self.REFERENCE_ANGLES[phase]

        if angle is None:

            self.sail_deployed = False

        else:

            self.sail_angle = angle
            self.sail_deployed = True

    def update_reference_maneuver(self):

        if not self.autopilot:
            return

        phase = int(
            (
                self.time + 1e-10
            ) / self.REFERENCE_PHASE_DURATION
        )

        phase = min(
            phase,
            len(self.REFERENCE_ANGLES) - 1
        )

        if phase != self.reference_phase:

            self.reference_phase = phase
            self.apply_reference_phase()

    # ========================================================
    # Solar gravity
    # ========================================================

    def gravity_acceleration(self, x, y):

        r = math.hypot(x, y)

        if r <= 0:
            return 0.0, 0.0

        factor = (
            -self.SOLAR_MU / r**3
        )

        return (
            factor * x,
            factor * y
        )

    # ========================================================
    # Solar radiation pressure
    # ========================================================

    def sail_acceleration(self, x, y):

        if not self.sail_deployed:
            return 0.0, 0.0

        r = math.hypot(x, y)

        if r <= 0:
            return 0.0, 0.0

        radial_x = x / r
        radial_y = y / r

        tangent_x = -radial_y
        tangent_y = radial_x

        theta = math.radians(
            self.sail_angle
        )

        cosine = math.cos(theta)
        sine = math.sin(theta)

        normal_x = (
            cosine * radial_x
            + sine * tangent_x
        )

        normal_y = (
            cosine * radial_y
            + sine * tangent_y
        )

        # Ideal reflective sail:
        #
        # a = a0/r² * cos²(theta) * normal
        #
        # The force points away from the Sun
        # and cannot be arbitrarily reversed.

        magnitude = (
            self.SAIL_ACCELERATION_1_AU
            / (r * r)
            * cosine**2
        )

        return (
            magnitude * normal_x,
            magnitude * normal_y
        )

    def ship_acceleration(self, x, y):

        gx, gy = self.gravity_acceleration(
            x, y
        )

        sx, sy = self.sail_acceleration(
            x, y
        )

        return (
            gx + sx,
            gy + sy
        )

    # ========================================================
    # Velocity-Verlet integration
    # ========================================================

    def integrate_body(
        self,
        x,
        y,
        vx,
        vy,
        dt,
        acceleration_function
    ):

        ax, ay = acceleration_function(
            x, y
        )

        next_x = (
            x
            + vx * dt
            + 0.5 * ax * dt**2
        )

        next_y = (
            y
            + vy * dt
            + 0.5 * ay * dt**2
        )

        next_ax, next_ay = (
            acceleration_function(
                next_x,
                next_y
            )
        )

        next_vx = (
            vx
            + 0.5 * (ax + next_ax) * dt
        )

        next_vy = (
            vy
            + 0.5 * (ay + next_ay) * dt
        )

        return (
            next_x,
            next_y,
            next_vx,
            next_vy
        )

    # ========================================================
    # Simulation
    # ========================================================

    def step(self, dt):

        remaining = dt

        while (
            remaining > 1e-12
            and self.status == "flying"
        ):

            self.update_reference_maneuver()

            h = min(
                self.TIME_STEP,
                remaining,
                self.MAX_TIME - self.time
            )

            # Stop exactly at a reference maneuver
            # boundary, so the next sail orientation
            # is applied at the correct time.
            if self.autopilot:

                next_boundary = (
                    (
                        self.reference_phase + 1
                    )
                    * self.REFERENCE_PHASE_DURATION
                )

                if (
                    next_boundary > self.time + 1e-10
                    and self.reference_phase
                    < len(self.REFERENCE_ANGLES) - 1
                ):

                    h = min(
                        h,
                        next_boundary - self.time
                    )

            if h <= 1e-12:
                break

            previous_distance = self.distance

            # Ada: gravity + sail.
            (
                self.x,
                self.y,
                self.vx,
                self.vy
            ) = self.integrate_body(
                self.x,
                self.y,
                self.vx,
                self.vy,
                h,
                self.ship_acceleration
            )

            # Vera: gravity only.
            (
                self.target_x,
                self.target_y,
                self.target_vx,
                self.target_vy
            ) = self.integrate_body(
                self.target_x,
                self.target_y,
                self.target_vx,
                self.target_vy,
                h,
                self.gravity_acceleration
            )

            self.time += h
            remaining -= h

            self.trajectory.append(
                (self.x, self.y)
            )

            self.target_trajectory.append(
                (
                    self.target_x,
                    self.target_y
                )
            )

            self.update_relative_state()

            if self.distance < self.closest_distance:

                self.closest_distance = self.distance

                self.closest_relative_speed = (
                    self.relative_speed
                )

            self.evaluate(previous_distance)

    # ========================================================
    # Relative motion
    # ========================================================

    def update_relative_state(self):

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        dvx = self.target_vx - self.vx
        dvy = self.target_vy - self.vy

        self.distance = math.hypot(
            dx, dy
        )

        self.relative_speed = math.hypot(
            dvx, dvy
        )

    # ========================================================
    # Rendezvous evaluation
    # ========================================================

    def evaluate(self, previous_distance=None):

        radius = math.hypot(
            self.x,
            self.y
        )

        if radius <= self.SUN_COLLISION_RADIUS:

            self.status = "sun_collision"
            return

        # Contact at unsafe relative velocity.
        if (
            self.distance <= self.COLLISION_DISTANCE
            and self.relative_speed > self.DOCKING_SPEED
        ):

            self.status = "collision"
            return

        # Safe proximity and matching velocity.
        if (
            self.distance <= self.DOCKING_DISTANCE
            and self.relative_speed <= self.DOCKING_SPEED
        ):

            self.completed = True
            self.status = "success"
            return

        if self.time >= self.MAX_TIME - 1e-10:

            self.status = "timeout"

    # ========================================================
    # Validation
    # ========================================================

    def validate(self):
        return self.completed

    # ========================================================
    # State for UI
    # ========================================================

    def get_state(self):

        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,

            "target_x": self.target_x,
            "target_y": self.target_y,
            "target_vx": self.target_vx,
            "target_vy": self.target_vy,

            "time": self.time,

            "sail_angle": self.sail_angle,
            "sail_deployed": self.sail_deployed,

            "distance": self.distance,
            "relative_speed": self.relative_speed,

            "closest_distance": self.closest_distance,
            "closest_relative_speed": (
                self.closest_relative_speed
            ),

            "docking_distance": self.DOCKING_DISTANCE,
            "docking_speed": self.DOCKING_SPEED,

            "trajectory": self.trajectory,
            "target_trajectory": self.target_trajectory,

            "autopilot": self.autopilot,
            "reference_phase": self.reference_phase,

            "launched": self.launched,
            "completed": self.completed,
            "status": self.status
        }
