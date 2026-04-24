import pygame
import sys
import math
import random
import os

from graphics import (
    set_pixel, draw_line, draw_circle, draw_filled_circle,
    draw_ellipse, draw_filled_ellipse,
    draw_polygon, scanline_fill, scanline_fill_gradient, scanline_fill_texture,
    flood_fill, draw_text, draw_text_centered, text_width,
    draw_rect, fill_rect,
    identity, translation, scale, rotation, mat_mult, apply_transform,
    transform_point, window_to_viewport,
    cohen_sutherland, draw_line_clipped, draw_polygon_clipped,
)

# =====================================================
# Configurações
# =====================================================
SCREEN_W, SCREEN_H = 800, 600
WORLD_W, WORLD_H = 2000, 2000
FPS = 60

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Sobreviva ao Semestre!")
clock = pygame.time.Clock()

# =====================================================
# Carregar textura (se existir)
# =====================================================
def load_texture(path):
    """Carrega imagem para matriz de pixels (permitido pelo enunciado)."""
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

GROUND_TEX, GROUND_TEX_W, GROUND_TEX_H = load_texture("texture_ground.png")

# =====================================================
# Carregar sprite do boss (imagem do professor)
# =====================================================
BOSS_SPRITE = None
BOSS_SPRITE_W, BOSS_SPRITE_H = 0, 0

def load_boss_sprite():
    global BOSS_SPRITE, BOSS_SPRITE_W, BOSS_SPRITE_H
    path = os.path.join(os.path.dirname(__file__), "negresco.png")
    if os.path.exists(path):
        img = pygame.image.load(path)
        BOSS_SPRITE_W, BOSS_SPRITE_H = img.get_width(), img.get_height()
        BOSS_SPRITE = []
        for y in range(BOSS_SPRITE_H):
            row = []
            for x in range(BOSS_SPRITE_W):
                c = img.get_at((x, y))
                row.append((c[0], c[1], c[2], c[3] if len(c) > 3 else 255))
            BOSS_SPRITE.append(row)

load_boss_sprite()

# =====================================================
# Formas temáticas como polígonos
# =====================================================
def make_player_shape():
    """Jogador: forma de pessoa/aluno (hexágono simples)."""
    return [(-6, -12), (6, -12), (10, -2), (6, 12), (-6, 12), (-10, -2)]

def make_grade_shape():
    """Nota baixa: retângulo (como uma prova/folha)."""
    return [(-9, -11), (9, -11), (9, 11), (-9, 11)]

def make_fast_grade_shape():
    """Nota baixa rápida: mais estreita."""
    return [(-6, -10), (6, -10), (6, 10), (-6, 10)]

def make_tank_grade_shape():
    """Nota baixa tanque: maior."""
    return [(-12, -14), (12, -14), (12, 14), (-12, 14)]

def make_boss_shape():
    """Boss: forma circular aproximada (biscoito Negresco) via polígono."""
    pts = []
    for i in range(12):
        a = math.radians(i * 30)
        r = 28 + 4 * (i % 2)  # ondulado tipo biscoito
        pts.append((math.cos(a) * r, math.sin(a) * r))
    return pts

def make_projectile_shape():
    """Projétil: lápis/café (triângulo alongado)."""
    return [(0, -5), (3, 4), (-3, 4)]

def make_xp_shape():
    """XP: nota boa (diamante com +)."""
    return [(0, -6), (5, 0), (0, 6), (-5, 0)]

PLAYER_SHAPE = make_player_shape()
GRADE_SHAPES = [make_grade_shape(), make_fast_grade_shape(), make_tank_grade_shape()]
BOSS_SHAPE = make_boss_shape()
PROJ_SHAPE = make_projectile_shape()
XP_SHAPE = make_xp_shape()

# Notas que aparecem nos inimigos
GRADE_LABELS = ["2", "1", "0", "3", "0.5"]
GRADE_COLORS = {
    0: ((220, 60, 60), (255, 120, 120), "2"),    # nota 2 - vermelho
    1: ((220, 160, 40), (255, 200, 80), "1"),     # nota 1 - laranja (rápido)
    2: ((140, 40, 180), (200, 100, 255), "0"),    # nota 0 - roxo (tanque)
}

# =====================================================
# Estado do Jogo
# =====================================================
class GameState:
    TITLE = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0
        self.target_zoom = 1.0

    def update(self, target_x, target_y):
        self.x += (target_x - SCREEN_W / 2 - self.x) * 0.1
        self.y += (target_y - SCREEN_H / 2 - self.y) * 0.1
        self.zoom += (self.target_zoom - self.zoom) * 0.05

    def world_to_screen(self, wx, wy):
        sx = (wx - self.x) * self.zoom
        sy = (wy - self.y) * self.zoom
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = sx / self.zoom + self.x
        wy = sy / self.zoom + self.y
        return wx, wy

    def get_clip_rect(self):
        x0, y0 = self.screen_to_world(0, 0)
        x1, y1 = self.screen_to_world(SCREEN_W, SCREEN_H)
        return (x0, y0, x1, y1)

class Player:
    def __init__(self):
        self.x = WORLD_W / 2
        self.y = WORLD_H / 2
        self.speed = 3.0
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.xp = 0
        self.xp_next = 10
        self.angle = 0.0
        self.attack_timer = 0
        self.attack_cooldown = 15  # frames
        self.damage = 10
        self.proj_speed = 6.0
        self.invincible = 0

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.angle = math.atan2(dy, dx)

        # Limitar ao mundo
        self.x = max(20, min(WORLD_W - 20, self.x))
        self.y = max(20, min(WORLD_H - 20, self.y))

        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.5)
            self.max_hp += 10
            self.hp = min(self.hp + 20, self.max_hp)
            self.damage += 2
            if self.attack_cooldown > 5:
                self.attack_cooldown -= 1
            return True
        return False

class Enemy:
    def __init__(self, x, y, hp=20, speed=1.2, damage=5, kind=0, is_boss=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.kind = kind  # 0=nota2, 1=nota1(fast), 2=nota0(tank)
        self.is_boss = is_boss
        self.angle = 0.0
        self.anim_timer = random.uniform(0, math.pi * 2)

    def update(self, px, py):
        self.anim_timer += 0.05
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 1:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
            self.angle = math.atan2(dy, dx)

class Projectile:
    def __init__(self, x, y, angle, speed, damage):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.lifetime = 90
        self.angle = angle

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

class XPOrb:
    def __init__(self, x, y, value=1):
        self.x = x
        self.y = y
        self.value = value

# =====================================================
# Jogo principal
# =====================================================
class Game:
    def __init__(self):
        self.state = GameState.TITLE
        self.player = Player()
        self.camera = Camera()
        self.enemies = []
        self.projectiles = []
        self.xp_orbs = []
        self.spawn_timer = 0
        self.spawn_rate = 60  # frames
        self.frame = 0
        self.score = 0
        self.title_anim = 0.0
        self.menu_selection = 0  # 0=Jogar, 1=Sair
        self.boss_spawned = False
        self.boss_alive = False
        self.semester_timer = 0  # tempo de jogo em frames
        self.boss_spawn_time = 60 * 90  # boss aparece após ~90 segundos

    def reset(self):
        self.player = Player()
        self.camera = Camera()
        self.enemies.clear()
        self.projectiles.clear()
        self.xp_orbs.clear()
        self.spawn_timer = 0
        self.spawn_rate = 60
        self.frame = 0
        self.score = 0
        self.boss_spawned = False
        self.boss_alive = False
        self.semester_timer = 0

    def spawn_enemy(self):
        # Spawn fora da tela
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(400, 600)
        ex = self.player.x + math.cos(angle) * dist
        ey = self.player.y + math.sin(angle) * dist
        ex = max(10, min(WORLD_W - 10, ex))
        ey = max(10, min(WORLD_H - 10, ey))

        difficulty = self.player.level
        kind = random.choices([0, 1, 2], weights=[5, 3, 2])[0]
        if kind == 0:
            hp = 15 + difficulty * 3
            spd = 1.0 + difficulty * 0.05
            dmg = 5 + difficulty
        elif kind == 1:
            hp = 10 + difficulty * 2
            spd = 2.0 + difficulty * 0.1
            dmg = 3 + difficulty
        else:
            hp = 40 + difficulty * 5
            spd = 0.6 + difficulty * 0.02
            dmg = 8 + difficulty * 2

        self.enemies.append(Enemy(ex, ey, hp, spd, dmg, kind))

    def spawn_boss(self):
        """Spawna o boss: Professor Negresco!"""
        angle = random.uniform(0, 2 * math.pi)
        dist = 500
        ex = self.player.x + math.cos(angle) * dist
        ey = self.player.y + math.sin(angle) * dist
        ex = max(50, min(WORLD_W - 50, ex))
        ey = max(50, min(WORLD_H - 50, ey))

        boss_hp = 300 + self.player.level * 30
        boss = Enemy(ex, ey, boss_hp, 0.8, 20, kind=0, is_boss=True)
        self.enemies.append(boss)
        self.boss_spawned = True
        self.boss_alive = True

    def auto_attack(self):
        """Atira automaticamente no inimigo mais próximo."""
        if self.player.attack_timer > 0:
            return
        if not self.enemies:
            return

        closest = None
        min_dist = float('inf')
        for e in self.enemies:
            dx = e.x - self.player.x
            dy = e.y - self.player.y
            d = dx * dx + dy * dy
            if d < min_dist:
                min_dist = d
                closest = e

        if closest and min_dist < 300 * 300:
            angle = math.atan2(closest.y - self.player.y, closest.x - self.player.x)
            self.projectiles.append(
                Projectile(self.player.x, self.player.y, angle,
                           self.player.proj_speed, self.player.damage)
            )
            self.player.attack_timer = self.player.attack_cooldown

    def update(self):
        if self.state != GameState.PLAYING:
            return

        self.frame += 1
        self.semester_timer += 1
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.camera.update(self.player.x, self.player.y)

        # Zoom com scroll ou teclas
        if keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS]:
            self.camera.target_zoom = min(3.0, self.camera.target_zoom + 0.02)
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
            self.camera.target_zoom = max(0.3, self.camera.target_zoom - 0.02)

        # Boss spawn
        if not self.boss_spawned and self.semester_timer >= self.boss_spawn_time:
            self.spawn_boss()

        # Spawn inimigos normais
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            num = 1 + self.player.level // 3
            for _ in range(num):
                self.spawn_enemy()
            if self.spawn_rate > 15:
                self.spawn_rate -= 1

        # Ataque automático
        self.auto_attack()

        # Atualiza inimigos
        for e in self.enemies:
            e.update(self.player.x, self.player.y)
            # Colisão com jogador
            dx = e.x - self.player.x
            dy = e.y - self.player.y
            if dx * dx + dy * dy < 20 * 20 and self.player.invincible <= 0:
                self.player.hp -= e.damage
                self.player.invincible = 30

        # Atualiza projéteis
        for p in self.projectiles:
            p.update()
            # Colisão com inimigos
            for e in self.enemies:
                dx = p.x - e.x
                dy = p.y - e.y
                if dx * dx + dy * dy < 12 * 12:
                    e.hp -= p.damage
                    p.lifetime = 0
                    break

        # Remove mortos
        dead_enemies = [e for e in self.enemies if e.hp <= 0]
        for e in dead_enemies:
            if e.is_boss:
                self.boss_alive = False
                self.score += 500
                # Muitos orbs do boss
                for _ in range(20):
                    ox = e.x + random.uniform(-30, 30)
                    oy = e.y + random.uniform(-30, 30)
                    self.xp_orbs.append(XPOrb(ox, oy, 5))
            else:
                self.xp_orbs.append(XPOrb(e.x, e.y, 1 + self.player.level // 2))
                self.score += 10

        self.enemies = [e for e in self.enemies if e.hp > 0]
        self.projectiles = [p for p in self.projectiles if p.lifetime > 0]

        # Verificar vitória: boss morto
        if self.boss_spawned and not self.boss_alive and not any(e.is_boss for e in self.enemies):
            # Checar se já coletou os orbs (espera um pouco)
            if self.semester_timer > self.boss_spawn_time + 120:
                self.state = GameState.VICTORY

        # Coletar XP
        for orb in self.xp_orbs[:]:
            dx = orb.x - self.player.x
            dy = orb.y - self.player.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 50:
                # Atrai
                orb.x -= dx * 0.2
                orb.y -= dy * 0.2
            if dist < 15:
                self.player.gain_xp(orb.value)
                self.xp_orbs.remove(orb)

        # Limitar inimigos/orbs longe
        self.enemies = [e for e in self.enemies
                        if abs(e.x - self.player.x) < 800 and abs(e.y - self.player.y) < 800]
        self.xp_orbs = [o for o in self.xp_orbs
                        if abs(o.x - self.player.x) < 600 and abs(o.y - self.player.y) < 600]

        if self.player.hp <= 0:
            self.state = GameState.GAME_OVER

    # =====================================================
    # RENDERIZAÇÃO
    # =====================================================
    def render(self):
        screen.fill((0, 0, 0))

        if self.state == GameState.TITLE:
            self.render_title()
        elif self.state in (GameState.PLAYING, GameState.PAUSED):
            self.render_game()
            if self.state == GameState.PAUSED:
                self.render_pause()
        elif self.state == GameState.GAME_OVER:
            self.render_game()
            self.render_game_over()
        elif self.state == GameState.VICTORY:
            self.render_game()
            self.render_victory()

        pygame.display.flip()

    def render_title(self):
        """Tela de abertura usando retas, círculos e elipses + flood fill."""
        self.title_anim += 0.03

        # Fundo escuro (lousa)
        screen.fill((15, 25, 15))

        # Polígono com gradiente (quadro verde)
        grad_pts = [(40, 60), (SCREEN_W - 40, 60), (SCREEN_W - 40, 350), (40, 350)]
        grad_colors = [(20, 60, 30), (30, 80, 40), (25, 70, 35), (15, 50, 25)]
        scanline_fill_gradient(screen, grad_pts, grad_colors)

        # Moldura do quadro com retas (Bresenham)
        for i in range(4):
            draw_rect(screen, 38 + i, 58 + i, SCREEN_W - 78 - 2 * i, 294 - 2 * i,
                      (120 + i * 20, 80 + i * 10, 30))

        # Título
        title = "SOBREVIVA AO SEMESTRE"
        bob = int(math.sin(self.title_anim * 2) * 4)
        draw_text_centered(screen, title, SCREEN_W // 2, 100 + bob, (255, 255, 220), 4)

        draw_text_centered(screen, "DERROTE AS NOTAS BAIXAS", SCREEN_W // 2, 145,
                           (200, 200, 150), 2)

        # Círculos decorativos - notas flutuando (Bresenham circunferência)
        grades = ["0", "1", "2", "3", "0"]
        for i in range(5):
            cx = 120 + i * 140
            cy = 200
            r = int(18 + 6 * math.sin(self.title_anim + i))
            cval = int(180 + 75 * math.sin(self.title_anim + i * 0.7))
            draw_circle(screen, cx, cy, r, (cval, 50, 50))
            draw_text_centered(screen, grades[i], cx, cy, (255, 200, 200), 2)

        # Elipses decorativas (Bresenham elipse)
        for i in range(3):
            cx = 200 + i * 200
            cy = 280
            rx = int(25 + 10 * math.sin(self.title_anim * 1.5 + i))
            ry = int(12 + 5 * math.cos(self.title_anim * 1.5 + i))
            draw_filled_ellipse(screen, cx, cy, rx, ry, (80, 50, 20))
            draw_ellipse(screen, cx, cy, rx, ry, (140, 90, 40))

        # Ícone aluno (círculo preenchido com flood fill)
        pcx, pcy = SCREEN_W // 2, 330
        draw_circle(screen, pcx, pcy, 15, (100, 180, 255))
        flood_fill(screen, pcx, pcy, (100, 180, 255), (100, 180, 255))
        # Capelo
        draw_line(screen, pcx - 18, pcy - 12, pcx + 18, pcy - 12, (255, 220, 50))
        draw_line(screen, pcx - 18, pcy - 12, pcx, pcy - 22, (255, 220, 50))
        draw_line(screen, pcx + 18, pcy - 12, pcx, pcy - 22, (255, 220, 50))

        # Raios de conhecimento
        for i in range(8):
            a = self.title_anim + i * math.pi / 4
            x1 = pcx + int(math.cos(a) * 25)
            y1 = pcy + int(math.sin(a) * 25)
            x2 = pcx + int(math.cos(a) * 40)
            y2 = pcy + int(math.sin(a) * 40)
            draw_line(screen, x1, y1, x2, y2, (255, 255, 150))

        # Boss preview
        draw_text_centered(screen, "BOSS FINAL", SCREEN_W // 2, 380, (200, 100, 50), 2)
        draw_filled_ellipse(screen, SCREEN_W // 2, 410, 30, 18, (60, 30, 10))
        draw_ellipse(screen, SCREEN_W // 2, 410, 30, 18, (120, 70, 30))
        draw_text_centered(screen, "NEGRESCO", SCREEN_W // 2, 410, (200, 180, 140), 1)

        # Menu
        items = ["JOGAR", "SAIR"]
        for idx, item in enumerate(items):
            cy = 460 + idx * 35
            color = (255, 255, 0) if idx == self.menu_selection else (180, 180, 180)
            if idx == self.menu_selection:
                draw_text_centered(screen, "> " + item + " <", SCREEN_W // 2, cy, color, 3)
            else:
                draw_text_centered(screen, item, SCREEN_W // 2, cy, color, 3)

        draw_text_centered(screen, "WASD MOVER  +/- ZOOM  ESC PAUSAR",
                           SCREEN_W // 2, 560, (100, 100, 100), 2)

    def render_game(self):
        cam = self.camera
        clip = cam.get_clip_rect()

        # Fundo - grade de chão com linhas
        self._render_ground()

        # Borda do mundo (com recorte Cohen-Sutherland)
        corners = [(0, 0), (WORLD_W, 0), (WORLD_W, WORLD_H), (0, WORLD_H)]
        screen_corners = [cam.world_to_screen(x, y) for x, y in corners]
        clip_screen = (0, 0, SCREEN_W - 1, SCREEN_H - 1)
        draw_polygon_clipped(screen, screen_corners, (100, 100, 100), clip_screen)

        # XP orbs (notas boas - aprovações)
        for orb in self.xp_orbs:
            sx, sy = cam.world_to_screen(orb.x, orb.y)
            if 0 <= sx < SCREEN_W and 0 <= sy < SCREEN_H:
                pts = self._transform_shape(XP_SHAPE, orb.x, orb.y, 0, cam)
                colors = [(50, 255, 100), (150, 255, 50), (50, 200, 80), (100, 255, 180)]
                scanline_fill_gradient(screen, pts, colors)
                draw_text_centered(screen, "+", int(sx), int(sy), (255, 255, 255), 1)

        # Inimigos (notas baixas)
        for e in self.enemies:
            sx, sy = cam.world_to_screen(e.x, e.y)
            if -40 < sx < SCREEN_W + 40 and -40 < sy < SCREEN_H + 40:
                if e.is_boss:
                    self._render_boss(e, sx, sy, cam)
                else:
                    sc = 1.0 + (e.kind * 0.3)
                    shape = GRADE_SHAPES[e.kind]
                    wobble = math.sin(e.anim_timer) * 0.1
                    pts = self._transform_shape(shape, e.x, e.y, wobble, cam, sc)
                    fill_c, border_c, label = GRADE_COLORS[e.kind]
                    scanline_fill(screen, pts, fill_c)
                    draw_polygon(screen, pts, border_c)
                    # Desenha a nota no centro do inimigo
                    draw_text_centered(screen, label, int(sx), int(sy),
                                       (255, 255, 255), 2)

                # Barra de HP
                if e.hp < e.max_hp:
                    bar_w = 20 if not e.is_boss else 50
                    ratio = e.hp / e.max_hp
                    bar_color = (255, 50, 50) if not e.is_boss else (255, 200, 0)
                    fill_rect(screen, sx - bar_w / 2, sy - 20, bar_w * ratio, 3, bar_color)
                    draw_rect(screen, sx - bar_w / 2, sy - 20, bar_w, 3, (200, 200, 200))

        # Projéteis (café/conhecimento)
        for p in self.projectiles:
            sx, sy = cam.world_to_screen(p.x, p.y)
            if -10 < sx < SCREEN_W + 10 and -10 < sy < SCREEN_H + 10:
                pts = self._transform_shape(PROJ_SHAPE, p.x, p.y, p.angle, cam)
                scanline_fill(screen, pts, (180, 120, 50))
                draw_polygon(screen, pts, (220, 170, 80))

        # Jogador (aluno)
        blink = self.player.invincible > 0 and (self.frame % 4 < 2)
        if not blink:
            pts = self._transform_shape(PLAYER_SHAPE, self.player.x, self.player.y,
                                        self.player.angle, cam)
            # Gradiente azul (uniforme de aluno)
            player_colors = [
                (40, 100, 200), (60, 140, 230), (30, 80, 180),
                (50, 120, 210), (35, 90, 190), (45, 110, 220)
            ]
            scanline_fill_gradient(screen, pts, player_colors)
            draw_polygon(screen, pts, (150, 200, 255))

        # HUD
        self._render_hud()

        # Minimapa (viewport)
        self._render_minimap()

        # Aviso de boss
        if self.boss_spawned and self.boss_alive:
            if self.frame % 60 < 30:
                draw_text_centered(screen, "BOSS: PROF. NEGRESCO",
                                   SCREEN_W // 2, 50, (255, 100, 50), 3)

    def _render_boss(self, e, sx, sy, cam):
        """Renderiza o boss Negresco."""
        # Se tem sprite carregado, renderiza com textura
        if BOSS_SPRITE:
            # Mapear sprite na forma do boss usando textura
            boss_sc = 1.5
            pts = self._transform_shape(BOSS_SHAPE, e.x, e.y, e.anim_timer * 0.3, cam, boss_sc)
            tex_coords = []
            for px, py in BOSS_SHAPE:
                u = (px + 32) / 64
                v = (py + 32) / 64
                tex_coords.append((max(0, min(1, u)), max(0, min(1, v))))
            scanline_fill_texture(screen, pts, tex_coords,
                                  BOSS_SPRITE, BOSS_SPRITE_W, BOSS_SPRITE_H)
            draw_polygon(screen, pts, (180, 120, 60))
        else:
            # Sem sprite: desenha biscoito procedural
            boss_sc = 1.5
            pts = self._transform_shape(BOSS_SHAPE, e.x, e.y, e.anim_timer * 0.3, cam, boss_sc)
            # Gradiente marrom (biscoito)
            boss_colors = []
            for i in range(len(pts)):
                shade = 40 + (i * 15) % 60
                boss_colors.append((shade + 30, shade, shade - 10 if shade > 10 else 0))
            scanline_fill_gradient(screen, pts, boss_colors)
            draw_polygon(screen, pts, (150, 100, 40))

        # Nome do boss
        draw_text_centered(screen, "NEGRESCO", int(sx), int(sy) - 35, (255, 200, 100), 2)
        # Barra de HP grande
        bar_w = 60
        ratio = e.hp / e.max_hp
        fill_rect(screen, sx - bar_w / 2, sy + 35, bar_w * ratio, 4, (255, 50, 50))
        draw_rect(screen, sx - bar_w / 2, sy + 35, bar_w, 4, (255, 200, 100))

    def _render_ground(self):
        """Renderiza chão: fundo sólido + grid de linhas Bresenham."""
        cam = self.camera

        # Fundo sólido do mundo (usa fill do pygame - é apenas set_pixel em massa)
        # Determinar rect do mundo visível na tela
        w_tl = cam.world_to_screen(0, 0)
        w_br = cam.world_to_screen(WORLD_W, WORLD_H)
        rx = max(0, int(w_tl[0]))
        ry = max(0, int(w_tl[1]))
        rw = min(SCREEN_W, int(w_br[0])) - rx
        rh = min(SCREEN_H, int(w_br[1])) - ry
        if rw > 0 and rh > 0:
            screen.fill((45, 55, 45), (rx, ry, rw, rh))

        # Grid com linhas Bresenham (piso quadriculado)
        grid_size = 128
        x0w, y0w = cam.screen_to_world(0, 0)
        x1w, y1w = cam.screen_to_world(SCREEN_W, SCREEN_H)

        # Linhas verticais
        gx_start = int(x0w // grid_size) * grid_size
        for gx in range(gx_start, int(x1w) + grid_size, grid_size):
            if 0 <= gx <= WORLD_W:
                sx, sy0 = cam.world_to_screen(gx, max(0, y0w))
                _, sy1 = cam.world_to_screen(gx, min(WORLD_H, y1w))
                draw_line_clipped(screen, int(sx), int(sy0), int(sx), int(sy1),
                                  (55, 70, 55), 0, 0, SCREEN_W - 1, SCREEN_H - 1)

        # Linhas horizontais
        gy_start = int(y0w // grid_size) * grid_size
        for gy in range(gy_start, int(y1w) + grid_size, grid_size):
            if 0 <= gy <= WORLD_H:
                sx0, sy = cam.world_to_screen(max(0, x0w), gy)
                sx1, _ = cam.world_to_screen(min(WORLD_W, x1w), gy)
                draw_line_clipped(screen, int(sx0), int(sy), int(sx1), int(sy),
                                  (55, 70, 55), 0, 0, SCREEN_W - 1, SCREEN_H - 1)

        # Textura mapeada em uma área decorativa (centro do mundo) - requisito
        tex_world_x, tex_world_y = WORLD_W // 2 - 64, WORLD_H // 2 - 64
        tex_corners_w = [
            (tex_world_x, tex_world_y), (tex_world_x + 128, tex_world_y),
            (tex_world_x + 128, tex_world_y + 128), (tex_world_x, tex_world_y + 128)
        ]
        tex_corners_s = [cam.world_to_screen(cx, cy) for cx, cy in tex_corners_w]
        xs = [c[0] for c in tex_corners_s]
        ys = [c[1] for c in tex_corners_s]
        if max(xs) > 0 and min(xs) < SCREEN_W and max(ys) > 0 and min(ys) < SCREEN_H:
            tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
            scanline_fill_texture(screen, tex_corners_s, tex_coords,
                                  GROUND_TEX, GROUND_TEX_W, GROUND_TEX_H)

    def _transform_shape(self, shape, wx, wy, angle, cam, extra_scale=1.0):
        """Transforma shape: escala, rotação, translação, câmera."""
        m = identity()
        m = mat_mult(rotation(angle), m)
        m = mat_mult(scale(extra_scale * cam.zoom, extra_scale * cam.zoom), m)
        pts = apply_transform(m, shape)
        sx, sy = cam.world_to_screen(wx, wy)
        return [(px + sx, py + sy) for px, py in pts]

    def _render_hud(self):
        """Renderiza HUD temático: HP, XP, nível, score, semestre."""
        p = self.player

        # Barra de HP (energia do aluno)
        bar_x, bar_y, bar_w, bar_h = 10, 10, 200, 14
        fill_rect(screen, bar_x, bar_y, bar_w, bar_h, (40, 40, 40))
        hp_ratio = max(0, p.hp / p.max_hp)
        hp_color = (50, 220, 50) if hp_ratio > 0.5 else (220, 220, 50) if hp_ratio > 0.25 else (220, 50, 50)
        fill_rect(screen, bar_x + 1, bar_y + 1, int((bar_w - 2) * hp_ratio), bar_h - 2, hp_color)
        draw_rect(screen, bar_x, bar_y, bar_w, bar_h, (200, 200, 200))
        draw_text(screen, f"ENERGIA {p.hp}/{p.max_hp}", bar_x + 4, bar_y + 4, (255, 255, 255), 1)

        # Barra de XP (conhecimento)
        xp_y = bar_y + bar_h + 4
        fill_rect(screen, bar_x, xp_y, bar_w, 8, (20, 20, 40))
        xp_ratio = p.xp / p.xp_next if p.xp_next > 0 else 0
        fill_rect(screen, bar_x + 1, xp_y + 1, int((bar_w - 2) * xp_ratio), 6, (100, 100, 255))
        draw_rect(screen, bar_x, xp_y, bar_w, 8, (150, 150, 200))

        # Período e Score
        draw_text(screen, f"PERIODO {p.level}", bar_x, xp_y + 14, (200, 200, 255), 2)
        draw_text(screen, f"NOTA {self.score}", bar_x + 120, xp_y + 14, (255, 255, 200), 2)

        # Timer do semestre
        secs = self.semester_timer // 60
        boss_secs = self.boss_spawn_time // 60
        remaining = max(0, boss_secs - secs)
        if not self.boss_spawned:
            draw_text(screen, f"BOSS EM {remaining}S", SCREEN_W - 170, 10, (255, 180, 80), 2)
        else:
            draw_text(screen, "BOSS ATIVO", SCREEN_W - 150, 10, (255, 80, 80), 2)

        # Contadores
        draw_text(screen, f"NOTAS {len(self.enemies)}", SCREEN_W - 150, 30, (200, 200, 200), 1)

    def _render_minimap(self):
        """Viewport do minimapa com transformação janela->viewport e recorte."""
        vp_x, vp_y, vp_w, vp_h = SCREEN_W - 160, SCREEN_H - 120, 150, 110

        # Fundo do minimapa
        fill_rect(screen, vp_x, vp_y, vp_w, vp_h, (10, 10, 20))
        draw_rect(screen, vp_x, vp_y, vp_w, vp_h, (100, 100, 100))

        # Transformação janela mundo -> viewport minimapa
        world_window = (0, 0, WORLD_W, WORLD_H)
        viewport = (vp_x, vp_y, vp_x + vp_w, vp_y + vp_h)
        m = window_to_viewport(world_window, viewport)
        clip = (vp_x, vp_y, vp_x + vp_w, vp_y + vp_h)

        # Jogador no minimapa
        px, py = transform_point(m, self.player.x, self.player.y)
        draw_filled_circle(screen, int(px), int(py), 3, (50, 150, 255))

        # Inimigos no minimapa
        for e in self.enemies:
            ex, ey = transform_point(m, e.x, e.y)
            if vp_x <= ex <= vp_x + vp_w and vp_y <= ey <= vp_y + vp_h:
                set_pixel(screen, int(ex), int(ey), (255, 80, 80))

        # Câmera view rect no minimapa (com recorte Cohen-Sutherland)
        cx0, cy0 = self.camera.screen_to_world(0, 0)
        cx1, cy1 = self.camera.screen_to_world(SCREEN_W, SCREEN_H)
        cam_corners = [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)]
        cam_screen = apply_transform(m, cam_corners)
        draw_polygon_clipped(screen, cam_screen, (255, 255, 0), clip)

    def render_pause(self):
        fill_rect(screen, SCREEN_W // 2 - 180, SCREEN_H // 2 - 50, 360, 100, (0, 0, 0))
        draw_rect(screen, SCREEN_W // 2 - 180, SCREEN_H // 2 - 50, 360, 100, (200, 200, 0))

        draw_text_centered(screen, "AULA PAUSADA", SCREEN_W // 2, SCREEN_H // 2 - 20, (255, 255, 0), 4)
        draw_text_centered(screen, "P PARA CONTINUAR", SCREEN_W // 2, SCREEN_H // 2 + 30,
                           (200, 200, 200), 2)

    def render_game_over(self):
        fill_rect(screen, SCREEN_W // 2 - 180, SCREEN_H // 2 - 80, 360, 160, (30, 0, 0))
        draw_rect(screen, SCREEN_W // 2 - 180, SCREEN_H // 2 - 80, 360, 160, (255, 50, 50))
        draw_text_centered(screen, "REPROVADO", SCREEN_W // 2, SCREEN_H // 2 - 50, (255, 50, 50), 5)
        draw_text_centered(screen, "O SEMESTRE TE VENCEU",
                           SCREEN_W // 2, SCREEN_H // 2, (255, 180, 180), 2)
        draw_text_centered(screen, f"NOTA FINAL {self.score}", SCREEN_W // 2, SCREEN_H // 2 + 25,
                           (255, 255, 200), 3)
        draw_text_centered(screen, "ENTER PARA TENTAR DE NOVO",
                           SCREEN_W // 2, SCREEN_H // 2 + 55, (200, 200, 200), 2)

    def render_victory(self):
        fill_rect(screen, SCREEN_W // 2 - 200, SCREEN_H // 2 - 90, 400, 180, (0, 20, 0))
        draw_rect(screen, SCREEN_W // 2 - 200, SCREEN_H // 2 - 90, 400, 180, (50, 255, 50))
        draw_text_centered(screen, "APROVADO", SCREEN_W // 2, SCREEN_H // 2 - 55, (50, 255, 50), 5)
        draw_text_centered(screen, "VOCE SOBREVIVEU AO SEMESTRE",
                           SCREEN_W // 2, SCREEN_H // 2 - 10, (200, 255, 200), 2)
        draw_text_centered(screen, "PROF NEGRESCO DERROTADO",
                           SCREEN_W // 2, SCREEN_H // 2 + 15, (255, 220, 100), 2)
        draw_text_centered(screen, f"NOTA FINAL {self.score}", SCREEN_W // 2, SCREEN_H // 2 + 40,
                           (255, 255, 200), 3)
        draw_text_centered(screen, "ENTER PARA VOLTAR",
                           SCREEN_W // 2, SCREEN_H // 2 + 65, (200, 200, 200), 2)

    # =====================================================
    # EVENTS
    # =====================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == GameState.TITLE:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_selection = (self.menu_selection - 1) % 2
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_selection = (self.menu_selection + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menu_selection == 0:
                            self.reset()
                            self.state = GameState.PLAYING
                        else:
                            return False

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.TITLE

                elif self.state == GameState.VICTORY:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.TITLE

            if event.type == pygame.MOUSEWHEEL and self.state == GameState.PLAYING:
                self.camera.target_zoom = max(0.3, min(3.0,
                    self.camera.target_zoom + event.y * 0.1))

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
