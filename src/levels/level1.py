import pygame, os, sys
try:
    from ..entities.platform import Platform
    from ..entities.platform import FloatingPlatform
    from ..entities.enemy import Enemy
    from ..entities.nightborne import NightBorneEnemy
    from ..entities.collectible import Collectible
    from ..entities.plant import Plant
except ImportError:
    base = os.path.join(os.path.dirname(__file__), '..')
    if base not in sys.path:
        sys.path.append(base)
    from entities.platform import Platform  # type: ignore
    from entities.platform import FloatingPlatform  # type: ignore
    from entities.enemy import Enemy  # type: ignore
    from entities.nightborne import NightBorneEnemy  # type: ignore
    from entities.collectible import Collectible  # type: ignore
    from entities.plant import Plant  # type: ignore

class Level1:
    def __init__(self):
        self.platforms = []
        self.enemies = []
        self.collectibles = []
        self.plants = []
        self.decorations = []
        self._build()

    def _build(self):
        self.platforms.append(Platform((0,500,1400,64), variant=0))
        self.platforms.append(FloatingPlatform((220,420,200,50)))
        self.platforms.append(FloatingPlatform((400,320,160,50)))
        self.platforms.append(FloatingPlatform((650,270,176,50)))
        self.platforms.append(FloatingPlatform((840,170,135,50)))
        self.platforms.append(FloatingPlatform((980,80,128,50)))

        self.gate_rect = pygame.Rect(1120, 500-96, 64, 96)
        self.gate_open = False
        GROUND_Y = 500
        ENEMY_H = 120
        self.enemies.append(NightBorneEnemy((150, GROUND_Y-ENEMY_H), (-40, 60)))
        self.enemies.append(NightBorneEnemy((1100, GROUND_Y-ENEMY_H), (-50, 60)))
        self.enemies.append(NightBorneEnemy((420, 320-ENEMY_H), (-45, 65)))
        self.enemies.append(NightBorneEnemy((860, 170-ENEMY_H), (-55, 70)))

        self.collectibles.append(Collectible((260, 420-32))) 
        self.collectibles.append(Collectible((690, 270-32)))
        self.collectibles.append(Collectible((1000, 80-32)))
        self.collectibles.append(Collectible((360, GROUND_Y-96)))
        self.collectibles.append(Collectible((760, GROUND_Y-96)))

        self.plants.append(Plant('BlueFlower1', (120, GROUND_Y-48)))
        self.plants.append(Plant('BlueFlower1', (500, GROUND_Y-50)))
        self.plants.append(Plant('BlueFlower1', (1040, GROUND_Y-52)))
        self.plants.append(Plant('BlueFlower2', (430, 320-40)))
        self.plants.append(Plant('BlueFlower2', (880, 170-40)))
        self.plants.append(Plant('BlueFlower2', (1010, 80-40)))

    def update(self):
        alive = 0
        for e in self.enemies:
            e.update(self.platforms)
            if e.alive:
                alive += 1
        if alive == 0 and not self.gate_open:
            self.gate_open = True
        for c in self.collectibles:
            c.update()
        for p in self.plants:
            p.update(1/60)
        for d in getattr(self, 'decorations', []):
            d.update(1/60)

    def reset(self):
        self.__init__()
