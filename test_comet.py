
from puzzles.comet_spectrum import CometSpectrumPuzzle


def run_test(substances):
    puzzle = CometSpectrumPuzzle()

    for substance in substances:
        puzzle.update({
            "type": "toggle",
            "substance": substance
        })

    puzzle.update({
        "type": "submit"
    })

    state = puzzle.get_state()

    print("\nSelected:", substances)
    print("Status:", state["status"])
    print("Comparison:", state["comparison"])
    print("Completed:", state["completed"])


run_test(["water"])

run_test(["water", "sodium"])

run_test(["water", "cyanogen"])
