import os
import math

# =====================================================
# Configurações
# =====================================================
SCREEN_W, SCREEN_H = 800, 600
WORLD_W, WORLD_H = 2000, 2000
FPS = 60

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# =====================================================
# Formas temáticas como polígonos
# =====================================================
def _make_player_shape():
    # Corpo do estudante (torso retangular)
    return [(-5, -4), (5, -4), (5, 10), (-5, 10)]

def _make_player_legs():
    # Pernas (dois retângulos)
    return [
        [(-5, 10), (-1, 10), (-1, 16), (-5, 16)],  # perna esq
        [(1, 10), (5, 10), (5, 16), (1, 16)],       # perna dir
    ]

def _make_player_backpack():
    # Mochila nas costas
    return [(-7, -2), (-5, -2), (-5, 8), (-7, 8)]

def _make_grade_shape():
    return [(-12, -12), (12, -12), (12, 12), (-12, 12)]

def _make_fast_grade_shape():
    return [(-10, -10), (10, -10), (10, 10), (-10, 10)]

def _make_tank_grade_shape():
    return [(-15, -15), (15, -15), (15, 15), (-15, 15)]

def _make_boss_shape():
    pts = []
    for i in range(12):
        a = math.radians(i * 30)
        r = 28 + 4 * (i % 2)
        pts.append((math.cos(a) * r, math.sin(a) * r))
    return pts

def _make_projectile_shape():
    return [(-5, -5), (5, -5), (5, 5), (-5, 5)]

def _make_xp_shape():
    return [(0, -6), (5, 0), (0, 6), (-5, 0)]

PLAYER_SHAPE = _make_player_shape()
PLAYER_LEGS = _make_player_legs()
PLAYER_BACKPACK = _make_player_backpack()
GRADE_SHAPES = [_make_grade_shape(), _make_fast_grade_shape(), _make_tank_grade_shape()]
BOSS_SHAPE = _make_boss_shape()
PROJ_SHAPE = _make_projectile_shape()
XP_SHAPE = _make_xp_shape()

GRADE_COLORS = {
    0: ((220, 60, 60), (255, 120, 120), "2"),    # nota 2 - vermelho
    1: ((220, 160, 40), (255, 200, 80), "1"),     # nota 1 - laranja (rápido)
    2: ((140, 40, 180), (200, 100, 255), "0"),    # nota 0 - roxo (tanque)
}
