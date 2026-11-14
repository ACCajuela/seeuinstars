
from puzzles.comet_spectrum import CometSpectrumPuzzle


puzzle = CometSpectrumPuzzle(seed=42)

for number in range(1, 6):
    state = puzzle.get_state()

    print(f"\nComet {number}")
    print("Observed lines:", state["observed_lines"])

    # Access the answer only for automated testing.
    correct = puzzle.correct_substances.copy()

    print("Composition:", sorted(correct))

    for substance_id in correct:
        puzzle.update({
            "type": "toggle",
            "substance": substance_id
        })

    puzzle.update({
        "type": "submit"
    })

    result = puzzle.get_state()

    print("Status:", result["status"])
    print("Completed:", result["completed"])

    assert result["status"] == "success"
    assert result["completed"] is True

    puzzle.reset()

print("\nAll random comet tests passed!")
