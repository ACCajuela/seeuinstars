
import math

from puzzles.radio_signal import RadioSignalPuzzle


def simulate(puzzle):

    puzzle.update({
        "type": "start"
    })

    while puzzle.get_state()["running"]:

        puzzle.update({
            "type": "tick",
            "dt": 0.1
        })


# Test 1: Relativistic Doppler shift.
puzzle = RadioSignalPuzzle()

expected = 150.0 * math.sqrt(
    0.7 / 1.3
)

assert math.isclose(
    puzzle.get_state()["received_frequency"],
    expected,
    rel_tol=1e-9
)

print("Relativistic Doppler: OK")


# Test 2: Signal delay.
assert math.isclose(
    puzzle.get_state()["signal_delay"],
    12.0
)

print("Signal propagation delay: OK")


# Test 3: Signal cannot be decoded before arrival.
puzzle.update({
    "type": "submit"
})

assert (
    puzzle.get_state()["status"]
    == "signal_not_arrived"
)

print("Arrival restriction: OK")


# Test 4: Correct tuning.
puzzle.reset()

puzzle.update({
    "type": "tune",
    "frequency": expected
})

simulate(puzzle)

assert puzzle.validate()

assert (
    puzzle.get_state()["status"]
    == "success"
)

print("Correct tuning: OK")


# Test 5: Frequency too high.
puzzle.reset()

puzzle.update({
    "type": "tune",
    "frequency": 180.0
})

simulate(puzzle)

assert not puzzle.validate()

assert (
    puzzle.get_state()["status"]
    == "frequency_too_high"
)

print("Frequency too high: OK")


# Test 6: Frequency too low.
puzzle.reset()

puzzle.update({
    "type": "tune",
    "frequency": 80.0
})

simulate(puzzle)

assert not puzzle.validate()

assert (
    puzzle.get_state()["status"]
    == "frequency_too_low"
)

print("Frequency too low: OK")


# Test 7: Retuning after arrival.
puzzle.update({
    "type": "tune",
    "frequency": expected
})

puzzle.update({
    "type": "submit"
})

assert puzzle.validate()

print("Retuning after arrival: OK")


# Test 8: Reset.
puzzle.reset()

state = puzzle.get_state()

assert state["status"] == "ready"
assert not state["signal_arrived"]
assert not state["completed"]

print("Reset: OK")


print("\nALL RADIO SIGNAL TESTS PASSED!")
