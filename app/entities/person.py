from . import Entity
from ..services import config

class Person(Entity):
    use_step_sounds = True

    def move_to_current(self):
        self.move_to(self.position, force=True)

    def step_forward(self, force=False):
        self.move_by(config().navigation.step_length, force)
    
    def step_backward(self, force=False):
        self.move_by(-config().navigation.step_length, force)
    