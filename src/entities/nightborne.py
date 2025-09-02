import os, sys, pygame, random
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore
try:
    from PIL import Image
    _PIL_OK = True
except ImportError: 
    _PIL_OK = False

class NightBorneEnemy(pygame.sprite.Sprite):
    HITBOX_W_RATIO = 0.50
    HITBOX_H_RATIO = 0.70
    GRAVITY = 0.6
    MAX_FALL = 12
    ATTACK_COOLDOWN = 50
    ATTACK_RANGE_X = 38 
    DAMAGE = 1
    DEBUG = False

    def __init__(self, pos, patrol=(-40, 40)):
        super().__init__()
        self.animations = {}
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0.0
        self.anim_speed = 0.12
        self.facing = 1

        self.health = 4
        self.max_health = 4
        self.alive = True
        self.hit_timer = 0
        self.attack_timer = 0
        self.hurt_timer = 0
        self.death_frozen = False

        self.start_x = pos[0]
        self.patrol = patrol
        self.speed = 1.6
        self.direction = 1

        self.vel_y = 0
        self.on_ground = False

        self._load_gifs()
        self._normalize()

        first = self.animations['idle'][0]
        fw, fh = first.get_width(), first.get_height()
        hb_w = max(8, int(fw * self.HITBOX_W_RATIO))
        hb_h = max(8, int(fh * self.HITBOX_H_RATIO))
        self.rect = pygame.Rect(0,0,hb_w,hb_h)
        self.rect.midbottom = (pos[0] + fw//2, pos[1] + fh)
        self.start_x = self.rect.centerx
        self.image = first
        self.render_rect = self.image.get_rect(midbottom=self.rect.midbottom)

    # -------------- Carregamento GIFs -------------- #
    def _load_gifs(self):
        base = os.path.join(settings.IMG_DIR, 'NightBorne')
        mapping = {
            'idle': 'NightBorne_idle.gif',
            'run': 'NightBorne_run.gif',
            'attack': 'NightBorne_attack.gif',
            'hurt': 'NightBorne_hurt.gif',
            'die': 'NightBorne_death..gif'
        }
        for state, fname in mapping.items():
            path = os.path.join(base, fname)
            frames = self._extract_frames(path)
            if not frames:
                surf = pygame.Surface((48,48), pygame.SRCALPHA)
                surf.fill((200,0,200))
                pygame.draw.rect(surf,(0,0,0),surf.get_rect(),2)
                frames = [surf]
            self.animations[state] = frames
        if 'hurt' not in self.animations:
            self.animations['hurt'] = self.animations.get('idle', [])

    def _extract_frames(self, path):
        if not os.path.exists(path):
            return []
        frames = []
        if _PIL_OK:
            try:
                im = Image.open(path)
                index = 0
                while True:
                    im.seek(index)
                    frame = im.convert('RGBA')
                    mode = frame.mode
                    size = frame.size
                    data = frame.tobytes()
                    surf = pygame.image.fromstring(data, size, mode)
                    frames.append(self._remove_background(surf))
                    index += 1
            except EOFError:
                pass
            except Exception:
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    frames = [self._remove_background(surf)]
                except Exception:
                    frames = []
        else:
            try:
                surf = pygame.image.load(path).convert_alpha()
                frames = [self._remove_background(surf)]
            except Exception:
                frames = []
        return frames

    def _remove_background(self, surf):
        tl = surf.get_at((0,0))
        if tl.a == 0:
            return surf
        tol = 18
        w,h = surf.get_size()
        surf.lock()
        for y in range(h):
            for x in range(w):
                c = surf.get_at((x,y))
                if abs(c.r - tl.r) <= tol and abs(c.g - tl.g) <= tol and abs(c.b - tl.b) <= tol:
                    surf.set_at((x,y), (c.r, c.g, c.b, 0))
        surf.unlock()
        return surf

    # -------------- Normalização -------------- #
    def _normalize(self):
        max_w = 0; max_h = 0
        cropped = {}
        for st, frs in self.animations.items():
            new = []
            for f in frs:
                r = f.get_bounding_rect(min_alpha=10)
                if r.w == 0 or r.h == 0:
                    r = pygame.Rect(0,0,1,1)
                sub = f.subsurface(r).copy()
                new.append(sub)
                if sub.get_width() > max_w: max_w = sub.get_width()
                if sub.get_height() > max_h: max_h = sub.get_height()
            cropped[st] = new
        if max_w == 0 or max_h == 0:
            return
        for st, frs in cropped.items():
            uniform = []
            for f in frs:
                canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
                dest = f.get_rect()
                dest.midbottom = (max_w//2, max_h)
                canvas.blit(f, dest)
                uniform.append(canvas)
            self.animations[st] = uniform

    # -------------- Lógica -------------- #
    def _set_state(self):
        if not self.alive:
            self.state = 'die'
        elif self.hurt_timer > 0:
            self.state = 'hurt'
        elif self.attack_timer > 0:
            self.state = 'attack'
        elif abs(self.direction * self.speed) > 0.05:
            self.state = 'run'
        else:
            self.state = 'idle'
        frames = self.animations.get(self.state, [])
        if frames and self.frame_index >= len(frames):
            self.frame_index = 0

    def _animate(self, dt):
        frames = self.animations.get(self.state, [])
        if not frames: return
        self.frame_timer += dt
        if self.frame_timer >= self.anim_speed:
            if self.state == 'die':
                if not self.death_frozen:
                    if self.frame_index < len(frames)-1:
                        self.frame_index += 1
                    if self.frame_index == len(frames)-1:
                        self.death_frozen = True
                self.frame_timer = 0
            else:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(frames)
        frame = frames[self.frame_index]
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame.copy()
        self.render_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        if self.DEBUG:
            dbg = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(dbg,(0,255,0,120), dbg.get_rect(),1)
            self.image.blit(dbg,(0,0))

    def update(self, platforms):
        dt = 1/60
        if self.alive:
            self.rect.x += self.speed * self.direction
            left_lim = self.start_x + self.patrol[0]
            right_lim = self.start_x + self.patrol[1]
            if self.rect.centerx < left_lim:
                self.rect.centerx = left_lim
                self.direction = 1
                self.facing = 1
            elif self.rect.centerx > right_lim:
                self.rect.centerx = right_lim
                self.direction = -1
                self.facing = -1
            self.vel_y += self.GRAVITY
            if self.vel_y > self.MAX_FALL: self.vel_y = self.MAX_FALL
            self.rect.y += int(self.vel_y)
            self.on_ground = False
            for p in platforms:
                if self.rect.colliderect(p.rect):
                    if self.vel_y > 0 and self.rect.bottom >= p.rect.top and self.rect.centery < p.rect.centery:
                        self.rect.bottom = p.rect.top
                        self.vel_y = 0
                        self.on_ground = True
            if self.attack_timer > 0: self.attack_timer -= 1
            if self.hurt_timer > 0: self.hurt_timer -= 1
        else:
            if not self.on_ground:
                self.vel_y += self.GRAVITY
                if self.vel_y > self.MAX_FALL: self.vel_y = self.MAX_FALL
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

    # ---------- Interações ---------- #
    def hit_player(self, player):
        if not self.alive: return
        if abs(player.rect.centerx - self.rect.centerx) < self.ATTACK_RANGE_X and self.attack_timer <= 0:
            if player.rect.bottom > self.rect.top - 10 and player.rect.top < self.rect.bottom + 10:
                self.attack_timer = self.ATTACK_COOLDOWN
                self.frame_index = 0
                kb_dir = 1 if player.rect.centerx > self.rect.centerx else -1
                player.take_damage(self.DAMAGE, pygame.Vector2(kb_dir*6, -6))

    def take_damage(self, amount):
        if not self.alive or self.hurt_timer > 0:
            return
        self.health -= amount
        self.hurt_timer = 18
        self.frame_index = 0
        if self.health <= 0:
            self.alive = False
            self.state = 'die'
            self.frame_index = 0
            self.death_frozen = False

