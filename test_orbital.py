
from core.puzzle_manager import PuzzleManager
from puzzles.orbital_launch import OrbitalLaunchPuzzle


manager = PuzzleManager()
manager.register("orbital_launch", OrbitalLaunchPuzzle)

tests = [
    ("Velocidade baixa", 3000),
    ("Órbita circular", 7670),
    ("Velocidade de escape", 11000),
]

for name, velocity in tests:
    manager.start("orbital_launch")
    manager.update({
        "type": "launch",
        "velocity": velocity,
    })

    for _ in range(2000):
        state = manager.update({
            "type": "tick",
            "dt": 10,
        })

        if not state["launched"]:
            break

    print(f"\n{name}")
    print(f"Velocidade inicial: {velocity} m/s")
    print(f"Resultado: {state['status']}")
    print(f"Tempo: {state['time']:.0f} s")
    print(f"Altitude final: {state['altitude'] / 1000:.1f} km")
    print(f"Puzzle concluído: {manager.validate()}")
