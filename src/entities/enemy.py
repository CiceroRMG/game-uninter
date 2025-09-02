import pygame, os, sys, random
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore

class Enemy(pygame.sprite.Sprite):

    HITBOX_WIDTH_RATIO = 0.55
    HITBOX_HEIGHT_RATIO = 0.72
    FEET_OFFSET = 0
    DEBUG = False

    def __init__(self, pos, patrol=(0, 100)):
        super().__init__()
        self.animations = {}
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0.0
        self.anim_speed = 0.15
        self.facing = 1

        self.start_x = pos[0]
        self.patrol = patrol
        self.speed = 1.4
        self.direction = 1

        self.health = 3
        self.max_health = 3
        self.alive = True
        self.hit_timer = 0
        self.stun_timer = 0
        self.attack_timer = 0

        self._load_animations()
        self._normalize_animations()

        first = self.animations['idle'][0]
        fw, fh = first.get_width(), first.get_height()
        hb_w = int(fw * self.HITBOX_WIDTH_RATIO)
        hb_h = int(fh * self.HITBOX_HEIGHT_RATIO)
        if hb_w < 8: hb_w = fw
        if hb_h < 8: hb_h = fh
        self.rect = pygame.Rect(0, 0, hb_w, hb_h)
        visual_bottom = pos[1] + fh
        self.rect.midbottom = (pos[0] + fw//2, visual_bottom)
        self.image = first
        self.render_rect = self.image.get_rect(midbottom=(self.rect.midbottom[0], self.rect.bottom + self.FEET_OFFSET))

        self.vel_y = 0
        self.on_ground = False

    def _slice_sheet(self, path):
        if not os.path.exists(path):
            return []
        sheet = pygame.image.load(path).convert_alpha()
        h = sheet.get_height(); w = sheet.get_width()
        if h <= 0 or w <= 0: return []
        frame_w = h 
        cols = max(1, w // frame_w)
        return [sheet.subsurface(pygame.Rect(i*frame_w, 0, frame_w, h)).copy() for i in range(cols)]

    def _create_placeholder(self):
        s = pygame.Surface((48,48), pygame.SRCALPHA)
        s.fill((120,60,10))
        pygame.draw.rect(s,(0,0,0),s.get_rect(),2)
        return s

    def _load_animations(self):
        base = os.path.join(settings.IMG_DIR, 'Mushroom')
        sprite_map = {
            'idle': 'Mushroom-Idle.png',
            'run': 'Mushroom-Run.png',
            'attack': 'Mushroom-Attack.png',
            'hit': 'Mushroom-Hit.png',
            'stun': 'Mushroom-Stun.png',
            'die': 'Mushroom-Die.png'
        }
        for state, file in sprite_map.items():
            frames = self._slice_sheet(os.path.join(base, file))
            self.animations[state] = frames if frames else [self._create_placeholder()]

    def _normalize_animations(self):
        cropped = {}
        max_w = 0; max_h = 0
        for state, frames in self.animations.items():
            new_list = []
            for f in frames:
                r = f.get_bounding_rect(min_alpha=10)
                if r.width == 0 or r.height == 0:
                    r = pygame.Rect(0,0,1,1)
                sub = f.subsurface(r).copy()
                new_list.append(sub)
                if sub.get_width() > max_w: max_w = sub.get_width()
                if sub.get_height() > max_h: max_h = sub.get_height()
            cropped[state] = new_list
        if max_w == 0 or max_h == 0:
            return
        for state, frames in cropped.items():
            uniform = []
            for f in frames:
                canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
                dest = f.get_rect()
                dest.midbottom = (max_w//2, max_h)
                canvas.blit(f, dest)
                uniform.append(canvas)
            self.animations[state] = uniform

    def _set_state(self):
        if not self.alive:
            self.state = 'die'
        elif self.hit_timer > 0:
            self.state = 'hit'
        elif self.stun_timer > 0:
            self.state = 'stun'
        elif self.attack_timer > 0:
            self.state = 'attack'
        elif abs(self.direction * self.speed) > 0.05:
            self.state = 'run'
        else:
            self.state = 'idle'

    def _animate(self, dt):
        frames = self.animations.get(self.state, [])
        if not frames: return
        self.frame_timer += dt
        if self.frame_timer >= self.anim_speed:
            self.frame_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(frames)
        frame = frames[self.frame_index]
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame.copy()
        if self.hit_timer > 0 and (self.hit_timer // 2) % 2 == 0:
            tint = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            tint.fill((255,60,60,120))
            self.image.blit(tint, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
        self.render_rect = self.image.get_rect(midbottom=(self.rect.midbottom[0], self.rect.bottom + self.FEET_OFFSET))
        if self.DEBUG:
            dbg = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(dbg, (0,255,0,120), dbg.get_rect(), 1)
            self.image.blit(dbg, (0,0))

    def update(self, platforms):
        dt = 1/60
        if self.alive:
            if self.stun_timer <= 0 and self.hit_timer <= 0 and self.attack_timer <= 0:
                self.rect.x += self.speed * self.direction
                if (self.rect.x <= self.start_x + self.patrol[0] or
                    self.rect.x >= self.start_x + self.patrol[1]):
                    self.direction *= -1
                    self.facing = self.direction
            self.vel_y += 0.6
            if self.vel_y > 12: self.vel_y = 12
            self.rect.y += int(self.vel_y)
            self.on_ground = False
            for p in platforms:
                if self.rect.colliderect(p.rect):
                    if self.vel_y > 0 and self.rect.bottom >= p.rect.top and self.rect.centery < p.rect.centery:
                        self.rect.bottom = p.rect.top
                        self.vel_y = 0
                        self.on_ground = True
            if self.hit_timer > 0: self.hit_timer -= 1
            if self.stun_timer > 0: self.stun_timer -= 1
            if self.attack_timer > 0: self.attack_timer -= 1
        else:
            if not self.on_ground:
                self.vel_y += 0.6
                if self.vel_y > 12: self.vel_y = 12
                self.rect.y += int(self.vel_y)
                for p in platforms:
                    if self.rect.colliderect(p.rect) and self.vel_y > 0:
                        self.rect.bottom = p.rect.top
                        self.vel_y = 0
                        self.on_ground = True
            else:
                self.vel_y = 0
        self._set_state()
        self._animate(dt)

    def hit_player(self, player):
        if not self.alive: return
        if self.rect.colliderect(player.rect):
            if self.attack_timer <= 0 and self.stun_timer <= 0 and self.hit_timer <= 0:
                self.attack_timer = 30  # meio segundo
                self.frame_index = 0
                kb_dir = 1 if player.rect.centerx > self.rect.centerx else -1
                player.take_damage(1, pygame.Vector2(kb_dir*6, -6))

    def take_damage(self, amount):
        if not self.alive or self.hit_timer > 0: return
        self.health -= amount
        self.hit_timer = 20
        self.frame_index = 0
        if self.health <= 0:
            self.kill()
        else:
            if random.random() < 0.35:
                self.stun_timer = 50

    def kill(self):
        self.alive = False
        self.frame_index = 0
        self.hit_timer = 0
        self.stun_timer = 0
        self.attack_timer = 0
