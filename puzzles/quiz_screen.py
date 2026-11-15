
import tkinter as tk

from puzzles.knowledge_quiz import KnowledgeQuiz


# ============================================================
# VISUAL
# ============================================================

BG = "#101827"
PANEL = "#1B2940"
OPTION_BG = "#263650"
OPTION_HOVER = "#344867"

TEXT = "#F1F5F9"
MUTED = "#A8B6CC"

ACCENT = "#7DD3FC"
SUCCESS = "#86EFAC"
ERROR = "#FCA5A5"

FONT = "Arial"

WIDTH = 900
HEIGHT = 600


# ============================================================
# QUIZ SCREEN
# ============================================================

class QuizScreen(tk.Frame):

    def __init__(
        self,
        master,
        on_finish=None,
        language="en",
        quiz=None
    ):
        super().__init__(master, bg=BG)

        self.on_finish = on_finish
        self.language = language
        self.quiz = quiz if quiz is not None else KnowledgeQuiz()

        self.answer_locked = False
        self.selected_option = None
        self.option_buttons = []
        self.result_visible = False

        self.build_interface()
        self.show_question()

    # ========================================================
    # LOCALIZATION
    # ========================================================

    def localized(self, value):
        if isinstance(value, dict):
            return value.get(
                self.language,
                value.get("en", "")
            )

        return str(value)

    def ui_text(self, en, pt):
        return pt if self.language == "pt_BR" else en

    # ========================================================
    # INTERFACE
    # ========================================================

    def build_interface(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        self.header = tk.Frame(
            self,
            bg=BG
        )

        self.header.pack(
            side="top",
            fill="x",
            padx=35,
            pady=(16, 8)
        )

        self.program_label = tk.Label(
            self.header,
            text="NASA JUNIOR ASTRONAUT PROGRAM",
            font=(FONT, 9, "bold"),
            fg=ACCENT,
            bg=BG,
            anchor="w"
        )

        self.program_label.pack(
            fill="x"
        )

        self.title_label = tk.Label(
            self.header,
            text=self.ui_text(
                "Astronaut Practice Test",
                "Simulado de Astronauta"
            ),
            font=(FONT, 21, "bold"),
            fg=TEXT,
            bg=BG,
            anchor="w"
        )

        self.title_label.pack(
            fill="x",
            pady=(3, 0)
        )

        self.progress_label = tk.Label(
            self.header,
            text="",
            font=(FONT, 10),
            fg=MUTED,
            bg=BG,
            anchor="w"
        )

        self.progress_label.pack(
            fill="x",
            pady=(8, 4)
        )

        self.progress_canvas = tk.Canvas(
            self.header,
            height=6,
            bg=OPTION_BG,
            highlightthickness=0
        )

        self.progress_canvas.pack(
            fill="x"
        )

        self.progress_canvas.bind(
            "<Configure>",
            lambda event: self.update_progress()
        )

        # ----------------------------------------------------
        # FOOTER - FIXED ACTION AREA
        # ----------------------------------------------------

        # Packed before the content so Tkinter reserves
        # its space even when the question is long.

        self.footer = tk.Frame(
            self,
            bg=BG
        )

        self.footer.pack(
            side="bottom",
            fill="x",
            padx=35,
            pady=(7, 16)
        )

        self.action_button = tk.Button(
            self.footer,
            text="",
            font=(FONT, 12, "bold"),
            bg=ACCENT,
            fg=BG,
            activebackground="#BAE6FD",
            activeforeground=BG,
            disabledforeground="#607080",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.handle_action
        )

        self.action_button.pack(
            fill="x",
            ipady=9
        )

        # ----------------------------------------------------
        # MAIN PANEL
        # ----------------------------------------------------

        self.content = tk.Frame(
            self,
            bg=PANEL
        )

        self.content.pack(
            side="top",
            fill="both",
            expand=True,
            padx=35,
            pady=(6, 0)
        )

        # The content is scrollable, but the action
        # button always remains visible.

        self.content_canvas = tk.Canvas(
            self.content,
            bg=PANEL,
            highlightthickness=0,
            bd=0
        )

        self.content_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar = tk.Scrollbar(
            self.content,
            orient="vertical",
            command=self.content_canvas.yview
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.content_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.inner = tk.Frame(
            self.content_canvas,
            bg=PANEL
        )

        self.inner_window = self.content_canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.inner.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.content_canvas.bind(
            "<Configure>",
            self.resize_content
        )

        # ----------------------------------------------------
        # QUESTION
        # ----------------------------------------------------

        self.question_label = tk.Label(
            self.inner,
            text="",
            font=(FONT, 15, "bold"),
            fg=TEXT,
            bg=PANEL,
            wraplength=720,
            justify="left",
            anchor="w"
        )

        self.question_label.pack(
            fill="x",
            padx=24,
            pady=(18, 12)
        )

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        self.options_frame = tk.Frame(
            self.inner,
            bg=PANEL
        )

        self.options_frame.pack(
            fill="x",
            padx=24
        )

        # ----------------------------------------------------
        # FEEDBACK
        # ----------------------------------------------------

        self.feedback_label = tk.Label(
            self.inner,
            text="",
            font=(FONT, 11),
            fg=MUTED,
            bg=PANEL,
            wraplength=720,
            justify="left",
            anchor="w"
        )

        self.feedback_label.pack(
            fill="x",
            padx=24,
            pady=(10, 20)
        )

        # ----------------------------------------------------
        # SCROLLING
        # ----------------------------------------------------

        self.content_canvas.bind(
            "<Enter>",
            self.bind_mousewheel
        )

        self.content_canvas.bind(
            "<Leave>",
            self.unbind_mousewheel
        )

    # ========================================================
    # SCROLLING
    # ========================================================

    def update_scroll_region(self, event=None):
        self.content_canvas.configure(
            scrollregion=self.content_canvas.bbox("all")
        )

    def resize_content(self, event):
        width = event.width

        self.content_canvas.itemconfigure(
            self.inner_window,
            width=width
        )

        wrap_width = max(200, width - 55)

        self.question_label.configure(
            wraplength=wrap_width
        )

        self.feedback_label.configure(
            wraplength=wrap_width
        )

        for button in self.option_buttons:
            button.configure(
                wraplength=wrap_width - 20
            )

    def bind_mousewheel(self, event=None):
        self.content_canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

    def unbind_mousewheel(self, event=None):
        self.content_canvas.unbind_all(
            "<MouseWheel>"
        )

    def on_mousewheel(self, event):
        self.content_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )

    def scroll_to_top(self):
        self.update_idletasks()

        self.content_canvas.yview_moveto(0)

    # ========================================================
    # PROGRESS
    # ========================================================

    def update_progress(self):
        total = self.quiz.total_questions
        current = self.quiz.current_index

        if total <= 0:
            return

        if self.result_visible:
            self.progress_label.configure(
                text=self.ui_text(
                    "Practice test finished",
                    "Simulado concluído"
                )
            )

            progress = 1.0

        else:
            display_number = min(current + 1, total)

            self.progress_label.configure(
                text=self.ui_text(
                    f"Question {display_number} of {total}",
                    f"Pergunta {display_number} de {total}"
                )
            )

            progress = current / total

        width = self.progress_canvas.winfo_width()

        if width <= 1:
            width = WIDTH - 70

        self.progress_canvas.delete("all")

        self.progress_canvas.create_rectangle(
            0,
            0,
            width,
            6,
            fill=OPTION_BG,
            outline=""
        )

        self.progress_canvas.create_rectangle(
            0,
            0,
            width * progress,
            6,
            fill=ACCENT,
            outline=""
        )

    # ========================================================
    # OPTIONS
    # ========================================================

    def clear_options(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        self.option_buttons = []

    # ========================================================
    # SHOW QUESTION
    # ========================================================

    def show_question(self):

        if self.quiz.finished:
            self.show_result()
            return

        self.result_visible = False
        self.answer_locked = False
        self.selected_option = None

        self.clear_options()

        question = self.quiz.get_current_question()

        self.question_label.configure(
            text=self.localized(
                question["question"]
            )
        )

        self.feedback_label.configure(
            text="",
            fg=MUTED
        )

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for index, option in enumerate(
            question["options"]
        ):
            option_text = self.localized(option)

            button = tk.Button(
                self.options_frame,
                text=f"{letters[index]}.  {option_text}",
                font=(FONT, 11),
                bg=OPTION_BG,
                fg=TEXT,
                activebackground=OPTION_HOVER,
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                anchor="w",
                justify="left",
                wraplength=680,
                cursor="hand2",
                command=lambda i=index: self.select_option(i)
            )

            button.pack(
                fill="x",
                pady=4,
                ipady=8,
                ipadx=10
            )

            self.option_buttons.append(button)

        self.action_button.configure(
            text=self.ui_text(
                "Check answer",
                "Conferir resposta"
            ),
            state="disabled",
            command=self.handle_action
        )

        self.update_progress()
        self.scroll_to_top()

    # ========================================================
    # SELECT OPTION
    # ========================================================

    def select_option(self, index):

        if self.answer_locked:
            return

        self.selected_option = index

        for i, button in enumerate(self.option_buttons):
            button.configure(
                bg=(
                    OPTION_HOVER
                    if i == index
                    else OPTION_BG
                )
            )

        self.action_button.configure(
            state="normal"
        )

    # ========================================================
    # ACTIONS
    # ========================================================

    def handle_action(self):

        if self.result_visible:
            self.finish()
            return

        if self.answer_locked:
            self.show_question()
            return

        self.submit_answer()

    # ========================================================
    # SUBMIT ANSWER
    # ========================================================

    def submit_answer(self):

        if self.selected_option is None:
            return

        if self.answer_locked:
            return

        question = self.quiz.get_current_question()

        result = self.quiz.submit_answer(
            self.selected_option
        )

        self.answer_locked = True

        correct_index = result["correct_index"]

        for index, button in enumerate(self.option_buttons):

            button.configure(
                state="disabled"
            )

            if index == correct_index:
                button.configure(
                    bg="#24543B",
                    disabledforeground=SUCCESS
                )

            elif index == self.selected_option:
                button.configure(
                    bg="#63333B",
                    disabledforeground=ERROR
                )

        if result["correct"]:
            prefix = self.ui_text(
                "Correct!",
                "Resposta correta!"
            )

            color = SUCCESS

        else:
            prefix = self.ui_text(
                "Almost!",
                "Quase!"
            )

            color = ERROR

        explanation = self.localized(
            question["explanation"]
        )

        self.feedback_label.configure(
            text=f"{prefix}\n\n{explanation}",
            fg=color
        )

        if self.quiz.finished:
            action_text = self.ui_text(
                "View Results",
                "Ver resultado"
            )
        else:
            action_text = self.ui_text(
                "Next question",
                "Próxima pergunta"
            )

        self.action_button.configure(
            text=action_text,
            state="normal",
            command=self.handle_action
        )

        self.update_progress()

        # Scroll to the explanation so the player
        # can read the educational feedback.
        self.update_idletasks()
        self.content_canvas.yview_moveto(1.0)

    # ========================================================
    # RESULTS
    # ========================================================

    def show_result(self):

        self.result_visible = True
        self.answer_locked = True

        self.clear_options()

        result = self.quiz.get_result()

        self.question_label.configure(
            text=self.ui_text(
                "Practice test finished!",
                "Simulado concluído!"
            )
        )

        score = result["score"]
        total = result["total"]

        score_label = tk.Label(
            self.options_frame,
            text=f"{score} / {total}",
            font=(FONT, 42, "bold"),
            fg=ACCENT,
            bg=PANEL
        )

        score_label.pack(
            pady=(15, 10)
        )

        percentage_label = tk.Label(
            self.options_frame,
            text=f'{result["percentage"]:.1f}%',
            font=(FONT, 14),
            fg=MUTED,
            bg=PANEL
        )

        percentage_label.pack(
            pady=(0, 12)
        )

        if result["passed"]:
            message = self.ui_text(
                "Great job, Ada! You passed the practice test.",
                "Muito bem, Ada! Você passou no simulado."
            )

            color = SUCCESS

        else:
            message = self.ui_text(
                "Keep going, Ada! Every mistake helps you learn something new.",
                "Continue, Ada! Cada erro ajuda você a aprender algo novo."
            )

            color = MUTED

        self.feedback_label.configure(
            text=message,
            fg=color
        )

        self.action_button.configure(
            text=self.ui_text(
                "Continue the story",
                "Continuar a história"
            ),
            state="normal",
            command=self.finish
        )

        self.update_progress()
        self.scroll_to_top()

    # ========================================================
    # FINISH
    # ========================================================

    def finish(self):

        if not self.quiz.finished:
            return

        result = self.quiz.get_result()

        print("[QUIZ] Assessment completed.")
        print(f'[QUIZ] Score: {result["score"]}/{result["total"]}')
        print(f'[QUIZ] Passed: {result["passed"]}')

        if self.on_finish:
            self.on_finish(result)

    # ========================================================
    # CLEANUP
    # ========================================================

    def destroy(self):
        self.unbind_mousewheel()
        super().destroy()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title("ASTRA - Knowledge Assessment")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)
    root.configure(bg=BG)

    def on_quiz_finish(result):
        print("[QUIZ] Finished!")
        print(result)
        root.destroy()

    screen = QuizScreen(
        root,
        on_finish=on_quiz_finish,
        language="en"
    )

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
