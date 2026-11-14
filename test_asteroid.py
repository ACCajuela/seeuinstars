
from puzzles.asteroid_route import AsteroidRoutePuzzle


def run_test(velocity):
    puzzle = AsteroidRoutePuzzle()

    puzzle.update({
        "type": "launch",
        "velocity": velocity
    })

    while puzzle.get_state()["launched"]:
        puzzle.update({
            "type": "tick",
            "dt": puzzle.TIME_STEP
        })

    state = puzzle.get_state()

    print(f"\nVelocity: {velocity:.2f} AU/year")
    print(f"Status: {state['status']}")
    print(f"Maximum radius: {state['max_radius']:.3f} AU")
    print(f"Time: {state['time']:.3f} years")
    print(f"Completed: {state['completed']}")


run_test(5.09)
run_test(5.60)
run_test(6.50)
