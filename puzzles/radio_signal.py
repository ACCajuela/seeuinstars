
import math

from puzzles.base import BasePuzzle


class RadioSignalPuzzle(BasePuzzle):
    """
    ASTRA — Chapter 6: Radio Communication

    Educational puzzle based on the longitudinal
    relativistic Doppler effect and light travel time.

    Simplifications:
        - Constant relative radial velocity.
        - Flat spacetime.
        - No gravitational redshift.
        - No interference or signal attenuation.
        - Distance is measured at emission in the
          receiver's inertial reference frame.

    Positive beta: source moving away.
    Negative beta: source approaching.

    Units:
        Frequency: MHz
        Distance: light-minutes
        Time: minutes
    """

    LIGHT_SPEED = 1.0

    EMITTED_FREQUENCY = 150.0

    SOURCE_VELOCITY = 0.30

    INITIAL_DISTANCE = 12.0

    FREQUENCY_TOLERANCE = 0.5

    MIN_FREQUENCY = 50.0
    MAX_FREQUENCY = 250.0

    def __init__(self):
        super().__init__()
        self.reset()

    # ========================================================
    # Initial state
    # ========================================================

    def reset(self):

        self.emitted_frequency = (
            self.EMITTED_FREQUENCY
        )

        self.source_velocity = (
            self.SOURCE_VELOCITY
        )

        self.distance = (
            self.INITIAL_DISTANCE
        )

        self.tuned_frequency = 150.0

        self.received_frequency = 0.0
        self.signal_delay = 0.0

        self.signal_progress = 0.0
        self.elapsed_time = 0.0

        self.signal_arrived = False
        self.running = False
        self.completed = False

        self.status = "ready"

        self.calculate_signal()

    # ========================================================
    # Physics
    # ========================================================

    def calculate_signal(self):

        beta = self.source_velocity

        if not -1.0 < beta < 1.0:
            raise ValueError(
                "Relative velocity must be below c."
            )

        doppler_factor = math.sqrt(
            (1.0 - beta)
            / (1.0 + beta)
        )

        self.received_frequency = (
            self.emitted_frequency
            * doppler_factor
        )

        # For a receding or approaching source,
        # the emitted signal still propagates at c.
        #
        # Here distance is the source-receiver
        # separation at the emission event.
        self.signal_delay = (
            self.distance
            / self.LIGHT_SPEED
        )

    # ========================================================
    # Actions
    # ========================================================

    def update(self, action):

        action_type = action.get("type")

        if action_type == "tune":

            frequency = float(
                action.get(
                    "frequency",
                    self.tuned_frequency
                )
            )

            self.tuned_frequency = max(
                self.MIN_FREQUENCY,
                min(
                    self.MAX_FREQUENCY,
                    frequency
                )
            )

            if not self.completed:
                self.status = "tuning"

        elif action_type == "start":

            self.calculate_signal()

            self.elapsed_time = 0.0
            self.signal_progress = 0.0

            self.signal_arrived = False
            self.completed = False
            self.running = True

            self.status = "transmitting"

        elif action_type == "tick":

            if not self.running:
                return

            dt = float(
                action.get("dt", 0.0)
            )

            if dt <= 0:
                return

            self.elapsed_time += dt

            self.signal_progress = min(
                1.0,
                self.elapsed_time
                / self.signal_delay
            )

            if self.elapsed_time >= self.signal_delay:

                self.elapsed_time = self.signal_delay
                self.signal_progress = 1.0

                self.signal_arrived = True
                self.running = False

                self.evaluate()

        elif action_type == "submit":

            if not self.signal_arrived:
                self.status = "signal_not_arrived"
                return

            self.evaluate()

        elif action_type == "reset":

            self.reset()

    # ========================================================
    # Validation
    # ========================================================

    def evaluate(self):

        error = abs(
            self.tuned_frequency
            - self.received_frequency
        )

        if error <= self.FREQUENCY_TOLERANCE:

            self.completed = True
            self.status = "success"

        elif self.tuned_frequency < self.received_frequency:

            self.completed = False
            self.status = "frequency_too_low"

        else:

            self.completed = False
            self.status = "frequency_too_high"

    def validate(self):
        return self.completed

    # ========================================================
    # State
    # ========================================================

    def get_state(self):

        return {
            "emitted_frequency":
                self.emitted_frequency,

            "source_velocity":
                self.source_velocity,

            "distance":
                self.distance,

            "tuned_frequency":
                self.tuned_frequency,

            "received_frequency":
                self.received_frequency,

            "signal_delay":
                self.signal_delay,

            "signal_progress":
                self.signal_progress,

            "elapsed_time":
                self.elapsed_time,

            "signal_arrived":
                self.signal_arrived,

            "running":
                self.running,

            "completed":
                self.completed,

            "status":
                self.status,

            "frequency_tolerance":
                self.FREQUENCY_TOLERANCE,
        }
