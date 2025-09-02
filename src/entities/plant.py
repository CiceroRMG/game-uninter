import pygame, os, random, sys
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore

class Plant(pygame.sprite.Sprite):
    def __init__(self, kind='BlueFlower1', pos=(0,0), fps=20):
        super().__init__()
        self.kind = kind
        self.frames = []
        self.frame_index = 0
        self.timer = 0.0
        self.fps = fps
        self.loop = True
        self._load_frames()
        if not self.frames:
            self.image = pygame.Surface((16,16), pygame.SRCALPHA)
            self.image.fill((0,200,0,120))
        else:
            self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)

    def _load_frames(self):
        root = os.path.join(settings.IMG_DIR, 'Plant Animations', self.kind)
        if not os.path.isdir(root):
            return
        files = [f for f in os.listdir(root) if f.lower().endswith('.png')]
        files.sort()
        for f in files:
            try:
                img = pygame.image.load(os.path.join(root,f)).convert_alpha()
                self.frames.append(img)
            except Exception:
                continue
        if self.frames:
            fw, fh = self.frames[0].get_size()
            scale = 1.0
            target_h = 48
            if fh > target_h:
                scale = target_h / fh
            if scale != 1.0:
                new_frames = []
                for fr in self.frames:
                    sz = (int(fr.get_width()*scale), int(fr.get_height()*scale))
                    new_frames.append(pygame.transform.smoothscale(fr, sz))
                self.frames = new_frames

    def update(self, dt):
        if not self.frames:
            return
        self.timer += dt
        frame_time = 1.0 / self.fps
        while self.timer >= frame_time:
            self.timer -= frame_time
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames)-1
        self.image = self.frames[self.frame_index]
