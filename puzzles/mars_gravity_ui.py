
import math
import time
import tkinter as tk

from puzzles.mars_gravity import MarsGravityPuzzle


# ============================================================
# ASTRA — Chapter 2: Mars Gravity
# Temporary interface — visual assets for Bri.
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 680

BG = "#1B1720"
PANEL = "#30232B"
TEXT = "#FFF4EA"
MUTED = "#D2B6A8"
ACCENT = "#FFB16B"
SUCCESS = "#91E4AE"

GROUND = "#9C4E37"
GROUND_DARK = "#68372F"
TRAJECTORY = "#FFE0A0"
SUIT = "#EAF2FA"
ROVER_COLOR = "#7DE0AC"


class MarsGravityUI(tk.Frame):

    FRAME_MS = 30

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=BG)

        self.puzzle = MarsGravityPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = False
        self.after_id = None
        self.completed_notified = False

        self.ground_y = 470
        self.origin_x = 65
        self.pixels_per_meter = 13

        self.trajectory = []

        self.velocity_var = tk.DoubleVar(value=8.6)
        self.angle_var = tk.DoubleVar(value=45)

        self.status_var = tk.StringVar(
            value="Watch the rover and time your jump!"
        )

        self.info_var = tk.StringVar()

        self.last_frame_time = time.monotonic()
        self.accumulator = 0.0

        self.build_ui()
        self.update_controls()
        self.update_info()
        self.draw_scene()

        # Start animation immediately.
        self.after_id = self.after(
            self.FRAME_MS,
            self.animate
        )

    # --------------------------------------------------------
    # Interface
    # --------------------------------------------------------

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
            bg=PANEL,
            width=WIDTH - SCENE_WIDTH
        )

        self.panel.pack(side="right", fill="y")
        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="MARS\nGRAVITY",
            font=("Arial", 18, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(25, 15))

        tk.Label(
            self.panel,
            text="Impulse velocity",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL
        ).pack()

        self.velocity_label = tk.Label(
            self.panel,
            font=("Arial", 14, "bold"),
            fg=ACCENT,
            bg=PANEL
        )
        self.velocity_label.pack(pady=5)

        self.velocity_slider = tk.Scale(
            self.panel,
            from_=0,
            to=30,
            resolution=0.1,
            orient="horizontal",
            variable=self.velocity_var,
            command=lambda _: self.update_controls(),
            bg=PANEL,
            fg=TEXT,
            troughcolor=GROUND_DARK,
            highlightthickness=0,
            showvalue=False,
            length=175
        )
        self.velocity_slider.pack(pady=5)

        tk.Label(
            self.panel,
            text="Launch angle",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL
        ).pack(pady=(12, 0))

        self.angle_label = tk.Label(
            self.panel,
            font=("Arial", 14, "bold"),
            fg=ACCENT,
            bg=PANEL
        )
        self.angle_label.pack(pady=5)

        self.angle_slider = tk.Scale(
            self.panel,
            from_=0,
            to=90,
            resolution=1,
            orient="horizontal",
            variable=self.angle_var,
            command=lambda _: self.update_controls(),
            bg=PANEL,
            fg=TEXT,
            troughcolor=GROUND_DARK,
            highlightthickness=0,
            showvalue=False,
            length=175
        )
        self.angle_slider.pack(pady=5)

        self.launch_button = tk.Button(
            self.panel,
            text="JUMP",
            font=("Arial", 11, "bold"),
            bg="#B85B3B",
            fg=TEXT,
            relief="flat",
            command=self.start_jump
        )
        self.launch_button.pack(
            fill="x",
            padx=20,
            pady=(18, 5),
            ipady=7
        )

        tk.Button(
            self.panel,
            text="RESET",
            font=("Arial", 10, "bold"),
            bg="#62453E",
            fg=TEXT,
            relief="flat",
            command=self.reset_simulation
        ).pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=6
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
            ).pack(pady=5)

        tk.Label(
            self.panel,
            textvariable=self.info_var,
            font=("Arial", 9),
            fg=MUTED,
            bg=PANEL,
            justify="left",
            wraplength=190
        ).pack(
            padx=15,
            pady=(15, 5),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=ACCENT,
            bg=PANEL,
            justify="center",
            wraplength=190
        ).pack(
            padx=12,
            pady=8
        )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    def update_controls(self):
        self.velocity_label.config(
            text=f"{self.velocity_var.get():.1f} m/s"
        )

        self.angle_label.config(
            text=f"{self.angle_var.get():.0f}°"
        )

    def start_jump(self):
        if self.running or self.puzzle.status != "ready":
            return

        self.trajectory.clear()
        self.completed_notified = False

        self.puzzle.update({
            "type": "launch",
            "velocity": self.velocity_var.get(),
            "angle": self.angle_var.get()
        })

        self.running = True

        self.velocity_slider.config(state="disabled")
        self.angle_slider.config(state="disabled")
        self.launch_button.config(state="disabled")

        self.status_var.set("Jump in progress...")

    def reset_simulation(self):
        self.puzzle.reset()
        self.trajectory.clear()

        self.running = False
        self.completed_notified = False
        self.accumulator = 0.0
        self.last_frame_time = time.monotonic()

        self.velocity_slider.config(state="normal")
        self.angle_slider.config(state="normal")
        self.launch_button.config(state="normal")

        self.status_var.set(
            "Watch the rover and time your jump!"
        )

        self.update_info()
        self.draw_scene()

    def go_back(self):
        self.stop_animation()

        if self.on_back is not None:
            self.on_back()

    def stop_animation(self):
        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

        self.after_id = None
        self.running = False

    # --------------------------------------------------------
    # Continuous simulation
    # --------------------------------------------------------

    def animate(self):
        now = time.monotonic()

        elapsed = min(
            now - self.last_frame_time,
            0.1
        )

        self.last_frame_time = now
        self.accumulator += elapsed

        dt = self.puzzle.TIME_STEP

        while self.accumulator >= dt:
            self.puzzle.update({
                "type": "tick",
                "dt": dt
            })

            self.accumulator -= dt

            state = self.puzzle.get_state()

            if self.running:
                self.trajectory.append(
                    (state["x"], state["y"])
                )

                if not state["launched"]:
                    self.finish_jump()
                    break

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            self.FRAME_MS,
            self.animate
        )

    def finish_jump(self):
        self.running = False

        self.velocity_slider.config(state="normal")
        self.angle_slider.config(state="normal")
        self.launch_button.config(state="normal")

        state = self.puzzle.get_state()

        messages = {
            "success": "Perfect landing! Mission complete.",
            "too_short": "Too short! Try a stronger impulse.",
            "too_far": "Too far! Try a weaker impulse.",
            "timeout": "Jump timed out. Try again."
        }

        self.status_var.set(
            messages.get(
                state["status"],
                "Jump finished."
            )
        )

        if (
            self.puzzle.validate()
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.after_idle(self.on_complete)

    # --------------------------------------------------------
    # Rendering
    # --------------------------------------------------------

    def world_to_screen(self, x, y):
        return (
            self.origin_x + x * self.pixels_per_meter,
            self.ground_y - y * self.pixels_per_meter
        )

    def draw_scene(self):
        self.canvas.delete("all")

        self.draw_sky()
        self.draw_ground()
        self.draw_rover()
        self.draw_trajectory()
        self.draw_astronaut()

        self.canvas.create_text(
            25, 25,
            text="CHAPTER 2 — ARRIVAL ON MARS",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            25, 55,
            text="Land on the moving rover.",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

    def draw_sky(self):
        self.canvas.create_oval(
            490, 90, 580, 180,
            fill="#E4A17A",
            outline=""
        )

        for i in range(35):
            x = (i * 89 + 41) % SCENE_WIDTH
            y = (i * 53 + 19) % 350

            self.canvas.create_oval(
                x, y, x + 2, y + 2,
                fill="#D8A894",
                outline=""
            )

    def draw_ground(self):
        self.canvas.create_rectangle(
            0,
            self.ground_y,
            SCENE_WIDTH,
            HEIGHT,
            fill=GROUND,
            outline=""
        )

        for i in range(12):
            x = i * 65

            self.canvas.create_oval(
                x,
                self.ground_y + 20 + (i % 3) * 17,
                x + 30,
                self.ground_y + 26 + (i % 3) * 17,
                fill=GROUND_DARK,
                outline=""
            )

    def draw_rover(self):
        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["rover_x"],
            0
        )

        half_width = (
            state["rover_width"]
            * self.pixels_per_meter
            / 2
        )

        # Placeholder rover body
        self.canvas.create_rectangle(
            x - half_width,
            y - 20,
            x + half_width,
            y - 8,
            fill=ROVER_COLOR,
            outline=""
        )

        self.canvas.create_rectangle(
            x - 12,
            y - 29,
            x + 12,
            y - 20,
            fill="#B5F0CE",
            outline=""
        )

        for wheel_x in (x - 15, x + 15):
            self.canvas.create_oval(
                wheel_x - 6,
                y - 10,
                wheel_x + 6,
                y + 2,
                fill="#343D47",
                outline=ROVER_COLOR,
                width=2
            )

        direction = (
            "→"
            if state["rover_direction"] > 0
            else "←"
        )

        self.canvas.create_text(
            x,
            y - 45,
            text=f"ROVER {direction}",
            fill=ROVER_COLOR,
            font=("Arial", 10, "bold")
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
            fill=TRAJECTORY,
            width=2
        )

    def draw_astronaut(self):
        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["x"],
            state["y"]
        )

        # Temporary Ada placeholder
        self.canvas.create_oval(
            x - 7,
            y - 22,
            x + 7,
            y - 8,
            fill=SUIT,
            outline=ACCENT,
            width=2
        )

        self.canvas.create_rectangle(
            x - 8,
            y - 8,
            x + 8,
            y + 6,
            fill=SUIT,
            outline=ACCENT
        )

        self.canvas.create_line(
            x - 4, y + 6,
            x - 6, y + 12,
            fill=SUIT,
            width=3
        )

        self.canvas.create_line(
            x + 4, y + 6,
            x + 6, y + 12,
            fill=SUIT,
            width=3
        )

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    def update_info(self):
        state = self.puzzle.get_state()

        self.info_var.set(
            f"Mars gravity: {state['gravity']:.2f} m/s²\n"
            f"Earth gravity: 9.81 m/s²\n\n"
            f"Ada distance: {state['x']:.2f} m\n"
            f"Ada height: {state['y']:.2f} m\n"
            f"Maximum height: {state['max_height']:.2f} m\n"
            f"Rover position: {state['rover_x']:.2f} m\n"
            f"Time: {state['time']:.2f} s"
        )

    def destroy(self):
        self.stop_animation()
        super().destroy()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ASTRA — Mars Gravity Test")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = MarsGravityUI(root)
    screen.pack(fill="both", expand=True)

    root.mainloop()
