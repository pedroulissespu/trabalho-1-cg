import math
import random
import pygame
import sys

from .config import SCREEN_W, SCREEN_H, PLAY_W, PLAY_H, FPS
from .state import GameState
from .entities import Player, Boss, Projectile, BossProjectile
from .assets import Assets
from .renderer import Renderer


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Sobreviva à Disciplina!")
        self.clock = pygame.time.Clock()

        Assets.init()
        self.renderer = Renderer(self.screen)

        self.state = GameState.TITLE
        self.player = Player()
        self.boss = Boss()
        self.projectiles = []
        self.boss_projectiles = []
        self.frame = 0
        self.fight_timer = 0
        self.title_anim = 0.0
        self.menu_selection = 0
        self.zoom = 1.0
        self.cam_x = PLAY_W / 2
        self.cam_y = PLAY_H / 2

    def reset(self):
        self.player = Player()
        self.boss = Boss()
        self.projectiles.clear()
        self.boss_projectiles.clear()
        self.frame = 0
        self.fight_timer = 0
        self.zoom = 1.0
        self.cam_x = PLAY_W / 2
        self.cam_y = PLAY_H / 2

    def auto_attack(self):
        if self.player.attack_timer > 0:
            return

        mx, my = pygame.mouse.get_pos()
        # Converter posição da tela para coordenadas do mundo via viewport inverso
        from .config import PLAY_X, PLAY_Y
        half_w = (PLAY_W / self.zoom) / 2
        half_h = (PLAY_H / self.zoom) / 2
        wx_min = self.cam_x - half_w
        wy_min = self.cam_y - half_h
        gx = wx_min + (mx - PLAY_X) / self.zoom
        gy = wy_min + (my - PLAY_Y) / self.zoom
        base_angle = math.atan2(gy - self.player.y, gx - self.player.x)

        dmg = self.player.damage
        # Dispara 3 projéteis em leque
        total = 4
        spread = 0.08
        for i in range(total):
            offset = (i - (total - 1) / 2) * spread
            angle = base_angle + offset
            self.projectiles.append(
                Projectile(self.player.x, self.player.y, angle,
                           self.player.proj_speed, dmg)
            )
        self.player.attack_timer = self.player.attack_cooldown

    def boss_attack(self):
        boss = self.boss
        if boss.attack_timer > 0:
            return

        bullet_slow = 2.5
        bullet_med = 3.5
        bullet_fast = 4.5

        boss.pattern_timer += 1
        phase = boss.pattern_timer % 480  # ciclo de 8 segundos

        if phase < 80:
            # Espiral tripla horária
            boss.spiral_angle += 0.12
            for arm in range(3):
                base = boss.spiral_angle + arm * (2 * math.pi / 3)
                self.boss_projectiles.append(
                    BossProjectile(boss.x, boss.y, base, bullet_slow, 12)
                )
            boss.attack_timer = 3

        elif phase < 160:
            # Anel completo (24 balas)
            num_ring = 24
            boss.spiral_angle += 0.08
            for i in range(num_ring):
                ang = (2 * math.pi / num_ring) * i + boss.spiral_angle
                self.boss_projectiles.append(
                    BossProjectile(boss.x, boss.y, ang, bullet_med, 12)
                )
            boss.attack_timer = 12

        elif phase < 240:
            # Espiral anti-horária quádrupla rápida
            boss.spiral_angle -= 0.1
            for arm in range(4):
                ang = boss.spiral_angle + arm * (math.pi / 2)
                self.boss_projectiles.append(
                    BossProjectile(boss.x, boss.y, ang, bullet_fast, 15)
                )
            boss.attack_timer = 2

        elif phase < 320:
            # Estrela (5 pontas, 2 camadas de velocidade)
            boss.spiral_angle += 0.07
            for arm in range(5):
                ang = boss.spiral_angle + arm * (2 * math.pi / 5)
                self.boss_projectiles.append(
                    BossProjectile(boss.x, boss.y, ang, bullet_slow, 10)
                )
                self.boss_projectiles.append(
                    BossProjectile(boss.x, boss.y, ang, bullet_fast, 10)
                )
            boss.attack_timer = 5

        elif phase < 400:
            # Cruz giratória (4 feixes grossos)
            boss.spiral_angle += 0.06
            for arm in range(4):
                base = boss.spiral_angle + arm * (math.pi / 2)
                for s in [-0.12, -0.06, 0, 0.06, 0.12]:
                    self.boss_projectiles.append(
                        BossProjectile(boss.x, boss.y, base + s, bullet_med, 12)
                    )
            boss.attack_timer = 3

        else:
            # Chuva caótica 360°
            for _ in range(16):
                ang = random.uniform(0, 2 * math.pi)
                spd = random.uniform(bullet_slow * 0.7, bullet_fast)
                self.boss_projectiles.append(
                    BossProjectile(boss.x, boss.y, ang, spd, 15)
                )
            boss.attack_timer = 4

    def update(self):
        if self.state == GameState.TITLE:
            self.title_anim += 0.03
            return
        if self.state != GameState.PLAYING:
            return

        self.frame += 1
        self.fight_timer += 1
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.boss.update()

        # Câmera segue o jogador (translação da janela)
        lerp = 0.1
        self.cam_x += (self.player.x - self.cam_x) * lerp
        self.cam_y += (self.player.y - self.cam_y) * lerp
        # Limitar câmera para não mostrar fora do mundo
        half_w = (PLAY_W / self.zoom) / 2
        half_h = (PLAY_H / self.zoom) / 2
        self.cam_x = max(half_w, min(PLAY_W - half_w, self.cam_x))
        self.cam_y = max(half_h, min(PLAY_H - half_h, self.cam_y))

        # Player atira automaticamente
        self.auto_attack()

        # Boss atira padrões
        self.boss_attack()

        # Atualiza projéteis do boss
        for bp in self.boss_projectiles:
            bp.update()
            dx = bp.x - self.player.x
            dy = bp.y - self.player.y
            hit_r = 4 if self.player.focused else 8
            if dx * dx + dy * dy < hit_r * hit_r and self.player.invincible <= 0:
                self.player.hp -= bp.damage
                self.player.invincible = 30
                bp.lifetime = 0

        # Colisão entre projéteis do player e do boss
        for p in self.projectiles:
            if p.lifetime <= 0:
                continue
            for bp in self.boss_projectiles:
                if bp.lifetime <= 0:
                    continue
                dx = p.x - bp.x
                dy = p.y - bp.y
                if dx * dx + dy * dy < 10 * 10:
                    p.lifetime = 0
                    bp.lifetime = 0
                    break

        self.boss_projectiles = [bp for bp in self.boss_projectiles if bp.lifetime > 0]

        # Atualiza projéteis do player
        for p in self.projectiles:
            p.update()
            # Acerta o boss
            dx = p.x - self.boss.x
            dy = p.y - self.boss.y
            if dx * dx + dy * dy < 25 * 25:
                self.boss.hp -= p.damage
                p.lifetime = 0

        self.projectiles = [p for p in self.projectiles if p.lifetime > 0]

        # Remover projéteis fora da área
        self.projectiles = [p for p in self.projectiles
                            if -20 < p.x < PLAY_W + 20 and -20 < p.y < PLAY_H + 20]
        self.boss_projectiles = [bp for bp in self.boss_projectiles
                                 if -20 < bp.x < PLAY_W + 20 and -20 < bp.y < PLAY_H + 20]

        # Checar fim de jogo
        if self.player.hp <= 0:
            self.state = GameState.GAME_OVER
        if self.boss.hp <= 0:
            self.state = GameState.VICTORY

    def render(self):
        self.renderer.render(self)
        pygame.display.flip()

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
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                        self.zoom = min(3.0, self.zoom + 0.2)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.zoom = max(0.5, self.zoom - 0.2)

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING

                elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.TITLE

            elif event.type == pygame.MOUSEWHEEL:
                if self.state == GameState.PLAYING:
                    self.zoom = max(0.5, min(3.0, self.zoom + event.y * 0.15))

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
