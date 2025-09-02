import os
import pygame
try:
    from .. import settings
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    import settings  # type: ignore


class Player(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.animations = {}
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0.0
        self.anim_speed = 0.12  # segundos por frame aproximado
        self.facing = 1  # 1 direita, -1 esquerda
        self.attack_timer = 0.0
        self.attack_hit_set = set()  # inimigos já atingidos neste ataque

        self._load_animations()
        first_frame = self.animations[self.state][0]
    hb_w = int(first_frame.get_width() * 0.6)
    hb_h = int(first_frame.get_height() * 0.9)
        self.rect = pygame.Rect(pos[0], pos[1], hb_w, hb_h)
        self.image = pygame.Surface(first_frame.get_size(), pygame.SRCALPHA)
        self._blit_frame(first_frame)
        self.render_rect = self.image.get_rect()
        self.render_rect.midbottom = self.rect.midbottom

        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.health = 5
        self.max_health = 5
        self.invuln_timer = 0
        self.score = 0

    def _load_animations(self):
        base = os.path.join(settings.IMG_DIR, 'TungTungTung Sahur', 'Sprites')

    def slice_sheet(path):
            if not os.path.exists(path):
                surf = pygame.Surface((48, 48), pygame.SRCALPHA)
                surf.fill((255, 0, 255))
                pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
                return [surf]
            sheet = pygame.image.load(path).convert_alpha()
            h = sheet.get_height()
            w = sheet.get_width()
            if h <= 0 or w <= 0:
                return []
            if w % h != 0:
                frame_w = h
            else:
                frame_w = h
            frames = []
            cols = max(1, w // frame_w)
            for i in range(cols):
                frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, h)).copy()
                frames.append(frame)
            return frames

    def crop_frames_preserve_baseline(frames):
            bboxes = []
            cropped = []
            max_w = 0
            max_h = 0
            for f in frames:
                r = f.get_bounding_rect(min_alpha=1)
                if r.width == 0 or r.height == 0:
                    r = pygame.Rect(0, 0, 1, 1)
                sub = f.subsurface(r).copy()
                cropped.append(sub)
                bboxes.append(r)
                if r.width > max_w:
                    max_w = r.width
                if r.height > max_h:
                    max_h = r.height
            uniform = []
            for sub in cropped:
                canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
                dest = sub.get_rect()
                dest.midbottom = (max_w // 2, max_h)
                canvas.blit(sub, dest)
                uniform.append(canvas)
            return uniform

        sheet_map = {
            'idle': 'Idling.png',
            'run': 'Running .png',
            'walk': 'Running .png',
            'jump': 'Jumping.png',
            'attack': 'Basic Attack .png'
        }
        for key, filename in sheet_map.items():
            path = os.path.join(base, filename)
            frames = slice_sheet(path)
            if not frames:
                frames = [settings.load_image('player_placeholder.png', (48, 48))]
            else:
                frames = crop_frames_preserve_baseline(frames)
            self.animations[key] = frames
        if 'walk' in self.animations and 'run' not in self.animations:
            self.animations['run'] = self.animations['walk']

    def _set_state(self):
        if self.attack_timer > 0:
            self.state = 'attack'
            return
        if not self.on_ground:
            self.state = 'jump'
            return
        if abs(self.vel.x) > 0.5:
            self.state = 'run'
        else:
            self.state = 'idle'

    def _animate(self, dt):
        frames = self.animations.get(self.state, [])
        if not frames:
            return
        self.frame_timer += dt
        if self.frame_timer >= self.anim_speed:
            self.frame_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(frames)
        frame = frames[self.frame_index]
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)
        self.image = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        self._blit_frame(frame)
        self.render_rect = self.image.get_rect()
        self.render_rect.midbottom = self.rect.midbottom
        if self.invuln_timer % 10 < 5 and self.invuln_timer > 0:
            self.image.set_alpha(80)
        else:
            self.image.set_alpha(255)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -settings.PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = settings.PLAYER_SPEED
            self.facing = 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel.y = settings.JUMP_FORCE
            self.on_ground = False
        if keys[pygame.K_j] and self.attack_timer <= 0:
            self.attack_timer = 0.4
            self.frame_index = 0
            self.attack_hit_set.clear()

    def apply_gravity(self):
        self.vel.y += settings.GRAVITY
        if self.vel.y > 20:
            self.vel.y = 20

    def take_damage(self, amount, knockback=None):
        if self.invuln_timer > 0 or self.health <= 0:
            return
        self.health -= amount
        self.invuln_timer = 60
        if knockback:
            self.vel += knockback
        if self.health <= 0:
            self.health = 0

    def update(self, platforms, dt):
        self.handle_input()
        self.apply_gravity()
        self.rect.x += int(self.vel.x)
        self.collide(platforms, 'x')
        self.rect.y += int(self.vel.y)
        self.on_ground = False
        self.collide(platforms, 'y')
        if hasattr(self, 'render_rect'):
            self.render_rect.midbottom = self.rect.midbottom
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = 0
        self._set_state()
        self._animate(dt)

    def get_attack_rect(self):
        if self.attack_timer <= 0:
            return None
    if self.attack_timer < 0.2:
            return None
    reach = int(self.rect.width * 2)
    height = int(self.rect.height * 0.8)
        top = self.rect.bottom - height
        if self.facing == 1:
            return pygame.Rect(self.rect.right, top, reach, height)
        else:
            return pygame.Rect(self.rect.left - reach, top, reach, height)

    def collide(self, platforms, dir):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if dir == 'x':
                    if self.vel.x > 0:
                        self.rect.right = p.rect.left
                    elif self.vel.x < 0:
                        self.rect.left = p.rect.right
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = p.rect.top
                        self.vel.y = 0
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.rect.top = p.rect.bottom
                        self.vel.y = 0

    def _blit_frame(self, frame):
        if not self.image:
            self.image = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        dest = frame.get_rect()
        dest.midbottom = self.image.get_rect().midbottom
        self.image.blit(frame, dest)
