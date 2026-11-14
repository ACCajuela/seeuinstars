
from puzzles.spacetime import SpacetimePuzzle


puzzle = SpacetimePuzzle()

print("INITIAL STATE")
print(puzzle.get_state())


# Test 1: Default configuration should fail.
puzzle.update({"type": "submit"})

assert not puzzle.validate()
print("\nDefault:", puzzle.get_state()["status"])


# Test 2: Narrow passage should fail.
puzzle.reset()

puzzle.update({
    "type": "adjust",
    "parameter": "curvature",
    "value": 0.65
})

puzzle.update({
    "type": "adjust",
    "parameter": "stabilization",
    "value": 0.95
})

puzzle.update({"type": "submit"})

assert puzzle.get_state()["status"] == "narrow_passage"
print("Narrow passage: OK")


# Test 3: Valid configuration should succeed.
puzzle.reset()

for parameter, value in [
    ("curvature", 0.65),
    ("throat_radius", 0.60),
    ("stabilization", 0.90),
]:
    puzzle.update({
        "type": "adjust",
        "parameter": parameter,
        "value": value
    })

puzzle.update({"type": "submit"})

assert puzzle.validate()
assert puzzle.get_state()["status"] == "success"

print("Valid configuration: OK")


# Test 4: Grid generation.
grid = puzzle.generate_spacetime_grid(
    size=21
)

assert len(grid) == 441
assert all(len(point) == 3 for point in grid)

print("Geometry grid: OK")


# Test 5: Reset.
puzzle.reset()

assert not puzzle.validate()
assert puzzle.get_state()["status"] == "ready"

print("Reset: OK")

print("\nALL SPACETIME TESTS PASSED!")
