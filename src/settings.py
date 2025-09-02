import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'assets')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
SND_DIR = os.path.join(ASSETS_DIR, 'sounds')
FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')

WIDTH = 960
HEIGHT = 540
TITLE = 'Brainrot: Tum Tum Sahur Despertar'
FPS = 60
GRAVITY = 0.7
PLAYER_SPEED = 5
JUMP_FORCE = -14

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 40, 60)
GREEN = (40, 200, 120)
BLUE = (60, 120, 255)
YELLOW = (255, 220, 0)
PURPLE = (180, 60, 255)

DEBUG = False

import pygame
pygame.init()

def load_image(name: str, size=None, colorkey=None):
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        surf = pygame.Surface((size or (48,48)), pygame.SRCALPHA)
        surf.fill((255,0,255))
        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
        return surf
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img

def load_font(name: str, size: int):
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path):
        return pygame.font.SysFont('Arial', size)
    return pygame.font.Font(path, size)

def load_sound(name: str):
    path = os.path.join(SND_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

class AudioManager:
    def __init__(self):
        self.cache = {}
        self.music_playing = None
        self.master_volume = 1.0
        self.music_volume = 0.2
        self.sfx_volume = 0.8
        self.muted = False

    def sound(self, name, volume=1.0):
        if name not in self.cache:
            s = load_sound(name)
            if s:
                self.cache[name] = s
        snd = self.cache.get(name)
        if snd:
            final = self._apply_master(volume * self.sfx_volume)
            snd.set_volume(final)
        return snd

    def play_sfx(self, name, volume=1.0):
        snd = self.sound(name, volume)
        if snd:
            snd.play()

    def play_music(self, name, volume=0.6, loop=-1):
        path = os.path.join(SND_DIR, name)
        if not os.path.exists(path):
            return
        if self.music_playing == name:
            return
        try:
            pygame.mixer.music.load(path)
            self.music_volume = volume
            self._apply_music_volume()
            pygame.mixer.music.play(loop)
            self.music_playing = name
        except Exception:
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.music_playing = None

    def toggle_mute(self):
        self.muted = not self.muted
        self._apply_music_volume()
        for snd in self.cache.values():
            snd.set_volume(self._apply_master(snd.get_volume()))

    def set_master(self, value: float):
        self.master_volume = max(0.0, min(1.0, value))
        self._apply_music_volume()

    def adjust_master(self, delta: float):
        self.set_master(self.master_volume + delta)

    def _apply_master(self, value: float) -> float:
        if self.muted:
            return 0.0
        return max(0.0, min(1.0, value * self.master_volume))

    def _apply_music_volume(self):
        try:
            vol = self._apply_master(self.music_volume)
            pygame.mixer.music.set_volume(vol)
        except Exception:
            pass

audio = AudioManager()
