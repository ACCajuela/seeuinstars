
import random

from puzzles.base import BasePuzzle


class CometSpectrumPuzzle(BasePuzzle):
    """
    Educational spectroscopy puzzle.

    Each new comet receives a random composition
    containing 1 to 3 substances.

    Wavelengths are in nanometers (nm).

    IMPORTANT:
    These are fictional educational signatures,
    not experimentally measured spectra.
    """

    SUBSTANCES = {
        "water": {
            "name": "Water vapor",
            "lines": [410, 530, 660],
        },
        "carbon_monoxide": {
            "name": "Carbon monoxide",
            "lines": [445, 575, 705],
        },
        "carbon_dioxide": {
            "name": "Carbon dioxide",
            "lines": [480, 610, 740],
        },
        "sodium": {
            "name": "Sodium",
            "lines": [520, 590, 680],
        },
        "cyanogen": {
            "name": "Cyanogen",
            "lines": [390, 515, 635],
        },
    }

    TOLERANCE = 5
    MEASUREMENT_NOISE = 2

    MIN_SUBSTANCES = 1
    MAX_SUBSTANCES = 3

    def __init__(self, seed=None):
        super().__init__()

        self.rng = random.Random(seed)

        self.reset()

    # --------------------------------------------------------
    # New random comet
    # --------------------------------------------------------

    def reset(self):
        self.selected_substances = set()

        self.completed = False
        self.status = "ready"

        substance_ids = list(self.SUBSTANCES.keys())

        quantity = self.rng.randint(
            self.MIN_SUBSTANCES,
            self.MAX_SUBSTANCES
        )

        self.correct_substances = set(
            self.rng.sample(
                substance_ids,
                quantity
            )
        )

        self.observed_lines = sorted(
            line + self.rng.randint(
                -self.MEASUREMENT_NOISE,
                self.MEASUREMENT_NOISE
            )
            for substance_id in self.correct_substances
            for line in self.SUBSTANCES[substance_id]["lines"]
        )

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------

    def update(self, action):
        action_type = action.get("type")

        if action_type == "toggle":
            substance_id = action.get("substance")

            if substance_id not in self.SUBSTANCES:
                raise ValueError(
                    f"Unknown substance: {substance_id}"
                )

            if substance_id in self.selected_substances:
                self.selected_substances.remove(
                    substance_id
                )
            else:
                self.selected_substances.add(
                    substance_id
                )

            self.completed = False
            self.status = "ready"

        elif action_type == "submit":
            self.check_answer()

        elif action_type == "reset":
            self.reset()

    # --------------------------------------------------------
    # Spectral comparison
    # --------------------------------------------------------

    def get_selected_lines(self):
        return sorted(
            line
            for substance_id in self.selected_substances
            for line in self.SUBSTANCES[substance_id]["lines"]
        )

    def compare_spectra(self):
        observed = self.observed_lines
        selected = self.get_selected_lines()

        # Match each observed line to at most one
        # selected reference line.
        unmatched_selected = selected.copy()
        matched = 0

        for observed_line in observed:
            best_index = None
            best_difference = self.TOLERANCE + 1

            for index, selected_line in enumerate(
                unmatched_selected
            ):
                difference = abs(
                    observed_line - selected_line
                )

                if difference < best_difference:
                    if difference <= self.TOLERANCE:
                        best_index = index
                        best_difference = difference

            if best_index is not None:
                matched += 1
                unmatched_selected.pop(best_index)

        return {
            "matched": matched,
            "missing": len(observed) - matched,
            "extra": len(selected) - matched,
            "total_observed": len(observed),
            "total_selected": len(selected),
        }

    # --------------------------------------------------------
    # Answer validation
    # --------------------------------------------------------

    def check_answer(self):
        comparison = self.compare_spectra()

        if (
            comparison["missing"] == 0
            and comparison["extra"] == 0
            and self.selected_substances
            == self.correct_substances
        ):
            self.completed = True
            self.status = "success"

        elif comparison["missing"] > 0:
            self.completed = False
            self.status = "missing_lines"

        elif comparison["extra"] > 0:
            self.completed = False
            self.status = "extra_lines"

        else:
            self.completed = False
            self.status = "incorrect"

    def validate(self):
        return self.completed

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    def get_state(self):
        comparison = self.compare_spectra()

        return {
            "observed_lines": self.observed_lines.copy(),

            "substances": {
                substance_id: {
                    "name": data["name"],
                    "lines": data["lines"].copy(),
                }
                for substance_id, data
                in self.SUBSTANCES.items()
            },

            "selected_substances": sorted(
                self.selected_substances
            ),

            "selected_lines": self.get_selected_lines(),

            "comparison": comparison,

            "tolerance": self.TOLERANCE,

            "completed": self.completed,
            "status": self.status,
        }
