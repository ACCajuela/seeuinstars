
import math
import tkinter as tk

from puzzles.orbital_launch import OrbitalLaunchPuzzle


# ============================================================
# ASTRA — Chapter 1: Orbital Launch
# Temporary UI — Bri can replace the visual elements later.
# ============================================================

WIDTH = 900
HEIGHT = 600

BG = "#081426"
PANEL = "#10243A"
TEXT = "#F3F7FF"
MUTED = "#A9BDD4"
ACCENT = "#71D8FF"
SUCCESS = "#8CE7B0"
WARNING = "#FFCE80"

EARTH_COLOR = "#3479B9"
SHIP_COLOR = "#FFFFFF"
ORBIT_COLOR = "#75CFFF"


class OrbitalLaunchUI(tk.Frame):

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=BG)

        self.puzzle = OrbitalLaunchPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = False
        self.after_id = None
        self.completed_notified = False

        self.scale_factor = 0.000025

        self.center_x = 360
        self.center_y = 300

        self.trajectory = []

        self.velocity_var = tk.DoubleVar(
            value=7670
        )

        self.status_var = tk.StringVar(
            value="Adjust the velocity and launch."
        )

        self.info_var = tk.StringVar(
            value=""
        )

        self.build_ui()
        self.draw_scene()
        self.update_info()

    # --------------------------------------------------------
    # Interface
    # --------------------------------------------------------

    def build_ui(self):

        self.canvas = tk.Canvas(
            self,
            width=700,
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
            bg=PANEL,
            width=200
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="ORBITAL\nLAUNCH",
            font=("Arial", 17, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(35, 12))

        tk.Label(
            self.panel,
            text="Initial velocity",
            font=("Arial", 11),
            fg=MUTED,
            bg=PANEL
        ).pack(pady=(10, 0))

        self.velocity_label = tk.Label(
            self.panel,
            text="7.67 km/s",
            font=("Arial", 15, "bold"),
            fg=ACCENT,
            bg=PANEL
        )

        self.velocity_label.pack(pady=8)

        self.velocity_slider = tk.Scale(
            self.panel,
            from_=0,
            to=15000,
            resolution=10,
            orient="horizontal",
            variable=self.velocity_var,
            command=self.on_velocity_change,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#28445F",
            activebackground=ACCENT,
            highlightthickness=0,
            length=170,
            showvalue=False
        )

        self.velocity_slider.pack(pady=8)

        self.start_button = tk.Button(
            self.panel,
            text="LAUNCH",
            font=("Arial", 11, "bold"),
            bg="#247DB5",
            fg=TEXT,
            activebackground="#369ACF",
            relief="flat",
            command=self.start_simulation
        )

        self.start_button.pack(
            fill="x",
            padx=20,
            pady=(25, 8),
            ipady=8
        )

        tk.Button(
            self.panel,
            text="RESET",
            font=("Arial", 10, "bold"),
            bg="#30475D",
            fg=TEXT,
            relief="flat",
            command=self.reset_simulation
        ).pack(
            fill="x",
            padx=20,
            pady=6,
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
            ).pack(
                fill="x",
                padx=20,
                pady=12
            )

        tk.Label(
            self.panel,
            textvariable=self.info_var,
            font=("Arial", 9),
            fg=MUTED,
            bg=PANEL,
            justify="left",
            wraplength=175
        ).pack(
            padx=12,
            pady=(25, 10),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=ACCENT,
            bg=PANEL,
            justify="center",
            wraplength=175
        ).pack(
            padx=12,
            pady=10
        )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    def on_velocity_change(self, value):
        velocity = float(value)

        self.velocity_label.config(
            text=f"{velocity / 1000:.2f} km/s"
        )

    def start_simulation(self):

        if self.running:
            return

        self.puzzle.reset()
        self.trajectory.clear()
        self.completed_notified = False

        velocity = self.velocity_var.get()

        self.puzzle.update({
            "type": "launch",
            "velocity": velocity
        })

        self.running = True

        self.velocity_slider.config(state="disabled")
        self.start_button.config(state="disabled")

        self.status_var.set("Simulating trajectory...")

        self.animate()

    def reset_simulation(self):

        self.stop_animation()

        self.puzzle.reset()
        self.trajectory.clear()

        self.completed_notified = False

        self.velocity_slider.config(state="normal")
        self.start_button.config(state="normal")

        self.status_var.set(
            "Adjust the velocity and launch."
        )

        self.update_info()
        self.draw_scene()

    def stop_animation(self):

        self.running = False

        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

    def go_back(self):

        self.stop_animation()

        if self.on_back is not None:
            self.on_back()

    # --------------------------------------------------------
    # Simulation
    # --------------------------------------------------------

    def animate(self):

        if not self.running:
            return

        # Multiple physics steps per rendered frame.
        for _ in range(5):

            self.puzzle.update({
                "type": "tick",
                "dt": 10
            })

            state = self.puzzle.get_state()

            self.trajectory.append(
                (state["x"], state["y"])
            )

            if not state["launched"]:
                break

        self.draw_scene()
        self.update_info()

        state = self.puzzle.get_state()

        if not state["launched"]:
            self.finish_simulation()
            return

        self.after_id = self.after(
            30,
            self.animate
        )

    def finish_simulation(self):

        self.running = False
        self.after_id = None

        self.velocity_slider.config(state="normal")
        self.start_button.config(state="normal")

        state = self.puzzle.get_state()

        messages = {
            "collision": "Collision! Try a higher velocity.",
            "escape": "Escape trajectory! Reduce velocity.",
            "stable_orbit": "Success! Stable orbit achieved.",
            "elliptical_orbit": (
                "Elliptical orbit. Try a more circular path."
            )
        }

        self.status_var.set(
            messages.get(
                state["status"],
                "Simulation finished."
            )
        )

        if (
            self.puzzle.validate()
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.on_complete()

    # --------------------------------------------------------
    # Rendering
    # --------------------------------------------------------

    def world_to_screen(self, x, y):

        return (
            self.center_x + x * self.scale_factor,
            self.center_y - y * self.scale_factor
        )

    def draw_scene(self):

        self.canvas.delete("all")

        self.draw_stars()
        self.draw_earth()
        self.draw_trajectory()
        self.draw_ship()

        self.canvas.create_text(
            25,
            25,
            text="CHAPTER 1 — THE WRONG SHIP",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            25,
            55,
            text="Find the correct orbital velocity.",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

    def draw_stars(self):

        # Deterministic placeholders.
        for i in range(65):

            x = (i * 97 + 31) % 700
            y = (i * 157 + 53) % HEIGHT

            radius = 1 if i % 3 else 2

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#7D9AB8",
                outline=""
            )

    def draw_earth(self):

        radius = (
            self.puzzle.EARTH_RADIUS
            * self.scale_factor
        )

        self.canvas.create_oval(
            self.center_x - radius,
            self.center_y - radius,
            self.center_x + radius,
            self.center_y + radius,
            fill=EARTH_COLOR,
            outline="#78C8FF",
            width=2
        )

        self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="EARTH",
            fill=TEXT,
            font=("Arial", 13, "bold")
        )

    def draw_trajectory(self):

        if len(self.trajectory) < 2:
            return

        points = []

        for x, y in self.trajectory:
            sx, sy = self.world_to_screen(x, y)
            points.extend((sx, sy))

        self.canvas.create_line(
            *points,
            fill=ORBIT_COLOR,
            width=2,
            smooth=False
        )

    def draw_ship(self):

        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["x"],
            state["y"]
        )

        # Temporary ship placeholder.
        self.canvas.create_polygon(
            x,
            y - 10,
            x - 8,
            y + 8,
            x + 8,
            y + 8,
            fill=SHIP_COLOR,
            outline=ACCENT,
            width=2
        )

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    def update_info(self):

        state = self.puzzle.get_state()

        altitude = max(0, state["altitude"] / 1000)

        self.info_var.set(
            f"Altitude: {altitude:.0f} km\n"
            f"Time: {state['time']:.0f} s\n\n"
            f"Circular speed:\n"
            f"{state['circular_speed'] / 1000:.2f} km/s\n\n"
            f"Escape speed:\n"
            f"{state['escape_speed'] / 1000:.2f} km/s"
        )

    def destroy(self):

        self.stop_animation()
        super().destroy()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()
    root.title("ASTRA — Orbital Launch Test")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = OrbitalLaunchUI(root)
    screen.pack(fill="both", expand=True)

    root.mainloop()
