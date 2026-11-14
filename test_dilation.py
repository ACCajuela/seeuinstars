
import math

from puzzles.time_dilation import TimeDilationPuzzle


def simulate(puzzle):
    puzzle.update({"type": "start"})

    while puzzle.get_state()["running"]:
        puzzle.update({
            "type": "tick",
            "dt": 0.1
        })


# Test 1: No time dilation at rest.
puzzle = TimeDilationPuzzle()

assert math.isclose(
    puzzle.get_state()["gamma"],
    1.0
)

assert math.isclose(
    puzzle.get_state()["ship_time"],
    10.0
)

print("Rest condition: OK")


# Test 2: Relativistic calculation.
puzzle.update({
    "type": "adjust",
    "parameter": "velocity",
    "value": 0.8
})

state = puzzle.get_state()

assert math.isclose(
    state["gamma"],
    5 / 3,
    rel_tol=1e-9
)

assert math.isclose(
    state["ship_time"],
    6.0,
    rel_tol=1e-9
)

assert math.isclose(
    state["time_difference"],
    4.0,
    rel_tol=1e-9
)

print("Lorentz calculation: OK")


# Test 3: Successful mission.
simulate(puzzle)

state = puzzle.get_state()

assert puzzle.validate()
assert state["status"] == "success"

assert math.isclose(
    state["elapsed_earth_time"],
    10.0,
    abs_tol=1e-8
)

assert math.isclose(
    state["elapsed_ship_time"],
    6.0,
    abs_tol=1e-8
)

print("Successful mission: OK")


# Test 4: Insufficient dilation.
puzzle.reset()

puzzle.update({
    "type": "adjust",
    "parameter": "velocity",
    "value": 0.2
})

simulate(puzzle)

assert not puzzle.validate()
assert (
    puzzle.get_state()["status"]
    == "insufficient_dilation"
)

print("Insufficient dilation: OK")


# Test 5: Excessive dilation.
puzzle.reset()

puzzle.update({
    "type": "adjust",
    "parameter": "velocity",
    "value": 0.95
})

simulate(puzzle)

assert not puzzle.validate()
assert (
    puzzle.get_state()["status"]
    == "excessive_dilation"
)

print("Excessive dilation: OK")


# Test 6: Reset.
puzzle.reset()

state = puzzle.get_state()

assert state["status"] == "ready"
assert not state["running"]
assert not state["completed"]

print("Reset: OK")


print("\nALL TIME DILATION TESTS PASSED!")
