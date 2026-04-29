import os
import math

# =====================================================
# Configurações
# =====================================================
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# Área de jogo (Touhou-style: retângulo à esquerda)
PLAY_X, PLAY_Y = 20, 20
PLAY_W, PLAY_H = 460, 560

# Painel HUD (à direita)
HUD_X = PLAY_X + PLAY_W + 20
HUD_W = SCREEN_W - HUD_X - 10

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# =====================================================
# Formas temáticas como polígonos
# =====================================================
def _make_player_shape():
    return [(-5, -4), (5, -4), (5, 10), (-5, 10)]

def _make_player_legs():
    return [
        [(-5, 10), (-1, 10), (-1, 16), (-5, 16)],
        [(1, 10), (5, 10), (5, 16), (1, 16)],
    ]

def _make_player_backpack():
    return [(-7, -2), (-5, -2), (-5, 8), (-7, 8)]

def _make_boss_shape():
    pts = []
    for i in range(12):
        a = math.radians(i * 30)
        r = 28 + 4 * (i % 2)
        pts.append((math.cos(a) * r, math.sin(a) * r))
    return pts

def _make_projectile_shape():
    return [(-5, -5), (5, -5), (5, 5), (-5, 5)]

PLAYER_SHAPE = _make_player_shape()
PLAYER_LEGS = _make_player_legs()
PLAYER_BACKPACK = _make_player_backpack()
BOSS_SHAPE = _make_boss_shape()
PROJ_SHAPE = _make_projectile_shape()
