import pygame, os, sys
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore

class HUD:
    def __init__(self, player):
        self.player = player
        kaph_ttf = os.path.join(settings.FONT_DIR, 'Kaph_Font_1_20', 'TrueType (.ttf)', 'Kaph-Regular.ttf')
        if os.path.exists(kaph_ttf):
            self.font_small = pygame.font.Font(kaph_ttf, 22)
            self.font_big = pygame.font.Font(kaph_ttf, 60)
        else:
            self.font_small = settings.load_font('pixel.ttf', 20)
            self.font_big = settings.load_font('pixel.ttf', 48)
        self._build_hearts()

    def _build_hearts(self):
        # Cria surfaces de coração cheio e vazio garantindo exibição mesmo sem fonte unicode
        w,h = 22,20
        def draw_heart(fill_color, outline_color, filled=True):
            surf = pygame.Surface((w,h), pygame.SRCALPHA)
            r = h//2 - 2
            # dois círculos superiores
            pygame.draw.circle(surf, fill_color if filled else (0,0,0,0), (r+2, r), r)
            pygame.draw.circle(surf, fill_color if filled else (0,0,0,0), (w - r - 3, r), r)
            # triângulo inferior
            points = [(3, r+2), (w-4, r+2), (w//2, h-2)]
            if filled:
                pygame.draw.polygon(surf, fill_color, points)
            # outline sempre
            pygame.draw.circle(surf, outline_color, (r+2, r), r, 2)
            pygame.draw.circle(surf, outline_color, (w - r - 3, r), r, 2)
            pygame.draw.lines(surf, outline_color, True, points, 2)
            return surf
        self.heart_full = draw_heart((220,40,60,255), (255,255,255,220), True)
        self.heart_empty = draw_heart((0,0,0,0), (180,180,200,200), False)

    def draw(self, screen):
        # Health (icone por coração)
        x = 16
        y = 12
        spacing = self.heart_full.get_width() + 6
        for i in range(self.player.max_health):
            img = self.heart_full if i < self.player.health else self.heart_empty
            screen.blit(img, (x + i*spacing, y))
        # Score
        score_surf = self.font_small.render(f'Dopamina: {self.player.score}', True, settings.YELLOW)
        screen.blit(score_surf, (16, 40))

    def draw_game_over(self, screen):
        text = self.font_big.render('GAME OVER', True, settings.PURPLE)
        info = self.font_small.render('Pressione R para reiniciar', True, settings.WHITE)
        rect = text.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 40))
        irect = info.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 20))
        screen.blit(text, rect)
        screen.blit(info, irect)
