import pygame, os, sys, math, random
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore

COIN_FILES = ['coins/Instagram.png', 'coins/TikTok.png', 'coins/Youtube.png']
_COIN_CACHE: list[pygame.Surface] = []

def _load_coins():
    if _COIN_CACHE:
        return _COIN_CACHE
    for fname in COIN_FILES:
        img = settings.load_image(fname, (32,32))
        if img:
            _COIN_CACHE.append(img)
    if not _COIN_CACHE:
        surf = pygame.Surface((32,32))
        surf.fill((255,215,0))
        _COIN_CACHE.append(surf)
    return _COIN_CACHE

class Collectible(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        choices = _load_coins()
        self.base_image = random.choice(choices)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0
        self.collected = False

    def update(self):
        if self.collected:
            return
        self.timer += 1
        offset = math.sin(self.timer * 0.15) * 4
        self.rect.y += offset
        self.rect.y -= offset 
        scale = 1 + math.sin(self.timer * 0.3) * 0.1
        base_w, base_h = self.base_image.get_size()
        size_w = int(base_w*scale)
        size_h = int(base_h*scale)
        self.image = pygame.transform.smoothscale(self.base_image, (size_w,size_h))
        self.rect = self.image.get_rect(center=self.rect.center)

    def try_collect(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            player.score += 10
            self.image.set_alpha(0)
