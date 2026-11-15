
import json
from pathlib import Path


class KnowledgeQuiz:
    """
    Gerencia um quiz de conhecimentos científicos.

    Responsabilidades:
    - Carregar perguntas
    - Registrar respostas
    - Calcular pontuação
    - Verificar aprovação
    - Reiniciar a avaliação
    """

    def __init__(self, filename=None):
        self.project_root = Path(__file__).resolve().parent.parent

        if filename is None:
            filename = (
                self.project_root
                / "puzzles"
                / "knowledge_questions.json"
            )

        self.filename = Path(filename)

        with open(
            self.filename,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        self.title_key = data.get(
            "title_key",
            "chapter_00.quiz_title"
        )

        self.questions = data["questions"]

        self.passing_score = data.get(
            "passing_score",
            len(self.questions)
        )

        if not self.questions:
            raise ValueError(
                "Quiz must contain questions."
            )

        self.reset()

    # ========================================================
    # ESTADO DO QUIZ
    # ========================================================

    def reset(self):
        self.current_index = 0
        self.answers = []
        self.score = 0

    @property
    def total_questions(self):
        return len(self.questions)

    @property
    def finished(self):
        return self.current_index >= self.total_questions

    @property
    def passed(self):
        return (
            self.finished
            and self.score >= self.passing_score
        )

    # ========================================================
    # QUESTÕES
    # ========================================================

    def get_current_question(self):
        if self.finished:
            return None

        return self.questions[self.current_index]

    # ========================================================
    # RESPOSTAS
    # ========================================================

    def submit_answer(self, option_index):
        if self.finished:
            raise ValueError(
                "Quiz already finished."
            )

        question = self.get_current_question()
        options = question["options"]

        if (
            not isinstance(option_index, int)
            or isinstance(option_index, bool)
        ):
            raise TypeError(
                "Option index must be an integer."
            )

        if not 0 <= option_index < len(options):
            raise IndexError(
                "Invalid option index."
            )

        correct_index = question["correct_index"]
        correct = option_index == correct_index

        if correct:
            self.score += 1

        result = {
            "question_index": self.current_index,
            "selected_index": option_index,
            "correct_index": correct_index,
            "correct": correct,
            "explanation": question["explanation"]
        }

        self.answers.append(result)
        self.current_index += 1

        return result

    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    def get_result(self):
        if not self.finished:
            raise ValueError(
                "Quiz is not finished."
            )

        return {
            "score": self.score,
            "total": self.total_questions,
            "passing_score": self.passing_score,
            "passed": self.passed,
            "percentage": round(
                self.score / self.total_questions * 100,
                1
            ),
            "answers": list(self.answers)
        }
