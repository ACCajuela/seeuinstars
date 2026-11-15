
import tkinter as tk

from core.ui import (
    ACCENT,
    FEEDBACK_COLOR,
    MINIGAME_MUTED as MUTED,
    MINIGAME_PANEL,
    MINIGAME_SUCCESS as SUCCESS,
    TITLE as TEXT,
    CosmoHint,
    MenuButton,
    draw_minigame_heading,
    draw_minigame_panel,
)

from puzzles.comet_spectrum import CometSpectrumPuzzle


# ============================================================
# ASTRA — Chapter 3B: Comet Spectroscopy
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 680

BG = "#101521"
OBSERVED = "#FFFFFF"
REFERENCE = "#77D9FF"

MIN_WAVELENGTH = 380
MAX_WAVELENGTH = 750


class CometSpectrumUI(tk.Frame):

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=BG)

        self.puzzle = CometSpectrumPuzzle()
        self.on_complete = on_complete
        self.on_back = on_back

        self.completed_notified = False
        self.hint_level = 0
        self.attempts = 0

        self.status_var = tk.StringVar(
            value=(
                "COSMO: Ada, a new comet has been detected! "
                "Compare its spectral lines with our "
                "reference library to identify its composition."
            )
        )

        self.info_var = tk.StringVar(value="")

        # Canvas-based selections, replacing the
        # original Tkinter Checkbuttons.
        self.substance_vars = {}
        self.substance_checks = {}

        self.build_ui()
        self.update_info()
        self.draw_scene()

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
            "CHAPTER 3 — COMET ANALYSIS",
            "Identify substances using spectral lines.",
        )

        draw_minigame_panel(c, "COMET\nSPECTRUM")

        x0, y0, x1, y1 = MINIGAME_PANEL
        cx = (x0 + x1) / 2

        c.create_text(
            cx, 119,
            text="Select the substances",
            font=("Arial", 11),
            fill=MUTED,
        )

        c.create_text(
            cx, 136,
            text="present in the comet:",
            font=("Arial", 11),
            fill=MUTED,
        )

        # Each substance gets an interactive Canvas row.
        state = self.puzzle.get_state()

        self.selection_top = 157
        self.selection_step = 30

        for index, (substance_id, data) in enumerate(
            state["substances"].items()
        ):
            y = self.selection_top + index * self.selection_step
            tag = f"substance_{substance_id}"

            rect = c.create_rectangle(
                x0 + 18, y - 11,
                x1 - 18, y + 13,
                fill="#263650",
                outline="#40526B",
                width=1,
                tags=(tag, "selection"),
            )

            marker = c.create_text(
                x0 + 30, y + 1,
                text="□",
                font=("Arial", 15, "bold"),
                fill=REFERENCE,
                anchor="w",
                tags=(tag, "selection"),
            )

            label = c.create_text(
                x0 + 54, y + 1,
                text=data["name"],
                font=("Arial", 10),
                fill=TEXT,
                anchor="w",
                tags=(tag, "selection"),
            )

            self.substance_vars[substance_id] = False
            self.substance_checks[substance_id] = {
                "rect": rect,
                "marker": marker,
                "label": label,
            }

            c.tag_bind(
                tag,
                "<Button-1>",
                lambda event, sid=substance_id:
                    self.toggle_substance(sid),
            )

            c.tag_bind(
                tag,
                "<Enter>",
                lambda event:
                    c.configure(cursor="hand2"),
            )

            c.tag_bind(
                tag,
                "<Leave>",
                lambda event:
                    c.configure(cursor=""),
            )

        self.analyze_button = MenuButton(
            c, cx, 335,
            "ANALYZE", self.analyze,
            width=160,
            height=36,
            font_size=11,
            primary=True,
        )

        MenuButton(
            c, cx, 378,
            "COSMO HINT", self.request_hint,
            width=160,
            height=36,
            font_size=11,
        )

        MenuButton(
            c, cx, 421,
            "NEW COMET", self.new_comet,
            width=160,
            height=36,
            font_size=11,
        )

        if self.on_back is not None:
            MenuButton(
                c, cx, 464,
                "BACK", self.go_back,
                width=160,
                height=34,
                font_size=11,
            )

        c.create_line(
            x0 + 20, 492,
            x1 - 20, 492,
            fill="#24324F",
            width=2,
        )

        self.info_item = c.create_text(
            x0 + 20, 503,
            anchor="nw",
            width=(x1 - x0) - 36,
            font=("Arial", 9),
            fill=MUTED,
        )

        self.info_var.trace_add(
            "write",
            lambda *_: c.itemconfigure(
                self.info_item,
                text=self.info_var.get(),
            ),
        )

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
            "missing_lines",
            "extra_lines",
            "incorrect",
        ):
            color = FEEDBACK_COLOR

        else:
            color = TEXT

        self.hint.set(self.status_var.get(), color)

    # ========================================================
    # COSMO
    # ========================================================

    def say(self, message):
        self.status_var.set("COSMO: " + message)

    def request_hint(self):
        if self.puzzle.completed:
            self.say(
                "Well done! Scientists use spectroscopy "
                "to study the chemical composition of "
                "distant objects by examining the "
                "wavelengths of light they emit or absorb."
            )
            return

        self.hint_level = min(self.hint_level + 1, 4)

        if self.hint_level == 1:
            self.say(
                "Each substance has a characteristic "
                "pattern of spectral lines. Compare the "
                "white observed lines with the cyan "
                "reference lines."
            )

        elif self.hint_level == 2:
            self.say(
                "The wavelength scale is measured in "
                "nanometers. Small differences can come "
                "from measurement noise. This puzzle "
                "allows a tolerance of 5 nm."
            )

        elif self.hint_level == 3:
            self.say(
                "Look for groups of three reference "
                "lines that match the observed spectrum. "
                "A single matching line is not enough "
                "to identify a substance reliably."
            )

        else:
            self.show_advanced_hint()

    def show_advanced_hint(self):
        state = self.puzzle.get_state()
        comparison = state["comparison"]

        if not state["selected_substances"]:
            self.say(
                "Start by finding a reference substance "
                "whose three lines appear in the observed "
                "spectrum. Select it and compare again."
            )
            return

        missing = comparison["missing"]
        extra = comparison["extra"]

        if missing > 0 and extra > 0:
            self.say(
                f"There are {missing} unmatched observed "
                f"lines and {extra} unmatched selected "
                "lines. Some substances may be missing, "
                "while others may be incorrect."
            )

        elif missing > 0:
            self.say(
                f"{missing} observed lines are still "
                "unmatched. Look for another reference "
                "pattern that explains them."
            )

        elif extra > 0:
            self.say(
                f"{extra} selected lines do not match "
                "the observation. Check whether one "
                "of your substances should be removed."
            )

        else:
            self.say(
                "All the lines match within the allowed "
                "tolerance. Submit your composition "
                "to verify the identification."
            )

    def contextual_feedback(self, state):
        status = state["status"]
        comparison = state["comparison"]

        if status == "success":
            names = [
                state["substances"][sid]["name"]
                for sid in state["selected_substances"]
            ]

            composition = ", ".join(names)

            self.say(
                f"Excellent work, Ada! We identified "
                f"{composition}. Each substance contributed "
                "a characteristic pattern of lines. "
                "Our reference spectra are fictional "
                "training data, but the scientific "
                "method is real!"
            )

        elif status == "missing_lines":
            self.say(
                f"{comparison['missing']} observed "
                "spectral line(s) are still unmatched. "
                "The comet may contain another substance. "
                "Compare the remaining wavelengths."
            )

        elif status == "extra_lines":
            self.say(
                f"{comparison['extra']} selected reference "
                "line(s) are not explained by the observed "
                "spectrum. You may have selected a "
                "substance that is not present."
            )

        else:
            self.say(
                "The selected composition is not correct. "
                "Compare the complete patterns rather "
                "than individual coincidences."
            )

    # ========================================================
    # Controls
    # ========================================================

    def toggle_substance(self, substance_id):
        self.puzzle.update({
            "type": "toggle",
            "substance": substance_id,
        })

        self.completed_notified = False

        self.say(
            "Selection updated. Compare the observed "
            "white lines with the selected cyan lines, "
            "then press ANALYZE."
        )

        self.update_info()
        self.draw_scene()

    def analyze(self):
        self.puzzle.update({
            "type": "submit",
        })

        self.attempts += 1

        state = self.puzzle.get_state()
        self.contextual_feedback(state)

        self.update_info()
        self.draw_scene()

        if (
            self.puzzle.validate()
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.after_idle(self.on_complete)

    def new_comet(self):
        self.puzzle.reset()
        self.completed_notified = False
        self.hint_level = 0

        self.say(
            "A new comet has been detected! Its "
            "composition may be different. Compare "
            "the new spectrum with the reference library."
        )

        self.update_info()
        self.draw_scene()

    def reset_simulation(self):
        # Compatibility with the original interface.
        self.new_comet()

    def go_back(self):
        if self.on_back is not None:
            self.on_back()

    # ========================================================
    # Wavelength visualization
    # ========================================================

    def wavelength_to_x(self, wavelength):
        left = 45
        right = SCENE_WIDTH - 35

        fraction = (
            (wavelength - MIN_WAVELENGTH)
            / (MAX_WAVELENGTH - MIN_WAVELENGTH)
        )

        return left + fraction * (right - left)

    def wavelength_to_rgb(self, wavelength):
        """
        Approximate visible-spectrum colors.
        Visualization only.
        """
        w = wavelength

        if w < 380 or w > 750:
            return "#222222"

        if w < 440:
            r = (440 - w) / 60
            g = 0
            b = 1

        elif w < 490:
            r = 0
            g = (w - 440) / 50
            b = 1

        elif w < 510:
            r = 0
            g = 1
            b = (510 - w) / 20

        elif w < 580:
            r = (w - 510) / 70
            g = 1
            b = 0

        elif w < 645:
            r = 1
            g = (645 - w) / 65
            b = 0

        else:
            r = 1
            g = 0
            b = 0

        return "#{:02x}{:02x}{:02x}".format(
            int(r * 255),
            int(g * 255),
            int(b * 255),
        )

    def draw_spectrum_bar(self, top, bottom):
        left = 45
        right = SCENE_WIDTH - 35

        for x in range(left, right):
            wavelength = (
                MIN_WAVELENGTH
                + (x - left)
                / (right - left)
                * (MAX_WAVELENGTH - MIN_WAVELENGTH)
            )

            color = self.wavelength_to_rgb(
                wavelength
            )

            self.canvas.create_line(
                x, top,
                x, bottom,
                fill=color,
                tags="spectrum_dyn",
            )

    def draw_spectral_lines(
        self, lines, top, bottom, color, width=2
    ):
        for wavelength in lines:
            x = self.wavelength_to_x(wavelength)

            self.canvas.create_line(
                x, top,
                x, bottom,
                fill=color,
                width=width,
                tags="spectrum_dyn",
            )

    # ========================================================
    # Rendering
    # ========================================================

    def draw_scene(self):
        # Preserve static panel, buttons and COSMO.
        self.canvas.delete("spectrum_dyn")

        state = self.puzzle.get_state()

        self.draw_stars()

        self.canvas.create_text(
            45, 115,
            text="OBSERVED COMET SPECTRUM",
            fill=TEXT,
            font=("Arial", 11, "bold"),
            anchor="nw",
            tags="spectrum_dyn",
        )

        self.draw_spectrum_bar(150, 205)

        self.draw_spectral_lines(
            state["observed_lines"],
            145, 210,
            OBSERVED,
            width=3,
        )

        self.draw_axis(220)

        self.canvas.create_text(
            45, 285,
            text="SELECTED REFERENCE LINES",
            fill=TEXT,
            font=("Arial", 11, "bold"),
            anchor="nw",
            tags="spectrum_dyn",
        )

        self.canvas.create_rectangle(
            45, 320,
            SCENE_WIDTH - 35, 375,
            fill="#182333",
            outline="#40526B",
            tags="spectrum_dyn",
        )

        self.draw_spectral_lines(
            state["selected_lines"],
            315, 380,
            REFERENCE,
            width=3,
        )

        self.draw_axis(390)

        self.canvas.create_text(
            45, 445,
            text="REFERENCE LIBRARY",
            fill=TEXT,
            font=("Arial", 11, "bold"),
            anchor="nw",
            tags="spectrum_dyn",
        )

        y = 475

        for substance_id, data in state["substances"].items():
            selected = (
                substance_id
                in state["selected_substances"]
            )

            color = SUCCESS if selected else MUTED

            lines_text = ", ".join(
                str(line) for line in data["lines"]
            )

            self.canvas.create_text(
                45, y,
                text=f"{data['name']}: {lines_text} nm",
                fill=color,
                font=("Arial", 9),
                anchor="nw",
                tags="spectrum_dyn",
            )

            y += 21

        self.update_selection_visuals(state)
        self.hint.raise_()

    def update_selection_visuals(self, state):
        selected = set(
            state["selected_substances"]
        )

        for substance_id, items in self.substance_checks.items():
            active = substance_id in selected

            self.substance_vars[substance_id] = active

            self.canvas.itemconfigure(
                items["rect"],
                fill="#34536A" if active else "#263650",
                outline=SUCCESS if active else "#40526B",
            )

            self.canvas.itemconfigure(
                items["marker"],
                text="☑" if active else "□",
                fill=SUCCESS if active else REFERENCE,
            )

            self.canvas.itemconfigure(
                items["label"],
                fill=SUCCESS if active else TEXT,
            )

    def draw_axis(self, y):
        for wavelength in range(400, 751, 50):
            x = self.wavelength_to_x(wavelength)

            self.canvas.create_text(
                x, y,
                text=str(wavelength),
                fill=MUTED,
                font=("Arial", 8),
                tags="spectrum_dyn",
            )

    def draw_stars(self):
        for i in range(45):
            x = (i * 113 + 37) % SCENE_WIDTH
            y = (i * 67 + 19) % HEIGHT

            self.canvas.create_oval(
                x, y,
                x + 2, y + 2,
                fill="#40526B",
                outline="",
                tags="spectrum_dyn",
            )

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):
        state = self.puzzle.get_state()
        comparison = state["comparison"]

        self.info_var.set(
            f"Observed lines: {comparison['total_observed']}\n"
            f"Selected lines: {comparison['total_selected']}\n"
            f"Matching lines: {comparison['matched']}\n"
            f"Missing lines: {comparison['missing']}\n"
            f"Extra lines: {comparison['extra']}\n"
            f"Tolerance: ±{state['tolerance']} nm"
        )


if __name__ == "__main__":
    root = tk.Tk()

    root.title("ASTRA — Comet Spectroscopy")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = CometSpectrumUI(root)
    screen.pack(fill="both", expand=True)

    root.mainloop()
