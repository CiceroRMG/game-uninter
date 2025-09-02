import pygame, os, sys
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore

_FLOOR_IMG = None
_FLOAT_IMG = None

def _load_image(name: str):
    path = os.path.join(settings.IMG_DIR, 'Mossy Tileset', name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            if pygame.display.get_init() and pygame.display.get_surface():
                img = img.convert_alpha()
            return img
        except Exception:
            return None
    return None

def get_floor():
    global _FLOOR_IMG
    if _FLOOR_IMG is None:
        _FLOOR_IMG = _load_image('floor.png')
    return _FLOOR_IMG

def get_floating():
    global _FLOAT_IMG
    if _FLOAT_IMG is None:
        _FLOAT_IMG = _load_image('plataformfloating.png')
    return _FLOAT_IMG

def adapt_image_to_block(src: pygame.Surface | None, width: int, height: int, tile: bool = True):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    if not src:
        surf.fill((90,130,100))
        return surf
    sw, sh = src.get_size()
    if sw > width or sh > height:
        scale = min(width / sw, height / sh)
        sw = max(1, int(sw * scale))
        sh = max(1, int(sh * scale))
        src = pygame.transform.smoothscale(src, (sw, sh))
    if not tile:
        ox = (width - sw) // 2
        oy = (height - sh) // 2
        surf.blit(src, (ox, oy))
        return surf
    for y in range(0, height, sh):
        tile_h = min(sh, height - y)
        for x in range(0, width, sw):
            tile_w = min(sw, width - x)
            if tile_w == sw and tile_h == sh:
                surf.blit(src, (x, y))
            else:
                fragment = src.subsurface(pygame.Rect(0, 0, tile_w, tile_h))
                surf.blit(fragment, (x, y))
    return surf

class Platform(pygame.sprite.Sprite):
    def __init__(self, rect, variant=0):
        super().__init__()
        x,y,w,h = rect
        base = get_floor()
        self.image = adapt_image_to_block(base, w, h, tile=True)
        self.rect = pygame.Rect(x,y,w,h)

class FloatingPlatform(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        x,y,w,h = rect
        src = get_floating()
        self.image = adapt_image_to_block(src, w, h, tile=False)
        self.rect = pygame.Rect(x,y,w,h)


