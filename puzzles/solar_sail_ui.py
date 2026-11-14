
import math
import time
import tkinter as tk

from puzzles.solar_sail import SolarSailPuzzle


WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 640
PANEL_WIDTH = 260

BG = "#0B1425"
PANEL_BG = "#1D2B40"

TEXT = "#F5F7FF"
MUTED = "#AABBD3"
CYAN = "#7ADCF3"
PURPLE = "#B6A1F6"
GOLD = "#F5C66F"
GREEN = "#8FE4AE"
RED = "#FF9999"

FRAME_MS = 30
SIMULATION_SPEED = 0.12


class SolarSailUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = SolarSailPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.after_id = None
        self.last_frame = time.monotonic()

        self.completed_notified = False
        self.running = True

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 75.0

        self.angle_var = tk.DoubleVar(
            value=self.puzzle.sail_angle
        )

        self.angle_label_var = tk.StringVar()
        self.info_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value="Orient the sail and begin."
        )

        self.sail_button_var = tk.StringVar(
            value="DEPLOY SAIL"
        )

        self.build_ui()

        self.update_labels()
        self.update_info()
        self.draw_scene()

        self.animate()

    # ========================================================
    # UI
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
            width=PANEL_WIDTH,
            bg=PANEL_BG
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="SOLAR\nSAIL",
            font=("Arial", 19, "bold"),
            fg=TEXT,
            bg=PANEL_BG,
            justify="center"
        ).pack(pady=(22, 16))

        tk.Label(
            self.panel,
            text="Sail orientation",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL_BG
        ).pack()

        tk.Label(
            self.panel,
            textvariable=self.angle_label_var,
            font=("Arial", 16, "bold"),
            fg=CYAN,
            bg=PANEL_BG
        ).pack(pady=7)

        self.angle_slider = tk.Scale(
            self.panel,
            from_=-85,
            to=85,
            resolution=1,
            orient="horizontal",
            variable=self.angle_var,
            command=self.on_angle_change,
            length=210,
            showvalue=False,
            bg=PANEL_BG,
            fg=TEXT,
            troughcolor="#465976",
            highlightthickness=0
        )

        self.angle_slider.pack(pady=(0, 14))

        self.create_button(
            "START SIMULATION",
            self.start_simulation,
            "#7356AE"
        )

        self.sail_button = tk.Button(
            self.panel,
            textvariable=self.sail_button_var,
            command=self.toggle_sail,
            font=("Arial", 11, "bold"),
            bg="#386A76",
            fg=TEXT,
            relief="flat"
        )

        self.sail_button.pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=8
        )

        self.create_button(
            "RESET",
            self.reset_simulation,
            "#435571"
        )

        if self.on_back is not None:

            self.create_button(
                "BACK",
                self.go_back,
                "#35445C"
            )

        tk.Label(
            self.panel,
            textvariable=self.info_var,
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL_BG,
            justify="left",
            wraplength=220
        ).pack(
            padx=20,
            pady=(18, 12),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=GOLD,
            bg=PANEL_BG,
            justify="center",
            wraplength=220
        ).pack(
            padx=15,
            pady=10
        )

    def create_button(self, label, command, color):

        button = tk.Button(
            self.panel,
            text=label,
            command=command,
            font=("Arial", 11, "bold"),
            bg=color,
            fg=TEXT,
            relief="flat"
        )

        button.pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=8
        )

        return button

    # ========================================================
    # Controls
    # ========================================================

    def on_angle_change(self, value):

        self.puzzle.update({
            "type": "adjust",
            "angle": float(value)
        })

        self.update_labels()

    def start_simulation(self):

        if self.puzzle.status != "ready":
            return

        self.puzzle.update({
            "type": "launch"
        })

        self.last_frame = time.monotonic()

        self.status_var.set(
            "Simulation started. Deploy the sail!"
        )

    def toggle_sail(self):

        state = self.puzzle.get_state()

        if state["status"] not in (
            "ready",
            "flying"
        ):
            return

        if state["sail_deployed"]:

            self.puzzle.update({
                "type": "retract"
            })

            self.sail_button_var.set(
                "DEPLOY SAIL"
            )

            self.status_var.set(
                "Sail retracted. Gravity only."
            )

        else:

            self.puzzle.update({
                "type": "deploy"
            })

            self.sail_button_var.set(
                "RETRACT SAIL"
            )

            self.status_var.set(
                "Sail deployed. Radiation pressure active."
            )

        self.draw_scene()

    def reset_simulation(self):

        self.puzzle.reset()

        self.angle_var.set(0.0)

        self.sail_button_var.set(
            "DEPLOY SAIL"
        )

        self.completed_notified = False

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 75.0

        self.last_frame = time.monotonic()

        self.status_var.set(
            "Simulation reset. Orient the sail."
        )

        self.update_labels()
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

    def update_labels(self):

        self.angle_label_var.set(
            f"{self.angle_var.get():+.0f}°"
        )

    def update_info(self):

        state = self.puzzle.get_state()

        self.info_var.set(
            f"Time: {state['time']:.3f} yr\n"
            f"Distance: {state['distance']:.4f} AU\n"
            f"Relative speed: "
            f"{state['relative_speed']:.3f} AU/yr\n"
            f"Docking range: "
            f"{state['docking_distance']:.3f} AU\n"
            f"Safe speed: "
            f"{state['docking_speed']:.2f} AU/yr\n"
            f"Sail: "
            f"{'DEPLOYED' if state['sail_deployed'] else 'RETRACTED'}"
        )

    # ========================================================
    # Camera
    # ========================================================

    def update_camera(self, state):

        ship_x = state["x"]
        ship_y = state["y"]

        target_x = state["target_x"]
        target_y = state["target_y"]

        midpoint_x = (
            ship_x + target_x
        ) / 2

        midpoint_y = (
            ship_y + target_y
        ) / 2

        distance = state["distance"]

        # Follow both ships at close range.
        if distance < 0.8:

            desired_x = midpoint_x
            desired_y = midpoint_y

            # Fit both ships in the scene.
            desired_zoom = min(
                850.0,
                max(
                    90.0,
                    400.0 / max(distance, 0.05)
                )
            )

        else:

            desired_x = 0.0
            desired_y = 0.0
            desired_zoom = 75.0

        smoothing = 0.05

        self.camera_x += (
            desired_x - self.camera_x
        ) * smoothing

        self.camera_y += (
            desired_y - self.camera_y
        ) * smoothing

        self.zoom += (
            desired_zoom - self.zoom
        ) * smoothing

    def world_to_screen(self, x, y):

        screen_x = (
            SCENE_WIDTH / 2
            + (x - self.camera_x) * self.zoom
        )

        screen_y = (
            HEIGHT / 2
            - (y - self.camera_y) * self.zoom
        )

        return screen_x, screen_y

    # ========================================================
    # Drawing
    # ========================================================

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.update_camera(state)

        self.draw_stars()
        self.draw_orbits()
        self.draw_trajectories(state)
        self.draw_sun()
        self.draw_connection(state)
        self.draw_spacecraft(state)
        self.draw_hud(state)

    def draw_stars(self):

        for i in range(90):

            x = (i * 97 + 23) % SCENE_WIDTH
            y = (i * 157 + 41) % HEIGHT

            size = 1 if i % 5 else 2

            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#53698B",
                outline=""
            )

    def draw_orbits(self):

        for radius, color in (
            (
                self.puzzle.START_RADIUS,
                "#314B68"
            ),
            (
                self.puzzle.TARGET_RADIUS,
                "#493C69"
            )
        ):

            x, y = self.world_to_screen(
                0, 0
            )

            r = radius * self.zoom

            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                outline=color,
                dash=(3, 5)
            )

    def draw_trajectories(self, state):

        self.draw_path(
            state["trajectory"],
            CYAN
        )

        self.draw_path(
            state["target_trajectory"],
            PURPLE
        )

    def draw_path(self, points, color):

        if len(points) < 2:
            return

        stride = max(
            1,
            len(points) // 700
        )

        sampled = points[::stride]

        if sampled[-1] != points[-1]:
            sampled.append(points[-1])

        coordinates = []

        for x, y in sampled:

            sx, sy = self.world_to_screen(
                x, y
            )

            coordinates.extend(
                (sx, sy)
            )

        if len(coordinates) >= 4:

            self.canvas.create_line(
                *coordinates,
                fill=color,
                width=2
            )

    def draw_sun(self):

        x, y = self.world_to_screen(
            0, 0
        )

        radius = max(
            8,
            min(
                24,
                0.12 * self.zoom
            )
        )

        self.canvas.create_oval(
            x - radius * 1.6,
            y - radius * 1.6,
            x + radius * 1.6,
            y + radius * 1.6,
            fill="#654A29",
            outline=""
        )

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=GOLD,
            outline="#FFF0AD",
            width=2
        )

    def draw_connection(self, state):

        x1, y1 = self.world_to_screen(
            state["x"],
            state["y"]
        )

        x2, y2 = self.world_to_screen(
            state["target_x"],
            state["target_y"]
        )

        if state["distance"] <= state["docking_distance"]:
            color = GREEN
        else:
            color = "#5C789A"

        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=color,
            dash=(4, 5)
        )

    def draw_spacecraft(self, state):

        ship_x, ship_y = self.world_to_screen(
            state["x"],
            state["y"]
        )

        target_x, target_y = self.world_to_screen(
            state["target_x"],
            state["target_y"]
        )

        self.draw_ship(
            ship_x,
            ship_y,
            CYAN,
            "ADA"
        )

        self.draw_ship(
            target_x,
            target_y,
            PURPLE,
            "VERA"
        )

        if state["sail_deployed"]:

            self.draw_sail(
                ship_x,
                ship_y,
                state
            )

    def draw_ship(
        self,
        x,
        y,
        color,
        label
    ):

        self.canvas.create_polygon(
            x,
            y - 11,
            x - 8,
            y + 9,
            x,
            y + 5,
            x + 8,
            y + 9,
            fill=color,
            outline=TEXT
        )

        self.canvas.create_text(
            x,
            y + 23,
            text=label,
            fill=color,
            font=("Arial", 10, "bold")
        )

    def draw_sail(
        self,
        x,
        y,
        state
    ):

        radial_angle = math.atan2(
            state["y"],
            state["x"]
        )

        normal_angle = (
            radial_angle
            + math.radians(
                state["sail_angle"]
            )
        )

        surface_angle = (
            normal_angle + math.pi / 2
        )

        dx = (
            math.cos(surface_angle) * 23
        )

        dy = (
            math.sin(surface_angle) * 23
        )

        self.canvas.create_line(
            x - dx,
            y + dy,
            x + dx,
            y - dy,
            fill=GOLD,
            width=4
        )

        self.canvas.create_line(
            x - dx,
            y + dy,
            x + dx,
            y - dy,
            fill="#FFF2C6",
            width=1
        )

    def draw_hud(self, state):

        self.canvas.create_text(
            20,
            20,
            text="CHAPTER 7 — SOLAR SAIL",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            49,
            text="Solar radiation pressure",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

        status = state["status"]

        if status == "success":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="SAFE RENDEZVOUS ACHIEVED",
                fill=GREEN,
                font=("Arial", 16, "bold")
            )

        elif status == "collision":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="COLLISION — RELATIVE SPEED TOO HIGH",
                fill=RED,
                font=("Arial", 12, "bold")
            )

        elif status == "timeout":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="TIME LIMIT REACHED",
                fill=RED,
                font=("Arial", 15, "bold")
            )

    # ========================================================
    # Status
    # ========================================================

    def handle_status(self, state):

        status = state["status"]

        if status == "success":

            self.status_var.set(
                "Success! Ada reached Vera safely."
            )

            if (
                not self.completed_notified
                and self.on_complete is not None
            ):

                self.completed_notified = True

                self.after_idle(
                    self.on_complete
                )

        elif status == "collision":

            self.status_var.set(
                "Collision! Relative speed too high."
            )

        elif status == "sun_collision":

            self.status_var.set(
                "Ada's ship collided with the Sun."
            )

        elif status == "timeout":

            self.status_var.set(
                "Time limit reached. Try another strategy."
            )

    # ========================================================
    # Animation
    # ========================================================

    def animate(self):

        if not self.running:
            return

        now = time.monotonic()

        elapsed = min(
            now - self.last_frame,
            0.1
        )

        self.last_frame = now

        previous_status = (
            self.puzzle.get_state()["status"]
        )

        if previous_status == "flying":

            self.puzzle.update({
                "type": "tick",
                "dt": (
                    elapsed
                    * SIMULATION_SPEED
                )
            })

        state = self.puzzle.get_state()

        if (
            previous_status == "flying"
            and state["status"] != "flying"
        ):

            self.handle_status(state)

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate
        )

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy(self):

        self.running = False

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
        "ASTRA — Solar Sail"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(False, False)

    screen = SolarSailUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
