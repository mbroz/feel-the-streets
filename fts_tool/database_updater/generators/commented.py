from .generator import Generator
from shared.entities import Commented

class CommentedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Commented)

    @staticmethod
    def accepts(props):
        return "comment" in props