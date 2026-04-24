import os
import pygame

from .config import ASSETS_DIR


class Assets:
    """Contêiner de texturas e sprites carregados."""
    ground_tex = None
    ground_tex_w = 0
    ground_tex_h = 0
    boss_sprite = None
    boss_sprite_w = 0
    boss_sprite_h = 0
    grade_sprites = {}  # {kind: (pixels, w, h)}
    lapis_sprite = None
    lapis_sprite_w = 0
    lapis_sprite_h = 0

    @classmethod
    def init(cls):
        cls.ground_tex, cls.ground_tex_w, cls.ground_tex_h = cls._load_texture(
            os.path.join(ASSETS_DIR, "texture_ground.png")
        )
        cls._load_boss_sprite()
        cls._load_grade_sprites()
        cls._load_lapis_sprite()

    @classmethod
    def _load_texture(cls, path):
        if not os.path.exists(path):
            # Gera textura procedural (piso de sala de aula)
            size = 32
            pixels = []
            for y in range(size):
                row = []
                for x in range(size):
                    if (x // 4 + y // 4) % 2 == 0:
                        row.append((70, 65, 55))
                    else:
                        row.append((55, 50, 42))
                pixels.append(row)
            return pixels, size, size

        img = pygame.image.load(path)
        w, h = img.get_width(), img.get_height()
        pixels = []
        for y in range(h):
            row = []
            for x in range(w):
                c = img.get_at((x, y))
                row.append((c[0], c[1], c[2]))
            pixels.append(row)
        return pixels, w, h

    @classmethod
    def _load_boss_sprite(cls):
        path = os.path.join(ASSETS_DIR, "negresco.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            cls.boss_sprite_w, cls.boss_sprite_h = img.get_width(), img.get_height()
            cls.boss_sprite = []
            for y in range(cls.boss_sprite_h):
                row = []
                for x in range(cls.boss_sprite_w):
                    c = img.get_at((x, y))
                    row.append((c[0], c[1], c[2], c[3] if len(c) > 3 else 255))
                cls.boss_sprite.append(row)

    @classmethod
    def _load_grade_sprites(cls):
        grade_files = {
            0: "nota_d.png",
            1: "nota_d-.png",
            2: "nota_f.png",
        }
        for kind, filename in grade_files.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_width(), img.get_height()
                pixels = []
                for y in range(h):
                    row = []
                    for x in range(w):
                        c = img.get_at((x, y))
                        r, g, b = c[0], c[1], c[2]
                        a = c[3] if len(c) > 3 else 255
                        # Tratar pixels claros como transparentes
                        if r > 220 and g > 220 and b > 220:
                            a = 0
                        row.append((r, g, b, a))
                    pixels.append(row)
                cls.grade_sprites[kind] = (pixels, w, h)

    @classmethod
    def _load_lapis_sprite(cls):
        path = os.path.join(ASSETS_DIR, "lapis.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            cls.lapis_sprite_w, cls.lapis_sprite_h = img.get_width(), img.get_height()
            cls.lapis_sprite = []
            for y in range(cls.lapis_sprite_h):
                row = []
                for x in range(cls.lapis_sprite_w):
                    c = img.get_at((x, y))
                    r, g, b = c[0], c[1], c[2]
                    a = c[3] if len(c) > 3 else 255
                    if r > 230 and g > 230 and b > 230:
                        a = 0
                    row.append((r, g, b, a))
                cls.lapis_sprite.append(row)
