
from abc import ABC, abstractmethod
from typing import Any


class BasePuzzle(ABC):
    def __init__(self):
        self.completed = False

    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        """Retorna os dados necessários para a interface."""
        pass

    @abstractmethod
    def update(self, action: dict[str, Any]) -> None:
        """Processa uma ação da jogadora."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Verifica se o objetivo foi alcançado."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Restaura o estado inicial do puzzle."""
        pass
