import pygame, sys, math, random, os
try:
    from . import settings
    from .core.scene_manager import Scene, SceneManager
    from .entities.player import Player
    from .levels.level1 import Level1
    from .ui.hud import HUD
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import settings  # type: ignore
    from core.scene_manager import Scene, SceneManager  # type: ignore
    from entities.player import Player  # type: ignore
    from levels.level1 import Level1  # type: ignore
    from ui.hud import HUD  # type: ignore

class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        kaph_path = os.path.join(settings.FONT_DIR, 'Kaph_Font_1_20', 'TrueType (.ttf)', 'Kaph-Regular.ttf')
        if os.path.exists(kaph_path):
            self.font_title = pygame.font.Font(kaph_path, 72)
            self.font_btn = pygame.font.Font(kaph_path, 32)
            self.font_small = pygame.font.Font(kaph_path, 20)
        else:
            self.font_title = settings.load_font('pixel.ttf', 64)
            self.font_btn = settings.load_font('pixel.ttf', 28)
            self.font_small = settings.load_font('pixel.ttf', 20)
        self.timer = 0
        self.buttons = [
            {'text': 'JOGAR', 'action': 'play'},
            {'text': 'CONTROLES', 'action': 'controls'},
            {'text': 'SAIR', 'action': 'quit'}
        ]
        self.selected = 0
        self.mode = 'menu'
        self.controls_text = [
            'Controles:',
            'A / ←  : mover esquerda',
            'D / →  : mover direita',
            'ESPACO / W / ↑ : pular',
            'J : atacar',
            'R : reiniciar (morto)',
            'ESC : voltar / menu'
        ]
        bg_candidates = [
            os.path.join(settings.IMG_DIR, 'menu_background.png'),
            os.path.join(settings.IMG_DIR, 'game_background_4', 'game_background_4.png'),
        ]
        self.bg_image = None
        for p in bg_candidates:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert()
                    if img.get_size() != (settings.WIDTH, settings.HEIGHT):
                        img = pygame.transform.smoothscale(img, (settings.WIDTH, settings.HEIGHT))
                    self.bg_image = img
                    break
                except Exception:
                    pass
        if self.bg_image is None:
            grad = pygame.Surface((settings.WIDTH, settings.HEIGHT))
            for y in range(settings.HEIGHT):
                c = int(25 + 90 * (y/settings.HEIGHT))
                pygame.draw.line(grad, (c//3, c//4, c), (0,y), (settings.WIDTH, y))
            self.bg_image = grad

    def handle_event(self, event):
        if self.mode == 'menu':
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._activate(self.buttons[self.selected]['action'])
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for idx, b in enumerate(self._button_layout()):
                    if b['rect'].collidepoint(mx, my):
                        self._activate(b['action'])
        else: 
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.mode = 'menu'

    def _activate(self, action):
        if action == 'play':
            self.manager.set(LoadingScene(self.manager))
        elif action == 'controls':
            self.mode = 'controls'
        elif action == 'quit':
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _button_layout(self):
        start_y = settings.HEIGHT//2 - 10
        out = []
        for i, btn in enumerate(self.buttons):
            surf = self.font_btn.render(btn['text'], True, (255,255,255))
            rect = surf.get_rect(center=(settings.WIDTH//2, start_y + i*60))
            out.append({'surf': surf, 'rect': rect, 'action': btn['action'], 'text': btn['text']})
        return out

    def update(self, dt):
        self.timer += dt

    def draw(self, screen):
        if self.bg_image:
            screen.blit(self.bg_image, (0,0))
        else:
            screen.fill((10,10,25))
        dark = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        dark.fill((5,0,15,140))
        screen.blit(dark, (0,0))
        title = self.font_title.render('BRAINROT', True, (255,0,200))
        trect = title.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 140))
        screen.blit(title, trect)
        if self.mode == 'menu':
            for idx, b in enumerate(self._button_layout()):
                bg_col = (80,20,120) if idx == self.selected and int(self.timer*6)%2==0 else (40,15,60)
                pygame.draw.rect(screen, bg_col, b['rect'].inflate(40,20), border_radius=12)
                pygame.draw.rect(screen, (255,0,200), b['rect'].inflate(40,20), 2, border_radius=12)
                screen.blit(b['surf'], b['rect'])
            hint = self.font_small.render('ENTER / CLIQUE para selecionar | ESC para sair', True, (200,200,220))
            screen.blit(hint, hint.get_rect(center=(settings.WIDTH//2, settings.HEIGHT - 40)))
        else:
            panel_rect = pygame.Rect(0,0, int(settings.WIDTH*0.6), int(settings.HEIGHT*0.6))
            panel_rect.center = (settings.WIDTH//2, settings.HEIGHT//2 + 10)
            pygame.draw.rect(screen, (30,15,50), panel_rect, border_radius=16)
            pygame.draw.rect(screen, (255,0,200), panel_rect, 2, border_radius=16)
            y = panel_rect.top + 30
            for line in self.controls_text:
                surf = self.font_small.render(line, True, (230,230,240))
                screen.blit(surf, (panel_rect.left + 30, y))
                y += 34
            back = self.font_small.render('ESC / ENTER para voltar', True, (180,180,200))
            screen.blit(back, back.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 30)))

class GameScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.level = Level1()
        self.player = Player((50, 300))
        self.hud = HUD(self.player)
        self.camera_offset = pygame.Vector2(0,0)
        self.shake_timer = 0
        self.elapsed = 0.0
        self.show_start_msg = 4.0 
        self.start_msg_active = True
        self.start_msg_elapsed = 0.0
        kaph_path = os.path.join(settings.FONT_DIR, 'Kaph_Font_1_20', 'TrueType (.ttf)', 'Kaph-Regular.ttf')
        if os.path.exists(kaph_path):
            self.start_msg_font = pygame.font.Font(kaph_path, 48)
        else:
            self.start_msg_font = settings.load_font('pixel.ttf', 48)
        self.start_msg_lines = [
            'MATE TODOS OS INIMIGOS',
            'PARA ABRIR O PORTAL'
        ]
        settings.audio.play_music('main_music.mp3', volume=0.4)
        self.bg_layers = []
        bg_root = os.path.join(settings.IMG_DIR, 'game_background_4', 'layers')
        order = [
            ('sky.png',        0.05, 0.02, True),
            ('rocks.png',      0.15, 0.04, True),
            ('clouds_2.png',   0.25, 0.06, True),
            ('clouds_1.png',   0.35, 0.07, True),
            ('ground.png',     0.55, 0.10, True),
        ]
        if os.path.isdir(bg_root):
            for fname, dx, dy, tile in order:
                path = os.path.join(bg_root, fname)
                if not os.path.exists(path):
                    continue
                img = pygame.image.load(path).convert_alpha()
                scale = settings.HEIGHT / img.get_height()
                if 'ground' in fname:
                    scale = min(scale, 0.9 * (settings.HEIGHT / img.get_height()))
                new_w = int(img.get_width() * scale)
                new_h = int(img.get_height() * scale)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
                self.bg_layers.append((img, dx, dy, tile))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.player.health <= 0:
            self.manager.set(LoadingScene(self.manager))
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.set(MenuScene(self.manager))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m: 
                settings.audio.toggle_mute()
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS): 
                settings.audio.adjust_master(0.05)
            elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                settings.audio.adjust_master(-0.05)
            elif event.key == pygame.K_F1:
                self.elapsed = 0.0
                self.start_msg_elapsed = 0.0
                self.start_msg_active = True

    def update(self, dt):
        self.elapsed += dt
        if self.start_msg_active:
            self.start_msg_elapsed += min(dt, 0.2)  # cap 200ms por frame
            if self.start_msg_elapsed >= self.show_start_msg:
                self.start_msg_active = False
        if self.player.health > 0:
            self.player.update(self.level.platforms, dt)
            self.level.update()
            if hasattr(self.level, 'plants'):
                for p in self.level.plants:
                    p.update(dt)
            for e in self.level.enemies:
                e.hit_player(self.player)
            atk = self.player.get_attack_rect()
            if atk:
                for e in self.level.enemies:
                    if not e.alive: 
                        continue
                    if atk.colliderect(e.rect) and e not in self.player.attack_hit_set:
                        e.take_damage(1)
                        kb = 6 if self.player.facing == 1 else -6
                        e.rect.x += kb
                        self.player.attack_hit_set.add(e)
                        self.shake_timer = 8
                        settings.audio.play_sfx('punch-sound-effect.mp3', 0.8)
            for c in self.level.collectibles:
                before = self.player.score
                c.try_collect(self.player)
                if self.player.score > before:
                    settings.audio.play_sfx('mario_coin_sound.mp3', 0.6)
            if self.player.invuln_timer == 59: 
                self.shake_timer = 20
                settings.audio.play_sfx('tung-tung.mp3', 0.8)
        if self.shake_timer > 0:
            self.shake_timer -= 1
        self.camera_offset.x = -self.player.rect.centerx + settings.WIDTH/2
        self.camera_offset.y = -self.player.rect.centery + settings.HEIGHT/2
        self.camera_offset.x = min(0, self.camera_offset.x)
        self.camera_offset.x = max(-400, self.camera_offset.x)
        self.camera_offset.y = min(0, self.camera_offset.y)
        self.camera_offset.y = max(-200, self.camera_offset.y)

    def draw(self, screen):
        screen.fill((5, 5, 15))
        shake = pygame.Vector2(0,0)
        if self.shake_timer>0:
            shake.x = random.randint(-4,4)
            shake.y = random.randint(-4,4)
        cam_x = -self.camera_offset.x
        cam_y = -self.camera_offset.y
        for img, dx, dy, tile in self.bg_layers:
            off_x = int(-cam_x * dx)
            off_y = int(-cam_y * dy)
            dest_y = 0
            if 'ground' in img.get_flags().__repr__():
                dest_y = settings.HEIGHT - img.get_height()
            if img.get_height() < settings.HEIGHT * 0.7:
                dest_y = settings.HEIGHT - img.get_height()
            if tile:
                w = img.get_width()
                start_x = off_x % w
                for ix in (-1,0,1,2):
                    draw_x = -start_x + ix * w
                    if draw_x > settings.WIDTH or draw_x + w < -settings.WIDTH:
                        continue
                    screen.blit(img, (draw_x, dest_y + off_y))
            else:
                screen.blit(img, (off_x, dest_y + off_y))
        for p in self.level.platforms:
            r = p.rect.move(self.camera_offset + shake)
            screen.blit(p.image, r)
        if hasattr(self.level, 'gate_rect'):
            gate_r = self.level.gate_rect.move(self.camera_offset + shake)
            if self.level.gate_open:
                glow = pygame.Surface((gate_r.width, gate_r.height), pygame.SRCALPHA)
                color = (180, 40, 255)
                pygame.draw.rect(glow, (*color,180), glow.get_rect(), border_radius=8)
                pygame.draw.rect(glow, (255,255,255,200), glow.get_rect(), 2, border_radius=8)
                screen.blit(glow, gate_r.topleft)
            else:
                door = pygame.Surface((gate_r.width, gate_r.height), pygame.SRCALPHA)
                pygame.draw.rect(door, (60,40,90), door.get_rect(), border_radius=4)
                pygame.draw.rect(door, (20,10,30), door.get_rect(),2, border_radius=4)
                bar_y = 0
                while bar_y < gate_r.height:
                    pygame.draw.line(door, (90,70,120), (0,bar_y), (gate_r.width, bar_y),1)
                    bar_y += 10
                screen.blit(door, gate_r.topleft)
        if hasattr(self.level, 'decorations'):
            for d in self.level.decorations:
                r = getattr(d, 'render_rect', d.rect).move(self.camera_offset + shake)
                screen.blit(d.image, r)
        if hasattr(self.level, 'plants'):
            for p in self.level.plants:
                r = p.rect.move(self.camera_offset + shake)
                screen.blit(p.image, r)
        for e in self.level.enemies:
            draw_rect = getattr(e, 'render_rect', e.rect)
            screen.blit(e.image, draw_rect.move(self.camera_offset + shake))
        for c in self.level.collectibles:
            r = c.rect.move(self.camera_offset + shake)
            screen.blit(c.image, r)
        if self.player.health > 0:
            draw_rect = getattr(self.player, 'render_rect', self.player.rect)
            screen.blit(self.player.image, draw_rect.move(self.camera_offset + shake))
            if hasattr(self.level, 'gate_open') and self.level.gate_open and self.player.rect.colliderect(self.level.gate_rect):
                total_collectibles = len(getattr(self.level, 'collectibles', []))
                collected = sum(1 for c in getattr(self.level, 'collectibles', []) if getattr(c, 'collected', False))
                self.manager.set(EndScene(self.manager, collected, total_collectibles))
        else:
            death_img = pygame.transform.rotate(self.player.image, 90)
            draw_rect = getattr(self.player, 'render_rect', self.player.rect)
            screen.blit(death_img, draw_rect.move(self.camera_offset + shake))
        self.hud.draw(screen)
        if self.player.health<=0:
            self.hud.draw_game_over(screen)
        if self.start_msg_active:
            alpha = 255
            remain = self.show_start_msg - self.start_msg_elapsed
            if remain < 0.75:
                alpha = int(255 * (remain / 0.75))
            line_surfs = []
            stroke_color = (150, 95, 40)
            for line in self.start_msg_lines:
                base = self.start_msg_font.render(line, True, (255,255,255))
                surf_line = pygame.Surface((base.get_width()+8, base.get_height()+8), pygame.SRCALPHA)
                for ox in (-2,-1,0,1,2):
                    for oy in (-2,-1,0,1,2):
                        if ox == 0 and oy == 0:
                            continue
                        surf_line.blit(self.start_msg_font.render(line, True, stroke_color), (ox+4, oy+4))
                surf_line.blit(base, (4,4))
                line_surfs.append(surf_line)
            total_h = sum(ls.get_height() for ls in line_surfs) + (len(line_surfs)-1)*10
            max_w = max(ls.get_width() for ls in line_surfs)
            block = pygame.Surface((max_w, total_h), pygame.SRCALPHA)
            y = 0
            for ls in line_surfs:
                block.blit(ls, ((max_w - ls.get_width())//2, y))
                y += ls.get_height() + 10
            if alpha < 255:
                block.set_alpha(alpha)
            rect = block.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2))
            screen.blit(block, rect)


class LoadingScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0.0
        self.done = False
        self.font = settings.load_font('pixel.ttf', 32)
        self.small = settings.load_font('pixel.ttf', 18)
        self.dot_timer = 0.0
        self.dot_stage = 0

    def handle_event(self, event):
        pass

    def update(self, dt):
        self.timer += dt
        self.dot_timer += dt
        if self.dot_timer >= 0.4:
            self.dot_timer = 0
            self.dot_stage = (self.dot_stage + 1) % 4
        if not self.done and self.timer > 0.15:
            game = GameScene(self.manager)
            self.manager.set(game)
            self.done = True

    def draw(self, screen):
        screen.fill((15,10,25))
        w = int(settings.WIDTH * 0.5)
        h = 28
        bar_bg = pygame.Rect(0,0,w,h)
        bar_bg.center = (settings.WIDTH//2, settings.HEIGHT//2 + 30)
        pygame.draw.rect(screen, (40,25,70), bar_bg, border_radius=12)
        prog = min(1.0, self.timer / 1.2)
        fill_w = int((w-6) * prog)
        fill_rect = pygame.Rect(bar_bg.left+3, bar_bg.top+3, fill_w, h-6)
        pygame.draw.rect(screen, (255,0,200), fill_rect, border_radius=10)
        title = self.font.render('CARREGANDO', True, (255,0,200))
        dots = '.' * self.dot_stage
        screen.blit(title, title.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 20)))
        if dots:
            dots_surf = self.font.render(dots, True, (255,0,200))
            rect = dots_surf.get_rect()
            rect.midleft = (title.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 20)).right + 8, settings.HEIGHT//2 - 20)
            screen.blit(dots_surf, rect)
        hint = self.small.render('Aguarde...', True, (220,220,230))
        screen.blit(hint, hint.get_rect(center=(settings.WIDTH//2, bar_bg.bottom + 30)))


class EndScene(Scene):
    def __init__(self, manager, collected, total):
        super().__init__(manager)
        self.collected = collected
        self.total = total if total>0 else 1
        self.percent = int((self.collected / self.total) * 100)
        kaph_path = os.path.join(settings.FONT_DIR, 'Kaph_Font_1_20', 'TrueType (.ttf)', 'Kaph-Regular.ttf')
        if os.path.exists(kaph_path):
            self.font_big = pygame.font.Font(kaph_path, 72)
            self.font_mid = pygame.font.Font(kaph_path, 36)
            self.font_small = pygame.font.Font(kaph_path, 20)
        else:
            self.font_big = settings.load_font('pixel.ttf', 64)
            self.font_mid = settings.load_font('pixel.ttf', 28)
            self.font_small = settings.load_font('pixel.ttf', 18)
        self.timer = 0.0
        self.fade = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                self.manager.set(MenuScene(self.manager))

    def update(self, dt):
        self.timer += dt
        self.fade = min(1.0, self.fade + dt * 0.7)

    def draw(self, screen):
        screen.fill((10,5,15))
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0, 160))
        screen.blit(overlay, (0,0))
        title = self.font_big.render('PARABENS!', True, (255,0,200))
        trect = title.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 140))
        screen.blit(title, trect)
        msg1 = self.font_mid.render(f'VOCE DERRETEU {self.percent}% DO SEU CEREBRO', True, (255,255,255))
        screen.blit(msg1, msg1.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 40)))
        msg2 = self.font_small.render('Obrigado por jogar minha demo!', True, (230,230,240))
        msg3 = self.font_small.render('Feito por Cícero Gomes', True, (200,200,220))
        msg4 = self.font_small.render('Projeto UNINTER - Linguagem de Programação Aplicada', True, (180,180,200))
        screen.blit(msg2, msg2.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 30)))
        screen.blit(msg3, msg3.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 60)))
        screen.blit(msg4, msg4.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 90)))
        hint = self.font_small.render('ENTER / ESPACO / ESC para voltar ao menu', True, (255,255,255))
        screen.blit(hint, hint.get_rect(center=(settings.WIDTH//2, settings.HEIGHT - 40)))


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()
    manager = SceneManager()
    manager.set(MenuScene(manager))

    running = True
    while running:
        dt = clock.tick(settings.FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)
        manager.update(dt)
        manager.draw(screen)
        if settings.DEBUG:
            fps_font = settings.load_font('pixel.ttf', 16)
            fps_surf = fps_font.render(f"FPS: {int(clock.get_fps())}", True, (255,255,255))
            screen.blit(fps_surf, (settings.WIDTH-90, 10))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
