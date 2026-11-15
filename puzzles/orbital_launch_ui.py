
import math
import tkinter as tk

from core.ui import (
    ACCENT,
    FEEDBACK_COLOR,
    IMAGES_DIR,
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
    fit_content,
)

from puzzles.orbital_launch import OrbitalLaunchPuzzle


# ============================================================
# ASTRA — Chapter 1: Orbital Launch
# Bilingual interface: English / Brazilian Portuguese
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 680

EARTH_IMAGE = IMAGES_DIR / "terra.png"

SPACE_BG = "#0A1120"
STAR_COLORS = ("#FFFFFF", "#CBD5E1", "#8BD3FF", "#64748B")
EARTH_OCEAN = "#2F6FAE"
EARTH_LAND = "#4FAF7A"
EARTH_GLOW = ("#122844", "#18375C", "#1F4A78")
SHIP_COLOR = "#FFFFFF"
FLAME_COLOR = "#FFB65C"
ORBIT_COLOR = "#8BD3FF"


# ============================================================
# LOCALIZATION
# ============================================================

TRANSLATIONS = {
    "en": {
        "chapter": "CHAPTER 1 — THE WRONG SHIP",
        "subtitle": "Find the correct orbital velocity.",
        "panel": "ORBITAL\nLAUNCH",
        "initial_velocity": "Initial velocity",
        "launch": "LAUNCH",
        "hint": "COSMO HINT",
        "reset": "RESET",
        "back": "BACK",
        "altitude": "Altitude",
        "time": "Time",
        "circular_speed": "Circular speed",
        "escape_speed": "Escape speed",

        "intro": (
            "Ada, we need a stable orbit around Earth. "
            "Choose a tangential velocity and launch."
        ),
        "hint_running": (
            "The simulation is running. Watch the path: "
            "does the spacecraft curve around Earth, "
            "fall toward it, or move away?"
        ),
        "hint_completed": (
            "Excellent work, Ada! Gravity continuously "
            "changes the direction of our velocity. "
            "That's why an orbit is a continuous fall "
            "around Earth rather than a fall into it."
        ),
        "hint_1": (
            "Gravity pulls the spacecraft toward Earth. "
            "A sideways velocity makes it move forward "
            "while gravity bends its path."
        ),
        "hint_2": (
            "Too little speed makes the orbit dip toward "
            "Earth. Too much speed can produce a very "
            "stretched orbit or even an escape trajectory."
        ),
        "hint_3": (
            "Look at the circular speed displayed on "
            "the panel. It is calculated from Earth's "
            "gravity and our starting distance."
        ),
        "hint_4": (
            "At 400 km altitude, circular speed is "
            "approximately {speed} km/s. "
            "Try setting the slider near that value."
        ),
        "collision": (
            "Our sideways velocity was too low. "
            "Gravity pulled the spacecraft into Earth. "
            "Try increasing the initial velocity."
        ),
        "escape": (
            "We exceeded the local escape speed. "
            "The spacecraft has enough energy to "
            "leave Earth's gravitational orbit. "
            "Try reducing the velocity."
        ),
        "elliptical_low": (
            "The spacecraft remained gravitationally "
            "bound, but its orbit dips too close to "
            "Earth. Increase the initial velocity "
            "toward circular speed."
        ),
        "elliptical_high": (
            "The spacecraft is in an elongated orbit. "
            "We launched faster than circular speed. "
            "Try reducing the velocity slightly."
        ),
        "elliptical_other": (
            "The orbit is not circular enough. "
            "Try adjusting the velocity in smaller steps."
        ),
        "stable_orbit": (
            "Orbital insertion successful! The spacecraft "
            "moves sideways fast enough for gravity to "
            "curve its path around Earth. "
            "We have achieved a stable orbit!"
        ),
        "simulation_complete": (
            "Simulation complete. Let's review "
            "the initial velocity and try again."
        ),
        "velocity_escape": (
            "That velocity is at or above escape speed. "
            "The spacecraft may leave Earth's orbit."
        ),
        "velocity_low": (
            "That is quite slow for this altitude. "
            "Gravity may pull the spacecraft into Earth."
        ),
        "velocity_high": (
            "That is faster than circular speed. "
            "Expect a more elongated orbit."
        ),
        "velocity_near": (
            "This velocity is closer to the circular "
            "orbit range. Launch and observe the path."
        ),
        "launch_started": (
            "Launch initiated. Observe how Earth's gravity "
            "changes the spacecraft's trajectory."
        ),
        "simulation_reset": (
            "Simulation reset. Adjust the initial velocity "
            "and launch again. You can ask me for a hint."
        ),
    },

    "pt_BR": {
        "chapter": "CAPÍTULO 1 — A NAVE ERRADA",
        "subtitle": "Encontre a velocidade orbital correta.",
        "panel": "LANÇAMENTO\nORBITAL",
        "initial_velocity": "Velocidade inicial",
        "launch": "LANÇAR",
        "hint": "DICA DO COSMO",
        "reset": "REINICIAR",
        "back": "VOLTAR",
        "altitude": "Altitude",
        "time": "Tempo",
        "circular_speed": "Velocidade circular",
        "escape_speed": "Velocidade de escape",

        "intro": (
            "Ada, precisamos estabelecer uma órbita estável "
            "ao redor da Terra. Escolha uma velocidade "
            "tangencial e inicie o lançamento."
        ),
        "hint_running": (
            "A simulação está em andamento. Observe a "
            "trajetória: a nave contorna a Terra, cai "
            "em direção a ela ou se afasta?"
        ),
        "hint_completed": (
            "Excelente trabalho, Ada! A gravidade altera "
            "continuamente a direção da nossa velocidade. "
            "Por isso, uma órbita é uma queda contínua "
            "ao redor da Terra, e não diretamente sobre ela."
        ),
        "hint_1": (
            "A gravidade atrai a nave em direção à Terra. "
            "Uma velocidade lateral faz a nave avançar "
            "enquanto a gravidade curva sua trajetória."
        ),
        "hint_2": (
            "Uma velocidade muito baixa faz a órbita "
            "se aproximar da Terra. Uma velocidade "
            "muito alta pode produzir uma órbita "
            "alongada ou até uma trajetória de escape."
        ),
        "hint_3": (
            "Observe a velocidade circular indicada "
            "no painel. Ela é calculada a partir "
            "da gravidade terrestre e da nossa "
            "distância inicial ao centro da Terra."
        ),
        "hint_4": (
            "A 400 km de altitude, a velocidade circular "
            "é de aproximadamente {speed} km/s. "
            "Tente ajustar o controle para um valor próximo."
        ),
        "collision": (
            "Nossa velocidade lateral estava muito baixa. "
            "A gravidade fez a nave colidir com a Terra. "
            "Tente aumentar a velocidade inicial."
        ),
        "escape": (
            "Ultrapassamos a velocidade de escape local. "
            "A nave possui energia suficiente para escapar "
            "da atração gravitacional terrestre. "
            "Tente diminuir a velocidade."
        ),
        "elliptical_low": (
            "A nave permaneceu gravitacionalmente ligada "
            "à Terra, mas sua órbita passa muito perto "
            "do planeta. Aumente a velocidade inicial "
            "em direção à velocidade circular."
        ),
        "elliptical_high": (
            "A nave entrou em uma órbita alongada. "
            "Partimos com velocidade superior à "
            "velocidade circular. Tente reduzi-la "
            "um pouco."
        ),
        "elliptical_other": (
            "A órbita ainda não está suficientemente "
            "circular. Tente ajustar a velocidade "
            "em incrementos menores."
        ),
        "stable_orbit": (
            "Inserção orbital bem-sucedida! A nave se "
            "desloca lateralmente rápido o suficiente "
            "para que a gravidade curve sua trajetória "
            "ao redor da Terra. Alcançamos uma órbita estável!"
        ),
        "simulation_complete": (
            "Simulação concluída. Vamos revisar "
            "a velocidade inicial e tentar novamente."
        ),
        "velocity_escape": (
            "Essa velocidade é igual ou superior à "
            "velocidade de escape. A nave pode "
            "abandonar a órbita terrestre."
        ),
        "velocity_low": (
            "Essa velocidade é bastante baixa para "
            "a altitude atual. A gravidade pode "
            "fazer a nave colidir com a Terra."
        ),
        "velocity_high": (
            "Essa velocidade é superior à velocidade "
            "circular. Espere uma órbita mais alongada."
        ),
        "velocity_near": (
            "Essa velocidade está mais próxima "
            "da faixa necessária para uma órbita "
            "circular. Inicie o lançamento e "
            "observe a trajetória."
        ),
        "launch_started": (
            "Lançamento iniciado. Observe como a "
            "gravidade terrestre modifica "
            "a trajetória da nave."
        ),
        "simulation_reset": (
            "Simulação reiniciada. Ajuste a velocidade "
            "inicial e tente novamente. Você também "
            "pode me pedir uma dica."
        ),
    },
}


class OrbitalLaunchUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None,
        language="en"
    ):
        super().__init__(master, bg=SPACE_BG)

        self.language = (
            language if language in TRANSLATIONS else "en"
        )

        self.strings = TRANSLATIONS[self.language]

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
        self.earth_img = None

        # COSMO state
        self.hint_level = 0
        self.attempts = 0
        self.last_result = None

        # Start away from the exact answer.
        self.velocity_var = tk.DoubleVar(value=6000)

        self.status_var = tk.StringVar(
            value="COSMO: " + self.tr("intro")
        )

        self.info_var = tk.StringVar(value="")

        self.build_ui()
        self.on_velocity_change(self.velocity_var.get())
        self.update_info()
        self.draw_scene()

    # ========================================================
    # LOCALIZATION
    # ========================================================

    def tr(self, key, **kwargs):
        text = self.strings.get(
            key,
            TRANSLATIONS["en"].get(key, key)
        )

        if kwargs:
            return text.format(**kwargs)

        return text

    def format_number(self, value, decimals=2):
        number = f"{value:.{decimals}f}"

        if self.language == "pt_BR":
            return number.replace(".", ",")

        return number

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):
        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=SPACE_BG,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        c = self.canvas

        self.draw_stars()
        self.draw_earth()

        draw_minigame_heading(
            c,
            self.tr("chapter"),
            self.tr("subtitle"),
        )

        draw_minigame_panel(
            c,
            self.tr("panel")
        )

        x0, y0, x1, y1 = MINIGAME_PANEL
        cx = (x0 + x1) / 2

        c.create_text(
            cx,
            130,
            text=self.tr("initial_velocity"),
            font=("Arial", 11),
            fill=MUTED,
        )

        self.velocity_label = CanvasLabel(
            c,
            c.create_text(
                cx,
                160,
                text=self.format_number(6.0) + " km/s",
                font=("Arial", 20, "bold"),
                fill=ACCENT,
            ),
        )

        self.velocity_slider = CanvasSlider(
            c,
            x0 + 22,
            195,
            (x1 - x0) - 44,
            from_=0,
            to=15000,
            resolution=10,
            variable=self.velocity_var,
            command=self.on_velocity_change,
        )

        self.start_button = MenuButton(
            c,
            cx,
            245,
            self.tr("launch"),
            self.start_simulation,
            width=160,
            height=40,
            font_size=12,
            primary=True,
        )

        self.hint_button = MenuButton(
            c,
            cx,
            293,
            self.tr("hint"),
            self.request_hint,
            width=160,
            height=38,
            font_size=11,
        )

        MenuButton(
            c,
            cx,
            339,
            self.tr("reset"),
            self.reset_simulation,
            width=160,
            height=38,
            font_size=11,
        )

        if self.on_back is not None:
            MenuButton(
                c,
                cx,
                383,
                self.tr("back"),
                self.go_back,
                width=160,
                height=36,
                font_size=11,
            )

        c.create_line(
            x0 + 20,
            420,
            x1 - 20,
            420,
            fill="#24324F",
            width=2,
        )

        info_item = c.create_text(
            x0 + 22,
            435,
            anchor="nw",
            width=(x1 - x0) - 40,
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

        # Reuse the existing COSMO speech bubble.
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

        if status == "stable_orbit":
            color = SUCCESS
        elif status in (
            "collision",
            "escape",
            "elliptical_orbit",
        ):
            color = FEEDBACK_COLOR
        else:
            color = TEXT

        self.hint.set(self.status_var.get(), color)

    # ========================================================
    # COSMO — EDUCATIONAL GUIDANCE
    # ========================================================

    def say(self, message):
        self.status_var.set("COSMO: " + message)

    def request_hint(self):
        """
        Progressive hints about orbital mechanics.
        """

        if self.running:
            self.say(self.tr("hint_running"))
            return

        if self.puzzle.completed:
            self.say(self.tr("hint_completed"))
            return

        self.hint_level = min(
            self.hint_level + 1,
            4
        )

        if self.hint_level == 1:
            self.say(self.tr("hint_1"))

        elif self.hint_level == 2:
            self.say(self.tr("hint_2"))

        elif self.hint_level == 3:
            self.say(self.tr("hint_3"))

        else:
            circular_kms = (
                self.puzzle.circular_speed / 1000
            )

            self.say(
                self.tr(
                    "hint_4",
                    speed=self.format_number(circular_kms)
                )
            )

    def contextual_feedback(self, status):
        """
        Explain the simulation result.
        """

        selected_speed = self.velocity_var.get()
        circular_speed = self.puzzle.circular_speed

        if status == "collision":
            self.say(self.tr("collision"))

        elif status == "escape":
            self.say(self.tr("escape"))

        elif status == "elliptical_orbit":

            if selected_speed < circular_speed:
                self.say(self.tr("elliptical_low"))

            elif selected_speed > circular_speed:
                self.say(self.tr("elliptical_high"))

            else:
                self.say(self.tr("elliptical_other"))

        elif status == "stable_orbit":
            self.say(self.tr("stable_orbit"))

        else:
            self.say(self.tr("simulation_complete"))

        self.last_result = status

    # ========================================================
    # CONTROLS
    # ========================================================

    def on_velocity_change(self, value):
        velocity = float(value)

        self.velocity_label.config(
            text=(
                self.format_number(velocity / 1000)
                + " km/s"
            )
        )

        if self.running:
            return

        if self.hint_level == 0:
            return

        circular_speed = self.puzzle.circular_speed
        escape_speed = self.puzzle.escape_speed

        if velocity >= escape_speed:
            self.say(self.tr("velocity_escape"))

        elif velocity < circular_speed * 0.85:
            self.say(self.tr("velocity_low"))

        elif velocity > circular_speed * 1.15:
            self.say(self.tr("velocity_high"))

        else:
            self.say(self.tr("velocity_near"))

    def start_simulation(self):
        if self.running:
            return

        self.puzzle.reset()
        self.trajectory.clear()
        self.completed_notified = False

        velocity = self.velocity_var.get()

        self.puzzle.update({
            "type": "launch",
            "velocity": velocity,
        })

        self.attempts += 1
        self.running = True

        self.velocity_slider.config(state="disabled")
        self.start_button.config(state="disabled")

        self.say(self.tr("launch_started"))

        self.animate()

    def reset_simulation(self):
        self.stop_animation()

        self.puzzle.reset()
        self.trajectory.clear()

        self.completed_notified = False
        self.last_result = None

        self.velocity_slider.config(state="normal")
        self.start_button.config(state="normal")

        # Preserve hints and selected velocity.
        self.say(self.tr("simulation_reset"))

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

    # ========================================================
    # SIMULATION
    # ========================================================

    def animate(self):
        if not self.running:
            return

        for _ in range(5):
            self.puzzle.update({
                "type": "tick",
                "dt": 10,
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
            self.animate,
        )

    def finish_simulation(self):
        self.running = False
        self.after_id = None

        self.velocity_slider.config(state="normal")
        self.start_button.config(state="normal")

        state = self.puzzle.get_state()

        self.contextual_feedback(state["status"])

        if (
            self.puzzle.validate()
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.after_idle(self.on_complete)

    # ========================================================
    # RENDERING
    # ========================================================

    def world_to_screen(self, x, y):
        return (
            self.center_x + x * self.scale_factor,
            self.center_y - y * self.scale_factor,
        )

    def draw_scene(self):
        self.canvas.delete("dyn")

        self.draw_trajectory()
        self.draw_ship()

        self.hint.raise_()

    def draw_stars(self):
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
                outline="",
            )

    def draw_earth(self):
        c = self.canvas
        cx, cy = self.center_x, self.center_y

        radius = (
            self.puzzle.EARTH_RADIUS
            * self.scale_factor
        )

        for i, color in enumerate(EARTH_GLOW):
            r = radius + 18 - i * 6

            c.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill=color,
                outline="",
            )

        if EARTH_IMAGE.exists():
            self.earth_img, box = fit_content(
                EARTH_IMAGE,
                radius * 2,
            )

            x0, y0, x1, y1 = box

            c.create_image(
                cx - (x0 + x1) / 2,
                cy - (y0 + y1) / 2,
                image=self.earth_img,
                anchor="nw",
            )
            return

        c.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=EARTH_OCEAN,
            outline=ACCENT,
            width=2,
        )

        for dx, dy, w, h in (
            (-70, -60, 70, 45),
            (-30, -85, 45, 22),
            (20, 10, 80, 55),
            (60, -40, 40, 28),
            (-90, 30, 45, 40),
            (-20, 80, 55, 25),
        ):
            c.create_oval(
                cx + dx - w / 2,
                cy + dy - h / 2,
                cx + dx + w / 2,
                cy + dy + h / 2,
                fill=EARTH_LAND,
                outline="",
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
            tags="dyn",
        )

    def draw_ship(self):
        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["x"],
            state["y"],
        )

        if state["vx"] or state["vy"]:
            angle = math.atan2(
                -state["vy"],
                state["vx"],
            )
        else:
            angle = -math.pi / 2

        def point(forward, side):
            return (
                x
                + forward * math.cos(angle)
                - side * math.sin(angle),
                y
                + forward * math.sin(angle)
                + side * math.cos(angle),
            )

        if self.running:
            self.canvas.create_polygon(
                *point(-8, -5),
                *point(-20, 0),
                *point(-8, 5),
                fill=FLAME_COLOR,
                outline="",
                tags="dyn",
            )

        self.canvas.create_polygon(
            *point(13, 0),
            *point(-9, -8),
            *point(-5, 0),
            *point(-9, 8),
            fill=SHIP_COLOR,
            outline=ACCENT,
            width=2,
            tags="dyn",
        )

    # ========================================================
    # INFORMATION
    # ========================================================

    def update_info(self):
        state = self.puzzle.get_state()

        altitude = max(
            0,
            state["altitude"] / 1000,
        )

        self.info_var.set(
            f"{self.tr('altitude')}: "
            f"{self.format_number(altitude, 0)} km\n"

            f"{self.tr('time')}: "
            f"{self.format_number(state['time'], 0)} s\n\n"

            f"{self.tr('circular_speed')}:\n"
            f"{self.format_number(state['circular_speed'] / 1000)} km/s\n\n"

            f"{self.tr('escape_speed')}:\n"
            f"{self.format_number(state['escape_speed'] / 1000)} km/s"
        )

    def destroy(self):
        self.stop_animation()
        super().destroy()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()

    root.title("ASTRA — Orbital Launch Test")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = OrbitalLaunchUI(
        root,
        language="pt_BR"
    )

    screen.pack(fill="both", expand=True)

    root.mainloop()
