import pygame
from typing import Optional

class Scene:
    def __init__(self, manager: 'SceneManager'):
        self.manager = manager
    def handle_event(self, event: pygame.event.Event):
        pass
    def update(self, dt: float):
        pass
    def draw(self, screen: pygame.Surface):
        pass

class SceneManager:
    def __init__(self):
        self.current: Optional[Scene] = None
    def set(self, scene: Scene):
        self.current = scene
    def handle_event(self, event: pygame.event.Event):
        if self.current:
            self.current.handle_event(event)
    def update(self, dt: float):
        if self.current:
            self.current.update(dt)
    def draw(self, screen: pygame.Surface):
        if self.current:
            self.current.draw(screen)
