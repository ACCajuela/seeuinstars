
import math
import random
import time
import tkinter as tk

from core.ui import (
    ACCENT,
    FEEDBACK_COLOR,
    MINIGAME_MUTED as MUTED,
    MINIGAME_PANEL,
    MINIGAME_SUCCESS as SUCCESS,
    TITLE as TEXT,
    CanvasLabel,
    CanvasSlider,
    CosmoHint,
    MenuButton,
    draw_minigame_heading,
    draw_minigame_panel,
)

from puzzles.asteroid_route import AsteroidRoutePuzzle


# ============================================================
# ASTRA — Chapter 3: Asteroid Belt
# Dynamic orbital transfer + COSMO educational guidance
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 680

BG = "#0D1424"

SOLAR_MU = AsteroidRoutePuzzle.SOLAR_MU
MARS_RADIUS = AsteroidRoutePuzzle.START_RADIUS
BELT_RADIUS = AsteroidRoutePuzzle.TARGET_RADIUS

SIMULATION_SPEED = 0.6
FRAME_MS = 30

STAR_COLOR = "#667996"
ASTEROID_COLOR = "#B5A38B"
PREVIEW_COLOR = "#4CB9C9"
TRAJECTORY_COLOR = "#7CE4F2"


class AsteroidRouteUI(tk.Frame):

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=BG)

        self.puzzle = AsteroidRoutePuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = False
        self.completed_notified = False
        self.after_id = None

        self.last_frame = time.monotonic()
        self.simulation_accumulator = 0.0

        # Planetary animation continues between attempts.
        self.visual_time = 0.0
        self.launch_angle = 0.0

        # Camera
        self.center_x = SCENE_WIDTH / 2
        self.center_y = HEIGHT / 2

        self.base_scale = 78.0
        self.zoom = 1.0
        self.target_zoom = 1.0

        self.camera_x = 0.0
        self.camera_y = 0.0

        # COSMO
        self.hint_level = 0
        self.attempts = 0
        self.last_result = None

        # Fixed random positions for repeatable visuals.
        self.rng = random.Random(42)

        self.stars = [
            (
                self.rng.randint(0, SCENE_WIDTH),
                self.rng.randint(0, HEIGHT),
                self.rng.choice([1, 1, 2]),
            )
            for _ in range(85)
        ]

        self.asteroids = []

        for _ in range(100):
            radius = self.rng.uniform(2.1, 3.2)
            phase = self.rng.uniform(0, 2 * math.pi)

            angular_speed = math.sqrt(
                SOLAR_MU / radius**3
            )

            self.asteroids.append({
                "radius": radius,
                "phase": phase,
                "speed": angular_speed,
                "size": self.rng.choice([1, 1, 2, 2, 3]),
            })

        # The starting value is intentionally below
        # the ideal transfer velocity.
        self.velocity_var = tk.DoubleVar(value=5.68)

        self.info_var = tk.StringVar(value="")

        self.status_var = tk.StringVar(
            value=(
                "COSMO: Ada, we must reach the asteroid belt. "
                "Adjust our tangential velocity to extend "
                "the orbit beyond Mars."
            )
        )

        self.build_ui()
        self.on_velocity_change(self.velocity_var.get())
        self.update_info()
        self.draw_scene()
        self.animate()

    # ========================================================
    # Interface
    # ========================================================

    def build_ui(self):
        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        c = self.canvas

        draw_minigame_heading(
            c,
            "CHAPTER 3 — ASTEROID BELT",
            "Reach the target distance from the Sun.",
        )

        draw_minigame_panel(c, "ASTEROID\nTRANSFER")

        x0, y0, x1, y1 = MINIGAME_PANEL
        cx = (x0 + x1) / 2

        c.create_text(
            cx, 137,
            text="Maneuver velocity",
            font=("Arial", 11),
            fill=MUTED,
        )

        self.velocity_label = CanvasLabel(
            c,
            c.create_text(
                cx, 165,
                text="5.68 AU/year",
                font=("Arial", 17, "bold"),
                fill=ACCENT,
            ),
        )

        self.velocity_slider = CanvasSlider(
            c,
            x0 + 22,
            205,
            (x1 - x0) - 44,
            from_=0,
            to=8,
            resolution=0.01,
            variable=self.velocity_var,
            command=self.on_velocity_change,
        )

        self.launch_button = MenuButton(
            c, cx, 260,
            "LAUNCH", self.launch,
            width=160,
            height=42,
            font_size=12,
            primary=True,
        )

        MenuButton(
            c, cx, 312,
            "COSMO HINT", self.request_hint,
            width=160,
            height=40,
            font_size=11,
        )

        MenuButton(
            c, cx, 362,
            "RESET", self.reset_simulation,
            width=160,
            height=40,
            font_size=11,
        )

        if self.on_back is not None:
            MenuButton(
                c, cx, 412,
                "BACK", self.go_back,
                width=160,
                height=38,
                font_size=11,
            )

        c.create_line(
            x0 + 20, 445,
            x1 - 20, 445,
            fill="#24324F",
            width=2,
        )

        info_item = c.create_text(
            x0 + 20, 460,
            anchor="nw",
            width=(x1 - x0) - 36,
            font=("Arial", 10),
            fill=MUTED,
        )

        self.info_var.trace_add(
            "write",
            lambda *_: c.itemconfigure(
                info_item,
                text=self.info_var.get(),
            ),
        )

        # COSMO appears over the orbital scene.
        self.hint = CosmoHint(
            c,
            right=SCENE_WIDTH - 20,
        )

        self.status_var.trace_add(
            "write",
            lambda *_: self.show_status(),
        )

        self.show_status()

    def show_status(self):
        status = self.puzzle.get_state()["status"]

        if status == "success":
            color = SUCCESS

        elif status in (
            "too_short",
            "too_far",
            "escape",
            "collision",
            "timeout",
        ):
            color = FEEDBACK_COLOR

        else:
            color = TEXT

        self.hint.set(self.status_var.get(), color)

    # ========================================================
    # COSMO — progressive educational guidance
    # ========================================================

    def say(self, message):
        self.status_var.set("COSMO: " + message)

    def request_hint(self):
        if self.puzzle.completed:
            self.say(
                "Excellent work! We changed the orbit's "
                "energy with a tangential maneuver. "
                "The spacecraft reached the asteroid "
                "belt at its farthest orbital point."
            )
            return

        if self.running:
            self.say(
                "Watch the spacecraft move away from "
                "the Sun. At aphelion, its radial motion "
                "changes from outward to inward."
            )
            return

        self.hint_level = min(self.hint_level + 1, 4)

        if self.hint_level == 1:
            self.say(
                "The spacecraft already has orbital "
                "velocity around the Sun. Our maneuver "
                "changes that tangential velocity."
            )

        elif self.hint_level == 2:
            self.say(
                "A small prograde speed increase can "
                "raise the opposite side of the orbit. "
                "This creates an elliptical transfer path."
            )

        elif self.hint_level == 3:
            self.say(
                "Our starting distance is 1.524 AU. "
                "The target is 2.5 AU. We want the "
                "orbit's farthest point, called aphelion, "
                "to reach that target."
            )

        else:
            self.show_advanced_hint()

    def show_advanced_hint(self):
        velocity = self.velocity_var.get()

        aphelion = self.predict_aphelion(velocity)

        if aphelion is None:
            self.say(
                "This velocity gives the spacecraft "
                "enough energy to escape the Sun. "
                "Reduce the maneuver velocity."
            )
            return

        if velocity < self.puzzle.circular_speed:
            self.say(
                "This velocity is below the local "
                "circular speed. The spacecraft will "
                "initially move inward rather than "
                "toward the asteroid belt."
            )
            return

        self.say(
            f"At {velocity:.2f} AU/year, the predicted "
            f"aphelion is about {aphelion:.2f} AU. "
            "Our target range is 2.4 to 2.6 AU. "
            "Adjust the velocity and compare."
        )

    def predict_aphelion(self, velocity):
        """
        Analytical prediction using specific orbital energy.

        For a prograde maneuver at Mars' radius,
        the launch point is perihelion.
        """

        radius = self.puzzle.START_RADIUS
        mu = self.puzzle.SOLAR_MU

        energy = velocity**2 / 2 - mu / radius

        if energy >= 0:
            return None

        semi_major = -mu / (2 * energy)

        circular_speed = math.sqrt(mu / radius)

        if velocity < circular_speed:
            # Launch point is aphelion, not perihelion.
            return radius

        return 2 * semi_major - radius

    def contextual_feedback(self, state):
        status = state["status"]
        self.last_result = status

        max_radius = state["max_radius"]
        target = state["target_radius"]

        if status == "too_short":
            difference = target - max_radius

            self.say(
                f"Our aphelion reached {max_radius:.2f} AU, "
                f"about {difference:.2f} AU short of the "
                "target. Increase the tangential velocity "
                "to raise the far side of the orbit."
            )

        elif status == "too_far":
            difference = max_radius - target

            self.say(
                f"Our aphelion reached {max_radius:.2f} AU, "
                f"about {difference:.2f} AU beyond the "
                "target. Reduce the maneuver velocity."
            )

        elif status == "escape":
            self.say(
                "The spacecraft gained enough orbital "
                "energy to escape the Sun. An escape "
                "trajectory will not give us the "
                "bounded transfer orbit we need."
            )

        elif status == "collision":
            self.say(
                "The spacecraft fell into the Sun! "
                "A very low tangential velocity cannot "
                "maintain a safe solar orbit. "
                "Try a faster maneuver."
            )

        elif status == "timeout":
            self.say(
                "We did not reach a valid first aphelion "
                "within the simulation time. Review the "
                "maneuver velocity and try again."
            )

        elif status == "success":
            self.say(
                f"Transfer successful! Our aphelion "
                f"reached {max_radius:.2f} AU, within "
                "the asteroid belt target range. "
                "This is how orbital energy can be used "
                "to plan transfers between solar orbits!"
            )

        else:
            self.say(
                "Simulation finished. Let's review "
                "the orbital maneuver."
            )

    # ========================================================
    # Orbital coordinates
    # ========================================================

    def get_mars_position(self):
        angular_speed = math.sqrt(
            SOLAR_MU / MARS_RADIUS**3
        )

        angle = angular_speed * self.visual_time

        return (
            MARS_RADIUS * math.cos(angle),
            MARS_RADIUS * math.sin(angle),
            angle,
        )

    def rotate_orbital_position(self, x, y):
        cos_a = math.cos(self.launch_angle)
        sin_a = math.sin(self.launch_angle)

        return (
            x * cos_a - y * sin_a,
            x * sin_a + y * cos_a,
        )

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

        # Preserve the visual orbital orientation
        # at the exact moment of the maneuver.
        _, _, self.launch_angle = self.get_mars_position()

        self.puzzle.update({
            "type": "launch",
            "velocity": self.velocity_var.get(),
        })

        self.running = True
        self.attempts += 1
        self.completed_notified = False
        self.simulation_accumulator = 0.0

        self.velocity_slider.config(state="disabled")
        self.launch_button.config(state="disabled")

        self.say(
            "Maneuver initiated! Watch the trajectory "
            "change as the spacecraft moves through "
            "the Sun's gravitational field."
        )

        self.update_info()

    def reset_simulation(self):
        self.running = False
        self.puzzle.reset()

        self.completed_notified = False
        self.simulation_accumulator = 0.0

        # Keep planets and asteroids moving.
        self.launch_angle = 0.0
        self.target_zoom = 1.0

        self.velocity_slider.config(state="normal")
        self.launch_button.config(state="normal")

        self.say(
            "Spacecraft returned to Mars' orbit. "
            "Adjust the maneuver velocity or ask "
            "me for another hint."
        )

        self.update_info()
        self.draw_scene()

    def go_back(self):
        self.stop_animation()

        if self.on_back is not None:
            self.on_back()

    def stop_animation(self):
        self.running = False

        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

    # ========================================================
    # Camera
    # ========================================================

    def world_to_screen(self, x, y):
        scale = self.base_scale * self.zoom

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
                    state["x"], state["y"]
                )
            )

            desired_x = ship_x * 0.25
            desired_y = ship_y * 0.25

            distance = math.hypot(ship_x, ship_y)

            self.target_zoom = max(
                0.55,
                min(1.0, 2.8 / max(distance, 0.1)),
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
            max(0.0, now - self.last_frame),
            0.1,
        )

        self.last_frame = now
        simulated_dt = elapsed * SIMULATION_SPEED

        # Mars and the asteroids continue orbiting
        # even when no maneuver is active.
        self.visual_time += simulated_dt

        if self.running:
            self.simulation_accumulator += simulated_dt

            dt = self.puzzle.TIME_STEP

            while self.simulation_accumulator >= dt:
                self.puzzle.update({
                    "type": "tick",
                    "dt": dt,
                })

                self.simulation_accumulator -= dt

                state = self.puzzle.get_state()

                if state["status"] != "flying":
                    self.finish_simulation(state)
                    break

        state = self.puzzle.get_state()

        self.update_camera(state)
        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate,
        )

    def finish_simulation(self, state):
        self.running = False
        self.simulation_accumulator = 0.0

        self.velocity_slider.config(state="normal")
        self.launch_button.config(state="normal")

        self.contextual_feedback(state)

        if (
            self.puzzle.validate()
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.after_idle(self.on_complete)

    # ========================================================
    # Predicted orbital geometry
    # ========================================================

    def calculate_preview_orbit(self):
        radius = MARS_RADIUS
        velocity = self.velocity_var.get()

        energy = (
            velocity**2 / 2
            - SOLAR_MU / radius
        )

        if energy >= 0:
            return None

        semi_major = -SOLAR_MU / (2 * energy)
        angular_momentum = radius * velocity

        eccentricity_squared = (
            1
            + 2 * energy * angular_momentum**2
            / SOLAR_MU**2
        )

        eccentricity = math.sqrt(
            max(0.0, eccentricity_squared)
        )

        if eccentricity >= 1:
            return None

        circular_speed = math.sqrt(
            SOLAR_MU / radius
        )

        if velocity >= circular_speed:
            center_x = radius - semi_major
        else:
            center_x = semi_major - radius

        semi_minor = (
            semi_major
            * math.sqrt(1 - eccentricity**2)
        )

        return {
            "a": semi_major,
            "b": semi_minor,
            "center_x": center_x,
        }

    # ========================================================
    # Drawing
    # ========================================================

    def draw_scene(self):
        # Only clear the moving space visualization.
        # The controls and COSMO bubble stay intact.
        self.canvas.delete("space_dyn")

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

        self.hint.raise_()

    def draw_stars(self):
        for x, y, size in self.stars:
            self.canvas.create_oval(
                x, y,
                x + size, y + size,
                fill=STAR_COLOR,
                outline="",
                tags="space_dyn",
            )

    def draw_world_circle(
        self, radius, color, dash=None, width=1
    ):
        cx, cy = self.world_to_screen(0, 0)

        r = radius * self.base_scale * self.zoom

        self.canvas.create_oval(
            cx - r, cy - r,
            cx + r, cy + r,
            outline=color,
            dash=dash,
            width=width,
            tags="space_dyn",
        )

    def draw_orbit_guides(self):
        self.draw_world_circle(
            MARS_RADIUS, "#405C82",
            dash=(4, 5),
        )

        self.draw_world_circle(
            BELT_RADIUS, "#8D7652",
            dash=(4, 5),
            width=2,
        )

        self.draw_world_circle(
            2.1, "#494332",
            dash=(2, 6),
        )

        self.draw_world_circle(
            3.2, "#494332",
            dash=(2, 6),
        )

    def draw_asteroids(self):
        for asteroid in self.asteroids:
            angle = (
                asteroid["phase"]
                + asteroid["speed"] * self.visual_time
            )

            radius = asteroid["radius"]

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            sx, sy = self.world_to_screen(x, y)
            size = asteroid["size"]

            if (
                -10 <= sx <= SCENE_WIDTH + 10
                and -10 <= sy <= HEIGHT + 10
            ):
                self.canvas.create_oval(
                    sx - size, sy - size,
                    sx + size, sy + size,
                    fill=ASTEROID_COLOR,
                    outline="",
                    tags="space_dyn",
                )

    def draw_preview_orbit(self, state):
        if state["launched"]:
            return

        orbit = self.calculate_preview_orbit()

        if orbit is None:
            return

        _, _, mars_angle = self.get_mars_position()

        cos_a = math.cos(mars_angle)
        sin_a = math.sin(mars_angle)

        points = []

        for i in range(181):
            theta = 2 * math.pi * i / 180

            local_x = (
                orbit["center_x"]
                + orbit["a"] * math.cos(theta)
            )

            local_y = (
                orbit["b"] * math.sin(theta)
            )

            x = (
                local_x * cos_a
                - local_y * sin_a
            )

            y = (
                local_x * sin_a
                + local_y * cos_a
            )

            sx, sy = self.world_to_screen(x, y)
            points.extend((sx, sy))

        self.canvas.create_line(
            *points,
            fill=PREVIEW_COLOR,
            width=2,
            dash=(5, 4),
            tags="space_dyn",
        )

    def draw_trajectory(self, state):
        trajectory = state.get("trajectory", [])

        # Keep the path visible after the maneuver ends.
        if len(trajectory) < 2:
            return

        if (
            not state["launched"]
            and state["status"] == "ready"
        ):
            return

        points = []

        for x, y in trajectory:
            rotated_x, rotated_y = (
                self.rotate_orbital_position(x, y)
            )

            sx, sy = self.world_to_screen(
                rotated_x, rotated_y
            )

            points.extend((sx, sy))

        self.canvas.create_line(
            *points,
            fill=TRAJECTORY_COLOR,
            width=2,
            tags="space_dyn",
        )

    def draw_sun(self):
        x, y = self.world_to_screen(0, 0)

        self.canvas.create_oval(
            x - 25, y - 25,
            x + 25, y + 25,
            fill="#E6A53B",
            outline="",
            tags="space_dyn",
        )

        self.canvas.create_oval(
            x - 17, y - 17,
            x + 17, y + 17,
            fill="#FFD36B",
            outline="",
            tags="space_dyn",
        )

    def draw_mars(self):
        x, y, _ = self.get_mars_position()
        sx, sy = self.world_to_screen(x, y)

        self.canvas.create_oval(
            sx - 7, sy - 7,
            sx + 7, sy + 7,
            fill="#D98669",
            outline="",
            tags="space_dyn",
        )

    def draw_spacecraft(self, state):
        if state["status"] != "ready":
            x, y = self.rotate_orbital_position(
                state["x"], state["y"]
            )

            vx, vy = self.rotate_orbital_position(
                state["vx"], state["vy"]
            )
        else:
            x, y, angle = self.get_mars_position()

            orbital_speed = math.sqrt(
                SOLAR_MU / MARS_RADIUS
            )

            vx = -orbital_speed * math.sin(angle)
            vy = orbital_speed * math.cos(angle)

        sx, sy = self.world_to_screen(x, y)

        direction_angle = math.atan2(vy, vx)

        direction_x = math.cos(direction_angle)
        direction_y = -math.sin(direction_angle)

        perpendicular_x = -direction_y
        perpendicular_y = direction_x

        tip_x = sx + direction_x * 12
        tip_y = sy + direction_y * 12

        back_x = sx - direction_x * 8
        back_y = sy - direction_y * 8

        left_x = back_x + perpendicular_x * 6
        left_y = back_y + perpendicular_y * 6

        right_x = back_x - perpendicular_x * 6
        right_y = back_y - perpendicular_y * 6

        self.canvas.create_polygon(
            tip_x, tip_y,
            left_x, left_y,
            right_x, right_y,
            fill=TRAJECTORY_COLOR,
            outline=TEXT,
            tags="space_dyn",
        )

    def draw_labels(self):
        # Heading is already drawn by core.ui.
        # Keep only the orbit legend in the scene.
        self.canvas.create_text(
            20,
            HEIGHT - 30,
            text=(
                "Dashed cyan: predicted orbit  |  "
                "Solid cyan: spacecraft path"
            ),
            fill=MUTED,
            font=("Arial", 9),
            anchor="nw",
            tags="space_dyn",
        )

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):
        state = self.puzzle.get_state()

        self.info_var.set(
            f"Distance from Sun: {state['radius']:.3f} AU\n"
            f"Maximum distance: {state['max_radius']:.3f} AU\n"
            f"Target distance: {BELT_RADIUS:.2f} AU\n"
            f"Flight time: {state['time']:.3f} years\n"
            f"Camera zoom: {self.zoom:.2f}x"
        )

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy(self):
        self.stop_animation()
        super().destroy()


if __name__ == "__main__":
    root = tk.Tk()

    root.title("ASTRA — Asteroid Transfer Test")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = AsteroidRouteUI(root)
    screen.pack(fill="both", expand=True)

    root.mainloop()
