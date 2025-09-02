import pygame, random, sys, os
try:
    from .. import settings
    from .mossy_assets import extract_components
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore
    from mossy_assets import extract_components  # type: ignore

class Decoration(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.Surface, pos, parallax=1.0):
        super().__init__()
        self.base_image = surface
        self.image = surface.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.parallax = parallax 
        self.offset_wave = random.random()*10
        self.wave_amp = 2
        self.wave_speed = 1.2

    def update(self, dt):
        import math
        dy = math.sin((pygame.time.get_ticks()/1000.0 + self.offset_wave)*self.wave_speed)*self.wave_amp
        self.image = self.base_image
        self.render_rect = self.rect.move(0, dy)

def build_decorations():
    files = [
        ('Mossy - BackgroundDecoration.png', 24, 24, 32),
        ('Mossy - Decorations&Hazards.png', 16, 16, 64),
        ('Mossy - Hanging Plants.png', 20, 30, 64),
        ('Mossy - MossyHills.png', 48, 32, 32)
    ]
    decos = []
    x_cursor = 150
    for fname, minw, minh, limit in files:
        comps = extract_components(fname, min_w=minw, min_h=minh, max_components=limit)
        for surf in comps[:8]:
            decos.append(Decoration(surf, (x_cursor, 500 - surf.get_height())))
            x_cursor += surf.get_width() + 40
            if x_cursor > 1000:
                x_cursor = 150
    return decos
