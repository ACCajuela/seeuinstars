
import tkinter as tk

from puzzles.comet_spectrum import CometSpectrumPuzzle


# ============================================================
# ASTRA — Chapter 3B: Comet Spectroscopy
#
# Temporary interface for Bri to customize.
# Each new comet has a randomly generated composition.
#
# NOTE:
# Spectral signatures are fictional educational data.
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 640

BG = "#101521"
PANEL = "#202B3D"
TEXT = "#F5F7FF"
MUTED = "#AABBD2"
ACCENT = "#F7C56B"
SUCCESS = "#91E4AE"
ERROR = "#FF9A91"

OBSERVED = "#FFFFFF"
REFERENCE = "#77D9FF"

MIN_WAVELENGTH = 380
MAX_WAVELENGTH = 750


class CometSpectrumUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = CometSpectrumPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.completed_notified = False

        self.status_var = tk.StringVar(
            value="New comet detected! Analyze its spectrum."
        )

        self.info_var = tk.StringVar()

        self.substance_vars = {}
        self.substance_checks = {}

        self.build_ui()
        self.update_info()
        self.draw_scene()

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
            text="COMET\nSPECTRUM",
            font=("Arial", 18, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(22, 12))

        tk.Label(
            self.panel,
            text="Select the substances\npresent in the comet:",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL,
            justify="center"
        ).pack(pady=(0, 12))

        state = self.puzzle.get_state()

        for substance_id, data in state["substances"].items():

            variable = tk.BooleanVar(value=False)

            self.substance_vars[substance_id] = variable

            check = tk.Checkbutton(
                self.panel,
                text=data["name"],
                variable=variable,
                command=lambda sid=substance_id:
                    self.toggle_substance(sid),
                font=("Arial", 10),
                fg=TEXT,
                bg=PANEL,
                activebackground=PANEL,
                activeforeground=ACCENT,
                selectcolor="#40526B",
                anchor="w",
                highlightthickness=0
            )

            check.pack(
                fill="x",
                padx=22,
                pady=3
            )

            self.substance_checks[substance_id] = check

        tk.Button(
            self.panel,
            text="ANALYZE",
            font=("Arial", 11, "bold"),
            bg="#B97843",
            fg=TEXT,
            relief="flat",
            command=self.analyze
        ).pack(
            fill="x",
            padx=20,
            pady=(20, 5),
            ipady=7
        )

        tk.Button(
            self.panel,
            text="NEW COMET",
            font=("Arial", 10, "bold"),
            bg="#46566B",
            fg=TEXT,
            relief="flat",
            command=self.new_comet
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
            wraplength=215
        ).pack(
            padx=18,
            pady=(16, 5),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=ACCENT,
            bg=PANEL,
            justify="center",
            wraplength=220
        ).pack(
            padx=12,
            pady=8
        )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    def toggle_substance(self, substance_id):

        self.puzzle.update({
            "type": "toggle",
            "substance": substance_id
        })

        self.completed_notified = False

        self.status_var.set(
            "Compare the lines, then press ANALYZE."
        )

        self.update_info()
        self.draw_scene()

    def analyze(self):

        self.puzzle.update({
            "type": "submit"
        })

        state = self.puzzle.get_state()
        status = state["status"]
        comparison = state["comparison"]

        if status == "success":

            self.status_var.set(
                "Correct! Comet composition identified."
            )

            if (
                not self.completed_notified
                and self.on_complete is not None
            ):
                self.completed_notified = True
                self.after_idle(self.on_complete)

        elif status == "missing_lines":

            self.status_var.set(
                f"{comparison['missing']} spectral line(s) "
                "are still missing."
            )

        elif status == "extra_lines":

            self.status_var.set(
                f"{comparison['extra']} extra spectral "
                "line(s) detected."
            )

        else:

            self.status_var.set(
                "Incorrect combination. Try again."
            )

        self.update_info()
        self.draw_scene()

    def new_comet(self):
        """
        Generate a new random comet and clear
        the previous player's selections.
        """

        self.puzzle.reset()

        for variable in self.substance_vars.values():
            variable.set(False)

        self.completed_notified = False

        self.status_var.set(
            "New comet detected! Analyze its spectrum."
        )

        self.update_info()
        self.draw_scene()

    def reset_simulation(self):
        # Compatibility with the previous interface.
        self.new_comet()

    def go_back(self):

        if self.on_back is not None:
            self.on_back()

    # --------------------------------------------------------
    # Wavelength visualization
    # --------------------------------------------------------

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
            int(b * 255)
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
                x,
                top,
                x,
                bottom,
                fill=color
            )

    def draw_spectral_lines(
        self,
        lines,
        top,
        bottom,
        color,
        width=2
    ):

        for wavelength in lines:

            x = self.wavelength_to_x(
                wavelength
            )

            self.canvas.create_line(
                x,
                top,
                x,
                bottom,
                fill=color,
                width=width
            )

    # --------------------------------------------------------
    # Rendering
    # --------------------------------------------------------

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.draw_stars()

        self.canvas.create_text(
            30,
            25,
            text="CHAPTER 3 — COMET ANALYSIS",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            30,
            58,
            text="Identify substances using spectral lines.",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

        # ----------------------------------------------------
        # Observed comet spectrum
        # ----------------------------------------------------

        self.canvas.create_text(
            45,
            115,
            text="OBSERVED COMET SPECTRUM",
            fill=TEXT,
            font=("Arial", 11, "bold"),
            anchor="nw"
        )

        self.draw_spectrum_bar(
            150,
            205
        )

        self.draw_spectral_lines(
            state["observed_lines"],
            145,
            210,
            OBSERVED,
            width=3
        )

        self.draw_axis(220)

        # ----------------------------------------------------
        # Selected reference spectrum
        # ----------------------------------------------------

        self.canvas.create_text(
            45,
            285,
            text="SELECTED REFERENCE LINES",
            fill=TEXT,
            font=("Arial", 11, "bold"),
            anchor="nw"
        )

        self.canvas.create_rectangle(
            45,
            320,
            SCENE_WIDTH - 35,
            375,
            fill="#182333",
            outline="#40526B"
        )

        self.draw_spectral_lines(
            state["selected_lines"],
            315,
            380,
            REFERENCE,
            width=3
        )

        self.draw_axis(390)

        # ----------------------------------------------------
        # Reference library
        # ----------------------------------------------------

        self.canvas.create_text(
            45,
            450,
            text="REFERENCE LIBRARY",
            fill=TEXT,
            font=("Arial", 11, "bold"),
            anchor="nw"
        )

        y = 480

        for substance_id, data in state["substances"].items():

            selected = (
                substance_id
                in state["selected_substances"]
            )

            color = (
                SUCCESS if selected else MUTED
            )

            lines_text = ", ".join(
                str(line)
                for line in data["lines"]
            )

            self.canvas.create_text(
                45,
                y,
                text=(
                    f"{data['name']}: "
                    f"{lines_text} nm"
                ),
                fill=color,
                font=("Arial", 9),
                anchor="nw"
            )

            y += 21

    def draw_axis(self, y):

        for wavelength in range(400, 751, 50):

            x = self.wavelength_to_x(
                wavelength
            )

            self.canvas.create_text(
                x,
                y,
                text=str(wavelength),
                fill=MUTED,
                font=("Arial", 8)
            )

    def draw_stars(self):

        for i in range(45):

            x = (i * 113 + 37) % SCENE_WIDTH
            y = (i * 67 + 19) % HEIGHT

            self.canvas.create_oval(
                x,
                y,
                x + 2,
                y + 2,
                fill="#40526B",
                outline=""
            )

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    def update_info(self):

        state = self.puzzle.get_state()
        comparison = state["comparison"]

        self.info_var.set(
            f"Observed lines: "
            f"{comparison['total_observed']}\n"
            f"Selected lines: "
            f"{comparison['total_selected']}\n"
            f"Matching lines: "
            f"{comparison['matched']}\n"
            f"Missing lines: "
            f"{comparison['missing']}\n"
            f"Extra lines: "
            f"{comparison['extra']}\n\n"
            f"Tolerance: ±{state['tolerance']} nm"
        )


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "ASTRA — Random Comet Spectroscopy"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(False, False)

    screen = CometSpectrumUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
