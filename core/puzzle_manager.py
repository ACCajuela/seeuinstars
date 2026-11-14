
from typing import Any

from puzzles.base import BasePuzzle


class PuzzleManager:
    def __init__(self):
        self.registry: dict[str, type[BasePuzzle]] = {}
        self.current_puzzle: BasePuzzle | None = None
        self.current_id: str | None = None

    def register(self, puzzle_id: str, puzzle_class: type[BasePuzzle]):
        if not issubclass(puzzle_class, BasePuzzle):
            raise TypeError("Puzzle must inherit from BasePuzzle")

        self.registry[puzzle_id] = puzzle_class

    def start(self, puzzle_id: str) -> dict[str, Any]:
        if puzzle_id not in self.registry:
            raise ValueError(f"Unknown puzzle: {puzzle_id}")

        self.current_puzzle = self.registry[puzzle_id]()
        self.current_id = puzzle_id

        return self.current_puzzle.get_state()

    def update(self, action: dict[str, Any]) -> dict[str, Any]:
        if self.current_puzzle is None:
            raise RuntimeError("No active puzzle")

        self.current_puzzle.update(action)
        return self.current_puzzle.get_state()

    def validate(self) -> bool:
        if self.current_puzzle is None:
            return False

        result = self.current_puzzle.validate()
        self.current_puzzle.completed = result
        return result

    def reset(self) -> dict[str, Any]:
        if self.current_puzzle is None:
            raise RuntimeError("No active puzzle")

        self.current_puzzle.reset()
        return self.current_puzzle.get_state()

    def get_state(self) -> dict[str, Any] | None:
        if self.current_puzzle is None:
            return None

        return self.current_puzzle.get_state()
