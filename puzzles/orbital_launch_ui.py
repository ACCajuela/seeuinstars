
import math
import tkinter as tk

from core.ui import (
    ACCENT, FEEDBACK_COLOR, IMAGES_DIR, MINIGAME_MUTED as MUTED,
    MINIGAME_PANEL, MINIGAME_SUCCESS as SUCCESS, TITLE as TEXT,
    CanvasLabel, CanvasSlider, CosmoHint, MenuButton,
    draw_minigame_heading, draw_minigame_panel, fit_content,
)
from puzzles.orbital_launch import OrbitalLaunchPuzzle


# ============================================================
# ASTRA — Chapter 1: Orbital Launch
# Visual com a identidade do jogo (cores, botões e painel de core/ui.py).
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 680

# Imagem da Terra (PNG com fundo transparente). Ela é ajustada sozinha
# para o tamanho da Terra na física. Sem o arquivo, a Terra é desenhada.
EARTH_IMAGE = IMAGES_DIR / "terra.png"

# Cores da cena (as cores gerais vêm de core/ui.py)
SPACE_BG = "#0A1120"
STAR_COLORS = ("#FFFFFF", "#CBD5E1", "#8BD3FF", "#64748B")
EARTH_OCEAN = "#2F6FAE"
EARTH_LAND = "#4FAF7A"
EARTH_GLOW = ("#122844", "#18375C", "#1F4A78")  # atmosfera, de fora p/ dentro
SHIP_COLOR = "#FFFFFF"
FLAME_COLOR = "#FFB65C"
ORBIT_COLOR = "#8BD3FF"


class OrbitalLaunchUI(tk.Frame):

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=SPACE_BG)

        self.puzzle = OrbitalLaunchPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = False
        self.after_id = None
        self.completed_notified = False

        self.scale_factor = 0.000025

        self.center_x = 340
        self.center_y = 265

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
            width=WIDTH,
            height=HEIGHT,
            bg=SPACE_BG,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)
        c = self.canvas

        # Cenário fixo (desenhado uma vez só)
        self.draw_stars()
        self.draw_earth()
        draw_minigame_heading(
            c,
            "CHAPTER 1 — THE WRONG SHIP",
            "Find the correct orbital velocity."
        )

        # Painel lateral
        draw_minigame_panel(c, "ORBITAL\nLAUNCH")
        x0, y0, x1, y1 = MINIGAME_PANEL
        cx = (x0 + x1) / 2

        c.create_text(cx, 135, text="Initial velocity",
                      font=("Arial", 11), fill=MUTED)

        self.velocity_label = CanvasLabel(c, c.create_text(
            cx, 165, text="7.67 km/s",
            font=("Arial", 20, "bold"), fill=ACCENT
        ))

        self.velocity_slider = CanvasSlider(
            c, x0 + 22, 205, (x1 - x0) - 44,
            from_=0, to=15000, resolution=10,
            variable=self.velocity_var,
            command=self.on_velocity_change
        )

        self.start_button = MenuButton(
            c, cx, 260, "LAUNCH", self.start_simulation,
            width=160, height=44, font_size=13, primary=True
        )

        MenuButton(
            c, cx, 312, "RESET", self.reset_simulation,
            width=160, height=40, font_size=12
        )

        if self.on_back is not None:
            MenuButton(
                c, cx, 360, "BACK", self.go_back,
                width=160, height=40, font_size=12
            )

        c.create_line(x0 + 20, 392, x1 - 20, 392, fill="#24324F", width=2)

        info_item = c.create_text(
            x0 + 22, 408, anchor="nw", width=(x1 - x0) - 40,
            font=("Arial", 10), fill=MUTED
        )
        self.info_var.trace_add(
            "write",
            lambda *_: c.itemconfigure(info_item, text=self.info_var.get())
        )

        # COSMO comenta o resultado no balão
        self.hint = CosmoHint(c, right=SCENE_WIDTH - 20)
        self.status_var.trace_add("write", lambda *_: self.show_status())
        self.show_status()

    def show_status(self):
        """Mostra a mensagem no balão do COSMO, colorida pelo resultado."""
        status = self.puzzle.get_state()["status"]

        if status == "stable_orbit":
            color = SUCCESS
        elif status in ("collision", "escape", "elliptical_orbit"):
            color = FEEDBACK_COLOR
        else:
            color = TEXT

        self.hint.set(self.status_var.get(), color)

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

        # Apaga só o que se move; cenário e painel ficam.
        self.canvas.delete("dyn")

        self.draw_trajectory()
        self.draw_ship()

        self.hint.raise_()

    def draw_stars(self):

        # Posições fixas (sempre as mesmas a cada partida).
        for i in range(90):

            x = (i * 97 + 31) % SCENE_WIDTH
            y = (i * 157 + 53) % HEIGHT

            radius = 1 if i % 3 else 2
            color = STAR_COLORS[i % len(STAR_COLORS)]

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline=""
            )

    def draw_earth(self):

        c = self.canvas
        cx, cy = self.center_x, self.center_y

        radius = (
            self.puzzle.EARTH_RADIUS
            * self.scale_factor
        )

        # Atmosfera: anéis de brilho em volta do planeta
        for i, color in enumerate(EARTH_GLOW):
            r = radius + 18 - i * 6
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          fill=color, outline="")

        # Imagem da Terra, com o planeta do tamanho exato da física
        if EARTH_IMAGE.exists():
            self.earth_img, box = fit_content(EARTH_IMAGE, radius * 2)
            x0, y0, x1, y1 = box
            c.create_image(
                cx - (x0 + x1) / 2, cy - (y0 + y1) / 2,
                image=self.earth_img, anchor="nw"
            )
            return

        # Sem imagem: Terra desenhada
        c.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            fill=EARTH_OCEAN, outline=ACCENT, width=2
        )

        # Continentes (formas simples dentro do planeta)
        for dx, dy, w, h in (
            (-70, -60, 70, 45), (-30, -85, 45, 22), (20, 10, 80, 55),
            (60, -40, 40, 28), (-90, 30, 45, 40), (-20, 80, 55, 25),
        ):
            c.create_oval(
                cx + dx - w / 2, cy + dy - h / 2,
                cx + dx + w / 2, cy + dy + h / 2,
                fill=EARTH_LAND, outline=""
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
            dash=(6, 4),
            tags="dyn"
        )

    def draw_ship(self):

        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["x"],
            state["y"]
        )

        # Nave apontando na direção do movimento
        if state["vx"] or state["vy"]:
            angle = math.atan2(-state["vy"], state["vx"])
        else:
            angle = -math.pi / 2  # parada: aponta para cima (direção do lançamento)

        def point(forward, side):
            return (
                x + forward * math.cos(angle) - side * math.sin(angle),
                y + forward * math.sin(angle) + side * math.cos(angle),
            )

        if self.running:
            self.canvas.create_polygon(
                *point(-8, -5), *point(-20, 0), *point(-8, 5),
                fill=FLAME_COLOR, outline="", tags="dyn"
            )

        self.canvas.create_polygon(
            *point(13, 0), *point(-9, -8), *point(-5, 0), *point(-9, 8),
            fill=SHIP_COLOR, outline=ACCENT, width=2, tags="dyn"
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
