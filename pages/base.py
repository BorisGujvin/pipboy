# pages/base.py
from abc import ABC, abstractmethod

class Page(ABC):
    @abstractmethod
    def render(self, draw):
        ...

    @abstractmethod
    def handle_touch(self, x, y, state):
        ...

    @abstractmethod
    def on_encoder(self, delta:int):
        ...

    @abstractmethod
    def on_click(self):
        ...
