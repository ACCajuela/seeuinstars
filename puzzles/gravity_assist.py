
import math
from copy import deepcopy
from puzzles.base import BasePuzzle


class GravityAssistPuzzle(BasePuzzle):
    """Two interactive, local gravitational flybys (AU, years, AU/year).

    Each encounter is simulated in the planet-centred inertial frame.
    Transfers between planets are abstracted; this is not an ephemeris model.
    """

    SOLAR_MU = 4.0 * math.pi ** 2

    PLANETS = (
        {
            "name": "Jupiter",
            "mass_solar": 0.0009543,
            "radius_au": 0.0004779,
            "velocity": (0.0, 2.75),
        },
        {
            "name": "Venus",
            "mass_solar": 0.000002447,
            "radius_au": 0.00004045,
            "velocity": (0.0, 7.38),
        },
    )

    INITIAL_VELOCITY = (5.0, 0.0)

    MIN_IMPACT = 3.0
    MAX_IMPACT = 80.0

    # Total available delta-v in AU/year.
    FUEL_CAPACITY = 0.16

    # AU/year², applied only while fuel remains.
    THRUST_ACCELERATION = 120.0

    MAX_STEP = 0.00002

    # Reference maneuver for calibration.
    REFERENCE = (
        (20.0, 1),
        (20.0, 1),
    )

    def __init__(self):
        self.reset()

    # ====================================================
    # Initial state
    # ====================================================

    def reset(self):

        self.completed = False
        self.status = "ready"

        self.encounter_index = 0

        self.vx, self.vy = self.INITIAL_VELOCITY

        self.fuel = self.FUEL_CAPACITY

        self.impact = 20.0
        self.side = -1
        self.steering = 0.0

        self.elapsed = 0.0
        self.encounter_elapsed = 0.0

        self.history = []
        self.trajectory = []

        self.message = (
            "Set the approach and begin the Jupiter flyby."
        )

        self.local = None
        self.closest_radii = float("inf")

        self.start_speed = math.hypot(
            self.vx,
            self.vy,
        )

        return self.get_state()

    # ====================================================
    # Planet selection
    # ====================================================

    def current_planet(self):

        if self.encounter_index >= len(self.PLANETS):
            return None

        return self.PLANETS[self.encounter_index]

    # ====================================================
    # Player actions
    # ====================================================

    def update(self, action):

        kind = action.get("type")

        if kind == "reset":
            return self.reset()

        if kind == "adjust" and self.status == "ready":

            value = float(
                action.get(
                    "approach",
                    action.get("impact", self.impact),
                )
            )

            if math.isfinite(value):
                self.impact = max(
                    self.MIN_IMPACT,
                    min(self.MAX_IMPACT, value),
                )

        elif kind == "set_side" and self.status == "ready":

            self.side = (
                -1
                if float(action.get("side", self.side)) < 0
                else 1
            )

        elif kind == "start" and self.status == "ready":

            self.start_encounter()

        elif kind == "steer" and self.status == "flying":

            value = float(action.get("value", 0.0))

            self.steering = (
                max(-1.0, min(1.0, value))
                if math.isfinite(value)
                else 0.0
            )

        elif kind == "tick" and self.status == "flying":

            dt = float(action.get("dt", 0.0))

            if math.isfinite(dt) and dt > 0:
                self.step(min(dt, 0.03))

        elif kind == "next" and self.status == "between":

            self.status = "ready"

            self.impact = 20.0
            self.side = -1
            self.steering = 0.0

            self.trajectory = []
            self.local = None

            self.message = "Plan the Venus flyby."

        return self.get_state()

    # ====================================================
    # Start encounter
    # ====================================================

    def start_encounter(self):

        planet = self.current_planet()

        pvx, pvy = planet["velocity"]

        ux = self.vx - pvx
        uy = self.vy - pvy

        speed = math.hypot(ux, uy)

        if speed < 1e-9:

            self.status = "failed"

            self.message = (
                "Relative speed is too small."
            )

            return

        ex = ux / speed
        ey = uy / speed

        nx = -ey
        ny = ex

        mu = (
            self.SOLAR_MU
            * planet["mass_solar"]
        )

        radius = planet["radius_au"]

        # Finite initial and final distance.
        # The encounter is not instantaneous.

        span = max(
            100.0 * radius,
            15.0 * mu / (speed * speed),
        )

        x = (
            -span * ex
            + self.side * self.impact * radius * nx
        )

        y = (
            -span * ey
            + self.side * self.impact * radius * ny
        )

        self.local = {
            "x": x,
            "y": y,
            "ux": ux,
            "uy": uy,
            "ex": ex,
            "ey": ey,
            "nx": nx,
            "ny": ny,
            "span": span,
            "mu": mu,
            "radius": radius,
            "initial_velocity": (
                self.vx,
                self.vy,
            ),
            "initial_relative_speed": speed,
            "planet_velocity": (
                pvx,
                pvy,
            ),
        }

        self.trajectory = [
            (
                x / radius,
                y / radius,
            )
        ]

        self.encounter_elapsed = 0.0

        self.closest_radii = (
            math.hypot(x, y) / radius
        )

        self.status = "flying"

        self.message = (
            "Flyby in progress. "
            "Steer gently; fuel is limited."
        )

    # ====================================================
    # Gravity and thrust
    # ====================================================

    def acceleration(
        self,
        x,
        y,
        ux,
        uy,
        steering,
    ):

        r = max(
            math.hypot(x, y),
            1e-12,
        )

        mu = self.local["mu"]

        gx = -mu * x / r**3
        gy = -mu * y / r**3

        # Lateral thrust relative to the
        # instantaneous velocity vector.

        speed = math.hypot(ux, uy)

        if (
            speed > 1e-12
            and self.fuel > 0
            and steering
        ):

            gx += (
                -uy / speed
                * self.THRUST_ACCELERATION
                * steering
            )

            gy += (
                ux / speed
                * self.THRUST_ACCELERATION
                * steering
            )

        return gx, gy

    # ====================================================
    # Continuous simulation
    # ====================================================

    def step(self, dt):

        remaining = dt

        while (
            remaining > 1e-12
            and self.status == "flying"
        ):

            loc = self.local

            x = loc["x"]
            y = loc["y"]

            ux = loc["ux"]
            uy = loc["uy"]

            r = math.hypot(x, y)

            speed = max(
                math.hypot(ux, uy),
                1e-9,
            )

            # Smaller steps near periapsis
            # to prevent tunnelling.

            h = min(
                remaining,
                self.MAX_STEP,
                0.08
                * max(r, loc["radius"])
                / speed,
            )

            thrust = (
                self.steering
                if self.fuel > 0
                else 0.0
            )

            if thrust:

                h = min(
                    h,
                    self.fuel
                    / (
                        self.THRUST_ACCELERATION
                        * abs(thrust)
                    ),
                )

            ax, ay = self.acceleration(
                x,
                y,
                ux,
                uy,
                thrust,
            )

            x2 = (
                x
                + ux * h
                + 0.5 * ax * h * h
            )

            y2 = (
                y
                + uy * h
                + 0.5 * ay * h * h
            )

            ax2, ay2 = self.acceleration(
                x2,
                y2,
                ux + ax * h,
                uy + ay * h,
                thrust,
            )

            ux2 = (
                ux
                + 0.5 * (ax + ax2) * h
            )

            uy2 = (
                uy
                + 0.5 * (ay + ay2) * h
            )

            loc.update(
                x=x2,
                y=y2,
                ux=ux2,
                uy=uy2,
            )

            self.fuel = max(
                0.0,
                self.fuel
                - self.THRUST_ACCELERATION
                * abs(thrust)
                * h,
            )

            self.encounter_elapsed += h
            self.elapsed += h

            remaining -= h

            self.trajectory.append(
                (
                    x2 / loc["radius"],
                    y2 / loc["radius"],
                )
            )

            distance = (
                math.hypot(x2, y2)
                / loc["radius"]
            )

            self.closest_radii = min(
                self.closest_radii,
                distance,
            )

            # Planet collision.

            if distance <= 1.0:

                self.status = "failed"

                self.message = (
                    "The spacecraft collided "
                    "with the planet."
                )

                return

            along = (
                x2 * loc["ex"]
                + y2 * loc["ey"]
            )

            outward = (
                ux2 * loc["ex"]
                + uy2 * loc["ey"]
            )

            # The spacecraft has left
            # the encounter region.

            if (
                along >= loc["span"]
                and outward > 0
            ):

                self.finish_encounter()
                return

            # Safety timeout.

            if self.encounter_elapsed > 0.25:

                self.status = "failed"

                self.message = (
                    "The spacecraft did not leave "
                    "the encounter zone."
                )

                return

    # ====================================================
    # Complete encounter
    # ====================================================

    def finish_encounter(self):

        loc = self.local

        pvx, pvy = loc["planet_velocity"]

        new_vx = loc["ux"] + pvx
        new_vy = loc["uy"] + pvy

        old_vx, old_vy = loc["initial_velocity"]

        old_speed = math.hypot(
            old_vx,
            old_vy,
        )

        new_speed = math.hypot(
            new_vx,
            new_vy,
        )

        self.history.append({
            "planet": self.current_planet()["name"],
            "incoming_speed": old_speed,
            "outgoing_speed": new_speed,
            "speed_change": (
                new_speed - old_speed
            ),
            "closest_radii": self.closest_radii,
            "fuel_remaining": self.fuel,
        })

        self.vx = new_vx
        self.vy = new_vy

        self.encounter_index += 1
        self.steering = 0.0

        if self.encounter_index == len(self.PLANETS):

            self.evaluate()

        else:

            self.status = "between"

            self.message = (
                "Jupiter flyby complete. "
                "Continue to Venus."
            )

    # ====================================================
    # Final evaluation
    # ====================================================

    def evaluate(self):

        # Didactic win condition:
        # both flybys must reduce heliocentric
        # speed by at least 0.5 AU/year.
        #
        # This does not prove a physical
        # Earth interception.

        final_speed = math.hypot(
            self.vx,
            self.vy,
        )

        self.completed = (
            final_speed
            <= self.start_speed - 0.5
        )

        self.status = (
            "success"
            if self.completed
            else "failed"
        )

        if self.completed:

            self.message = (
                "Return transfer prepared! "
                "Ada and Vera head toward Earth."
            )

        else:

            self.message = (
                "Not enough heliocentric speed "
                "was removed. Try another route."
            )

    # ====================================================
    # Validation
    # ====================================================

    def validate(self):
        return self.completed

    # ====================================================
    # State for UI
    # ====================================================

    def get_state(self):

        loc = self.local
        planet = self.current_planet()

        return {
            "status": self.status,
            "completed": self.completed,
            "message": self.message,

            "planet": (
                planet["name"]
                if planet
                else None
            ),

            "encounter_index": (
                self.encounter_index
            ),

            "total_encounters": len(
                self.PLANETS
            ),

            "impact": self.impact,
            "approach": self.impact,
            "side": self.side,

            "steering": self.steering,

            "fuel": self.fuel,
            "fuel_capacity": (
                self.FUEL_CAPACITY
            ),

            "elapsed": self.elapsed,
            "encounter_elapsed": (
                self.encounter_elapsed
            ),

            "x": (
                loc["x"] / loc["radius"]
                if loc
                else None
            ),

            "y": (
                loc["y"] / loc["radius"]
                if loc
                else None
            ),

            "vx": self.vx,
            "vy": self.vy,

            "speed": math.hypot(
                self.vx,
                self.vy,
            ),

            "relative_speed": (
                math.hypot(
                    loc["ux"],
                    loc["uy"],
                )
                if loc
                else None
            ),

            "distance_radii": (
                math.hypot(
                    loc["x"],
                    loc["y"],
                ) / loc["radius"]
                if loc
                else None
            ),

            "closest_radii": (
                self.closest_radii
            ),

            "trajectory": self.trajectory,

            "history": deepcopy(
                self.history
            ),

            "target_speed": (
                self.start_speed - 0.5
            ),
        }
