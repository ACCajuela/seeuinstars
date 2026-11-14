
import math

from puzzles.base import BasePuzzle


class SpacetimePuzzle(BasePuzzle):
    """
    ASTRA — Chapter 4: Spacetime Geometry

    Educational, fictional wormhole stabilization puzzle.

    This is NOT a physical simulation of a real,
    traversable wormhole.

    Parameters:
        curvature: 0.0 to 1.0
        throat_radius: 0.0 to 1.0
        stabilization: 0.0 to 1.0

    The player must balance curvature, opening size,
    and hypothetical stabilization.
    """

    def __init__(self):
        super().__init__()
        self.reset()

    # ========================================================
    # Initial state
    # ========================================================

    def reset(self):

        self.curvature = 0.25
        self.throat_radius = 0.30
        self.stabilization = 0.20

        self.completed = False
        self.status = "ready"

        self.stability_score = 0.0
        self.geometry = {}

        self.calculate_geometry()

    # ========================================================
    # Actions
    # ========================================================

    def update(self, action):

        action_type = action.get("type")

        if action_type == "adjust":

            parameter = action.get("parameter")
            value = float(action.get("value", 0.0))

            value = max(0.0, min(1.0, value))

            if parameter == "curvature":
                self.curvature = value

            elif parameter == "throat_radius":
                self.throat_radius = value

            elif parameter == "stabilization":
                self.stabilization = value

            else:
                raise ValueError(
                    f"Unknown parameter: {parameter}"
                )

            self.completed = False
            self.status = "adjusting"

            self.calculate_geometry()

        elif action_type == "submit":

            self.evaluate()

        elif action_type == "reset":

            self.reset()

    # ========================================================
    # Fictional geometry model
    # ========================================================

    def calculate_geometry(self):

        curvature = self.curvature
        radius = self.throat_radius
        stabilization = self.stabilization

        # A simplified visual deformation intensity.
        deformation = (
            curvature * (1.0 - 0.35 * radius)
        )

        # Narrow openings become harder to traverse.
        passage_quality = min(
            1.0,
            radius / 0.45
        )

        # Hypothetical stabilization requirement.
        required_stabilization = (
            0.25
            + 0.45 * curvature
            + 0.15 * radius
        )

        required_stabilization = min(
            1.0,
            required_stabilization
        )

        stabilization_margin = (
            stabilization - required_stabilization
        )

        # Strong curvature helps connect distant regions,
        # but an excessive value increases instability.
        curvature_quality = max(
            0.0,
            1.0 - abs(curvature - 0.65) / 0.65
        )

        # Reward a useful opening size.
        radius_quality = max(
            0.0,
            1.0 - abs(radius - 0.60) / 0.60
        )

        # Score components are intentionally fictional.
        self.stability_score = (
            0.35 * curvature_quality
            + 0.30 * radius_quality
            + 0.35 * stabilization
        )

        self.stability_score = max(
            0.0,
            min(1.0, self.stability_score)
        )

        self.geometry = {
            "deformation": deformation,
            "passage_quality": passage_quality,
            "required_stabilization":
                required_stabilization,
            "stabilization_margin":
                stabilization_margin,
            "curvature_quality":
                curvature_quality,
            "radius_quality":
                radius_quality,
        }

    # ========================================================
    # Validation
    # ========================================================

    def evaluate(self):

        self.calculate_geometry()

        if self.curvature < 0.40:

            self.status = "insufficient_curvature"
            self.completed = False
            return

        if self.curvature > 0.85:

            self.status = "excessive_curvature"
            self.completed = False
            return

        if self.throat_radius < 0.45:

            self.status = "narrow_passage"
            self.completed = False
            return

        if self.geometry["stabilization_margin"] < 0:

            self.status = "unstable"
            self.completed = False
            return

        if self.stability_score < 0.65:

            self.status = "low_stability"
            self.completed = False
            return

        self.status = "success"
        self.completed = True

    def validate(self):
        return self.completed

    # ========================================================
    # Visualization data
    # ========================================================

    def generate_spacetime_grid(
        self,
        size=21,
        extent=2.0
    ):
        """
        Generate a conceptual 3D deformation grid.

        Returns a list of (x, y, z) points.

        The surface resembles a gravity-well
        illustration, not a real spacetime metric.
        """

        if size < 2:
            raise ValueError(
                "Grid size must be at least 2."
            )

        points = []

        deformation = self.geometry["deformation"]

        radius = (
            0.15 + self.throat_radius * 0.85
        )

        for i in range(size):

            x = (
                -extent
                + 2 * extent * i / (size - 1)
            )

            for j in range(size):

                y = (
                    -extent
                    + 2 * extent * j / (size - 1)
                )

                distance = math.hypot(x, y)

                z = (
                    -deformation
                    * math.exp(
                        -(distance ** 2)
                        / (2 * radius ** 2)
                    )
                )

                points.append(
                    (x, y, z)
                )

        return points

    # ========================================================
    # State
    # ========================================================

    def get_state(self):

        return {
            "curvature": self.curvature,
            "throat_radius": self.throat_radius,
            "stabilization": self.stabilization,

            "stability_score":
                self.stability_score,

            "geometry": self.geometry.copy(),

            "completed": self.completed,
            "status": self.status,
        }
