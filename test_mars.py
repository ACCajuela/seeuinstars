
from core.puzzle_manager import PuzzleManager
from puzzles.mars_gravity import MarsGravityPuzzle


manager = PuzzleManager()
manager.register("mars_gravity", MarsGravityPuzzle)

tests = [
    ("Salto curto", 5.0, 45),
    ("Pouso correto", 8.6, 45),
    ("Salto longo", 12.0, 45),
]

for name, velocity, angle in tests:
    manager.start("mars_gravity")

    manager.update({
        "type": "launch",
        "velocity": velocity,
        "angle": angle,
    })

    for _ in range(2000):
        state = manager.update({
            "type": "tick",
            "dt": 0.02,
        })

        if not state["launched"]:
            break

    print(f"\n{name}")
    print(f"Velocidade: {velocity} m/s")
    print(f"Ângulo: {angle}°")
    print(f"Distância: {state['x']:.2f} m")
    print(f"Altura máxima: {state['max_height']:.2f} m")
    print(f"Tempo: {state['time']:.2f} s")
    print(f"Resultado: {state['status']}")
    print(f"Concluído: {manager.validate()}")
