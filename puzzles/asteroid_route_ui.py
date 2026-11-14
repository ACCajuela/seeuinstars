
import math
import random
import time
import tkinter as tk

from puzzles.asteroid_route import AsteroidRoutePuzzle


# ============================================================
# ASTRA — Chapter 3: Asteroid Belt
#
# Dynamic orbital transfer visualization.
#
# The spacecraft begins orbiting with Mars.
# LAUNCH represents an orbital maneuver.
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 640

BG = "#0D1424"
PANEL = "#202B3D"
TEXT = "#F5F7FF"
MUTED = "#AABBD2"
ACCENT = "#F7C56B"
SUCCESS = "#91E4AE"
ERROR = "#FF9A91"

SOLAR_MU = 4 * math.pi ** 2

MARS_RADIUS = 1.524
BELT_RADIUS = 2.5

SIMULATION_SPEED = 0.6
FRAME_MS = 30


class AsteroidRouteUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = AsteroidRoutePuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = False
        self.completed_notified = False

        self.after_id = None

        self.last_frame = time.monotonic()
        self.simulation_accumulator = 0.0

        # Global animation time.
        self.visual_time = 0.0

        # Orientation of the orbital maneuver.
        self.launch_angle = 0.0

        # Camera.
        self.center_x = SCENE_WIDTH / 2
        self.center_y = HEIGHT / 2

        self.base_scale = 78.0

        self.zoom = 1.0
        self.target_zoom = 1.0

        self.camera_x = 0.0
        self.camera_y = 0.0

        self.rng = random.Random(42)

        self.stars = [
            (
                self.rng.randint(0, SCENE_WIDTH),
                self.rng.randint(0, HEIGHT),
                self.rng.choice([1, 1, 2])
            )
            for _ in range(85)
        ]

        self.asteroids = []

        for _ in range(100):

            radius = self.rng.uniform(
                2.1,
                3.2
            )

            phase = self.rng.uniform(
                0,
                2 * math.pi
            )

            angular_speed = math.sqrt(
                SOLAR_MU / radius ** 3
            )

            self.asteroids.append({
                "radius": radius,
                "phase": phase,
                "speed": angular_speed,
                "size": self.rng.choice(
                    [1, 1, 2, 2, 3]
                )
            })

        self.velocity_var = tk.DoubleVar(
            value=5.68
        )

        self.info_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value="Spacecraft orbiting Mars. "
                  "Adjust velocity for maneuver."
        )

        self.build_ui()

        self.update_info()
        self.draw_scene()

        self.animate()

    # ========================================================
    # Interface
    # ========================================================

    def build_ui(self):

        self.canvas = tk.Canvas(
            self,
            width=SCENE_WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.panel = tk.Frame(
            self,
            width=WIDTH - SCENE_WIDTH,
            bg=PANEL
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="ASTEROID\nTRANSFER",
            font=("Arial", 18, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(25, 15))

        tk.Label(
            self.panel,
            text="Maneuver velocity (AU/year)",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL
        ).pack(pady=(10, 5))

        self.velocity_label = tk.Label(
            self.panel,
            text="5.68 AU/year",
            font=("Arial", 14, "bold"),
            fg=ACCENT,
            bg=PANEL
        )

        self.velocity_label.pack()

        self.velocity_slider = tk.Scale(
            self.panel,
            from_=0,
            to=8,
            resolution=0.01,
            orient="horizontal",
            variable=self.velocity_var,
            command=self.on_velocity_change,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#46566B",
            highlightthickness=0,
            length=210,
            showvalue=False
        )

        self.velocity_slider.pack(pady=10)

        tk.Button(
            self.panel,
            text="LAUNCH",
            font=("Arial", 11, "bold"),
            bg="#B97843",
            fg=TEXT,
            relief="flat",
            command=self.launch
        ).pack(
            fill="x",
            padx=20,
            pady=(15, 5),
            ipady=8
        )

        tk.Button(
            self.panel,
            text="RESET",
            font=("Arial", 10, "bold"),
            bg="#46566B",
            fg=TEXT,
            relief="flat",
            command=self.reset_simulation
        ).pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=7
        )

        if self.on_back is not None:

            tk.Button(
                self.panel,
                text="BACK",
                font=("Arial", 10),
                bg=PANEL,
                fg=MUTED,
                relief="flat",
                command=self.go_back
            ).pack(pady=8)

        tk.Label(
            self.panel,
            textvariable=self.info_var,
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL,
            justify="left",
            wraplength=220
        ).pack(
            padx=20,
            pady=(25, 10),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=ACCENT,
            bg=PANEL,
            wraplength=220,
            justify="center"
        ).pack(
            padx=15,
            pady=15
        )

    # ========================================================
    # Orbital coordinates
    # ========================================================

    def get_mars_position(self):

        angular_speed = math.sqrt(
            SOLAR_MU / MARS_RADIUS ** 3
        )

        angle = (
            angular_speed * self.visual_time
        )

        x = (
            MARS_RADIUS * math.cos(angle)
        )

        y = (
            MARS_RADIUS * math.sin(angle)
        )

        return x, y, angle

    def rotate_orbital_position(self, x, y):

        cos_a = math.cos(
            self.launch_angle
        )

        sin_a = math.sin(
            self.launch_angle
        )

        rotated_x = (
            x * cos_a
            - y * sin_a
        )

        rotated_y = (
            x * sin_a
            + y * cos_a
        )

        return rotated_x, rotated_y

    # ========================================================
    # Controls
    # ========================================================

    def on_velocity_change(self, value):

        velocity = float(value)

        self.velocity_label.config(
            text=f"{velocity:.2f} AU/year"
        )

    def launch(self):

        if self.running:
            return

        self.puzzle.reset()

        # Save the exact orbital orientation at
        # the moment of the maneuver.
        _, _, self.launch_angle = (
            self.get_mars_position()
        )

        self.puzzle.update({
            "type": "launch",
            "velocity": self.velocity_var.get()
        })

        self.running = True

        self.completed_notified = False

        self.simulation_accumulator = 0.0

        self.status_var.set(
            "Orbital maneuver initiated!"
        )

        self.update_info()

    def reset_simulation(self):

        self.running = False

        self.puzzle.reset()

        self.completed_notified = False

        self.simulation_accumulator = 0.0

        # Do not reset visual_time:
        # planets and asteroids keep orbiting.
        self.launch_angle = 0.0

        self.target_zoom = 1.0

        self.status_var.set(
            "Spacecraft returned to Mars orbit."
        )

        self.update_info()
        self.draw_scene()

    def go_back(self):

        self.running = False

        if self.after_id is not None:

            self.after_cancel(
                self.after_id
            )

            self.after_id = None

        if self.on_back is not None:
            self.on_back()

    # ========================================================
    # Camera
    # ========================================================

    def world_to_screen(self, x, y):

        scale = (
            self.base_scale * self.zoom
        )

        sx = (
            self.center_x
            + (x - self.camera_x) * scale
        )

        sy = (
            self.center_y
            - (y - self.camera_y) * scale
        )

        return sx, sy

    def update_camera(self, state):

        if state["launched"]:

            ship_x, ship_y = (
                self.rotate_orbital_position(
                    state["x"],
                    state["y"]
                )
            )

            desired_x = ship_x * 0.25
            desired_y = ship_y * 0.25

            distance = math.hypot(
                ship_x,
                ship_y
            )

            self.target_zoom = max(
                0.55,
                min(
                    1.0,
                    2.8 / max(distance, 0.1)
                )
            )

        else:

            desired_x = 0.0
            desired_y = 0.0

            self.target_zoom = 1.0

        smoothing = 0.06

        self.camera_x += (
            desired_x - self.camera_x
        ) * smoothing

        self.camera_y += (
            desired_y - self.camera_y
        ) * smoothing

        self.zoom += (
            self.target_zoom - self.zoom
        ) * smoothing

    # ========================================================
    # Animation
    # ========================================================

    def animate(self):

        now = time.monotonic()

        elapsed = min(
            now - self.last_frame,
            0.1
        )

        self.last_frame = now

        simulated_dt = (
            elapsed * SIMULATION_SPEED
        )

        # Planetary motion continues even before
        # the spacecraft maneuver.
        self.visual_time += simulated_dt

        if self.running:

            self.simulation_accumulator += (
                simulated_dt
            )

            while (
                self.simulation_accumulator
                >= 0.001
            ):

                self.puzzle.update({
                    "type": "tick",
                    "dt": 0.001
                })

                self.simulation_accumulator -= (
                    0.001
                )

                state = (
                    self.puzzle.get_state()
                )

                if state["status"] != "flying":

                    self.finish_simulation(
                        state
                    )

                    break

        state = self.puzzle.get_state()

        self.update_camera(state)

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate
        )

    def finish_simulation(self, state):

        self.running = False

        self.simulation_accumulator = 0.0

        status = state["status"]

        if status == "success":

            self.status_var.set(
                "Success! Asteroid belt reached."
            )

            if (
                not self.completed_notified
                and self.on_complete is not None
            ):

                self.completed_notified = True

                self.after_idle(
                    self.on_complete
                )

        elif status == "too_short":

            self.status_var.set(
                "The orbit did not reach the belt."
            )

        elif status == "too_far":

            self.status_var.set(
                "The orbit extended beyond the target."
            )

        elif status == "escape":

            self.status_var.set(
                "The spacecraft escaped the Sun!"
            )

        elif status == "collision":

            self.status_var.set(
                "The spacecraft collided with the Sun."
            )

        else:

            self.status_var.set(
                f"Simulation ended: {status}"
            )

    # ========================================================
    # Predicted orbital geometry
    # ========================================================

    def calculate_preview_orbit(self):

        radius = MARS_RADIUS
        velocity = self.velocity_var.get()

        energy = (
            velocity ** 2 / 2
            - SOLAR_MU / radius
        )

        if energy >= 0:
            return None

        semi_major = (
            -SOLAR_MU / (2 * energy)
        )

        angular_momentum = (
            radius * velocity
        )

        eccentricity_squared = (
            1
            + (
                2 * energy
                * angular_momentum ** 2
                / SOLAR_MU ** 2
            )
        )

        eccentricity = math.sqrt(
            max(
                0.0,
                eccentricity_squared
            )
        )

        if eccentricity >= 1:
            return None

        circular_speed = math.sqrt(
            SOLAR_MU / radius
        )

        if velocity >= circular_speed:

            center_x = (
                radius - semi_major
            )

        else:

            center_x = (
                semi_major - radius
            )

        semi_minor = (
            semi_major
            * math.sqrt(
                1 - eccentricity ** 2
            )
        )

        return {
            "a": semi_major,
            "b": semi_minor,
            "center_x": center_x
        }

    # ========================================================
    # Drawing
    # ========================================================

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.draw_stars()

        self.draw_orbit_guides()

        self.draw_asteroids()

        self.draw_preview_orbit(state)

        self.draw_trajectory(state)

        self.draw_sun()

        self.draw_mars()

        self.draw_spacecraft(state)

        self.draw_labels()

    def draw_stars(self):

        for x, y, size in self.stars:

            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#667996",
                outline=""
            )

    def draw_world_circle(
        self,
        radius,
        color,
        dash=None,
        width=1
    ):

        cx, cy = (
            self.world_to_screen(
                0,
                0
            )
        )

        r = (
            radius
            * self.base_scale
            * self.zoom
        )

        self.canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            outline=color,
            dash=dash,
            width=width
        )

    def draw_orbit_guides(self):

        self.draw_world_circle(
            MARS_RADIUS,
            "#405C82",
            dash=(4, 5)
        )

        self.draw_world_circle(
            BELT_RADIUS,
            "#8D7652",
            dash=(4, 5),
            width=2
        )

        self.draw_world_circle(
            2.1,
            "#494332",
            dash=(2, 6)
        )

        self.draw_world_circle(
            3.2,
            "#494332",
            dash=(2, 6)
        )

    def draw_asteroids(self):

        for asteroid in self.asteroids:

            angle = (
                asteroid["phase"]
                + asteroid["speed"]
                * self.visual_time
            )

            radius = asteroid["radius"]

            x = (
                radius * math.cos(angle)
            )

            y = (
                radius * math.sin(angle)
            )

            sx, sy = (
                self.world_to_screen(
                    x,
                    y
                )
            )

            size = asteroid["size"]

            if (
                -10 <= sx <= SCENE_WIDTH + 10
                and -10 <= sy <= HEIGHT + 10
            ):

                self.canvas.create_oval(
                    sx - size,
                    sy - size,
                    sx + size,
                    sy + size,
                    fill="#B5A38B",
                    outline=""
                )

    def draw_preview_orbit(self, state):

        if state["launched"]:
            return

        orbit = (
            self.calculate_preview_orbit()
        )

        if orbit is None:
            return

        _, _, mars_angle = (
            self.get_mars_position()
        )

        cos_a = math.cos(mars_angle)
        sin_a = math.sin(mars_angle)

        points = []

        for i in range(181):

            theta = (
                2 * math.pi * i / 180
            )

            local_x = (
                orbit["center_x"]
                + orbit["a"]
                * math.cos(theta)
            )

            local_y = (
                orbit["b"]
                * math.sin(theta)
            )

            # Rotate the predicted orbit so
            # it follows Mars' current position.
            x = (
                local_x * cos_a
                - local_y * sin_a
            )

            y = (
                local_x * sin_a
                + local_y * cos_a
            )

            sx, sy = (
                self.world_to_screen(
                    x,
                    y
                )
            )

            points.extend(
                [sx, sy]
            )

        self.canvas.create_line(
            *points,
            fill="#4CB9C9",
            width=2,
            dash=(5, 4)
        )

    def draw_trajectory(self, state):

        trajectory = state.get(
            "trajectory",
            []
        )

        if (
            not state["launched"]
            or len(trajectory) < 2
        ):
            return

        points = []

        for x, y in trajectory:

            rotated_x, rotated_y = (
                self.rotate_orbital_position(
                    x,
                    y
                )
            )

            sx, sy = (
                self.world_to_screen(
                    rotated_x,
                    rotated_y
                )
            )

            points.extend(
                [sx, sy]
            )

        self.canvas.create_line(
            *points,
            fill="#7CE4F2",
            width=2
        )

    def draw_sun(self):

        x, y = (
            self.world_to_screen(
                0,
                0
            )
        )

        self.canvas.create_oval(
            x - 25,
            y - 25,
            x + 25,
            y + 25,
            fill="#E6A53B",
            outline=""
        )

        self.canvas.create_oval(
            x - 17,
            y - 17,
            x + 17,
            y + 17,
            fill="#FFD36B",
            outline=""
        )

    def draw_mars(self):

        x, y, _ = (
            self.get_mars_position()
        )

        sx, sy = (
            self.world_to_screen(
                x,
                y
            )
        )

        self.canvas.create_oval(
            sx - 7,
            sy - 7,
            sx + 7,
            sy + 7,
            fill="#D98669",
            outline=""
        )

    def draw_spacecraft(self, state):

        if state["launched"]:

            x, y = (
                self.rotate_orbital_position(
                    state["x"],
                    state["y"]
                )
            )

            vx, vy = (
                self.rotate_orbital_position(
                    state["vx"],
                    state["vy"]
                )
            )

        else:

            x, y, angle = (
                self.get_mars_position()
            )

            orbital_speed = math.sqrt(
                SOLAR_MU / MARS_RADIUS
            )

            vx = (
                -orbital_speed
                * math.sin(angle)
            )

            vy = (
                orbital_speed
                * math.cos(angle)
            )

        sx, sy = (
            self.world_to_screen(
                x,
                y
            )
        )

        direction_angle = math.atan2(
            vy,
            vx
        )

        direction_x = math.cos(
            direction_angle
        )

        direction_y = -math.sin(
            direction_angle
        )

        perpendicular_x = -direction_y
        perpendicular_y = direction_x

        tip_x = (
            sx + direction_x * 12
        )

        tip_y = (
            sy + direction_y * 12
        )

        back_x = (
            sx - direction_x * 8
        )

        back_y = (
            sy - direction_y * 8
        )

        left_x = (
            back_x
            + perpendicular_x * 6
        )

        left_y = (
            back_y
            + perpendicular_y * 6
        )

        right_x = (
            back_x
            - perpendicular_x * 6
        )

        right_y = (
            back_y
            - perpendicular_y * 6
        )

        self.canvas.create_polygon(
            tip_x,
            tip_y,
            left_x,
            left_y,
            right_x,
            right_y,
            fill="#7CE4F2",
            outline=TEXT
        )

    def draw_labels(self):

        self.canvas.create_text(
            20,
            20,
            text="CHAPTER 3 — ASTEROID BELT",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            50,
            text="Dynamic orbital transfer",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            HEIGHT - 30,
            text=(
                "Dashed cyan: predicted orbit  |  "
                "Solid cyan: spacecraft path"
            ),
            fill=MUTED,
            font=("Arial", 9),
            anchor="nw"
        )

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):

        state = self.puzzle.get_state()

        radius = state.get(
            "radius",
            MARS_RADIUS
        )

        max_radius = state.get(
            "max_radius",
            MARS_RADIUS
        )

        simulation_time = state.get(
            "time",
            0.0
        )

        self.info_var.set(
            f"Distance from Sun: {radius:.3f} AU\n"
            f"Maximum distance: {max_radius:.3f} AU\n"
            f"Target distance: {BELT_RADIUS:.2f} AU\n"
            f"Flight time: {simulation_time:.3f} years\n"
            f"Camera zoom: {self.zoom:.2f}x"
        )

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy(self):

        if self.after_id is not None:

            self.after_cancel(
                self.after_id
            )

            self.after_id = None

        super().destroy()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "ASTRA — Dynamic Asteroid Transfer"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(False, False)

    screen = AsteroidRouteUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
