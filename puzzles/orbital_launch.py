
import math

from puzzles.base import BasePuzzle


class OrbitalLaunchPuzzle(BasePuzzle):
    # Constantes físicas (SI)
    G = 6.67430e-11
    EARTH_MASS = 5.972e24
    EARTH_RADIUS = 6_371_000

    # Altitude inicial: 400 km
    INITIAL_ALTITUDE = 400_000

    # Intervalo de simulação: 10 segundos
    TIME_STEP = 10.0

    def __init__(self):
        super().__init__()

        self.mu = self.G * self.EARTH_MASS
        self.start_radius = (
            self.EARTH_RADIUS + self.INITIAL_ALTITUDE
        )

        self.circular_speed = math.sqrt(
            self.mu / self.start_radius
        )

        self.escape_speed = math.sqrt(
            2 * self.mu / self.start_radius
        )

        self.reset()

    def reset(self):
        self.x = self.start_radius
        self.y = 0.0

        self.vx = 0.0
        self.vy = 0.0

        self.time = 0.0
        self.launched = False
        self.completed = False

        self.status = "ready"

        self.min_radius = self.start_radius
        self.max_radius = self.start_radius

    def acceleration(self, x, y):
        radius = math.hypot(x, y)

        if radius == 0:
            return 0.0, 0.0

        factor = -self.mu / radius**3

        return factor * x, factor * y

    def update(self, action):
        action_type = action.get("type")

        if action_type == "launch":
            if self.launched or self.status != "ready":
                return

            speed = float(action.get("velocity", 0))

            if not math.isfinite(speed):
                raise ValueError("Velocity must be finite")

            if not 0 <= speed <= 15_000:
                raise ValueError(
                    "Velocity must be between 0 and 15000 m/s"
                )

            self.vy = speed
            self.launched = True
            self.status = "flying"

        elif action_type == "tick":
            if not self.launched:
                return

            dt = float(
                action.get("dt", self.TIME_STEP)
            )

            if not math.isfinite(dt) or not 0 < dt <= 10:
                raise ValueError(
                    "dt must be between 0 and 10 seconds"
                )

            self.step(dt)

    def step(self, dt):
        ax, ay = self.acceleration(self.x, self.y)

        # Atualização da posição
        new_x = (
            self.x + self.vx * dt + 0.5 * ax * dt**2
        )

        new_y = (
            self.y + self.vy * dt + 0.5 * ay * dt**2
        )

        # Nova aceleração gravitacional
        new_ax, new_ay = self.acceleration(
            new_x, new_y
        )

        # Atualização da velocidade
        self.vx += 0.5 * (ax + new_ax) * dt
        self.vy += 0.5 * (ay + new_ay) * dt

        self.x = new_x
        self.y = new_y
        self.time += dt

        radius = math.hypot(self.x, self.y)

        self.min_radius = min(
            self.min_radius, radius
        )

        self.max_radius = max(
            self.max_radius, radius
        )

        # Colisão com a Terra
        if radius <= self.EARTH_RADIUS:
            self.status = "collision"
            self.launched = False
            return

        # Energia mecânica específica
        speed_squared = self.vx**2 + self.vy**2

        energy = (
            0.5 * speed_squared - self.mu / radius
        )

        # Trajetória não ligada gravitacionalmente
        if energy >= 0:
            self.status = "escape"
            self.launched = False
            return

        # Aproximadamente uma órbita completa
        orbital_period = 2 * math.pi * math.sqrt(
            self.start_radius**3 / self.mu
        )

        if self.time >= orbital_period:
            self.launched = False

            # Tolerância didática de 5%
            variation = (
                self.max_radius - self.min_radius
            ) / self.start_radius

            if variation <= 0.05:
                self.status = "stable_orbit"
                self.completed = True
            else:
                self.status = "elliptical_orbit"

    def validate(self):
        return self.completed

    def get_state(self):
        radius = math.hypot(self.x, self.y)

        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "time": self.time,
            "altitude": radius - self.EARTH_RADIUS,
            "radius": radius,
            "earth_radius": self.EARTH_RADIUS,
            "circular_speed": self.circular_speed,
            "escape_speed": self.escape_speed,
            "launched": self.launched,
            "completed": self.completed,
            "status": self.status,
        }
