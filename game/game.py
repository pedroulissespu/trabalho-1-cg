import math
import random
import pygame
import sys

from .config import SCREEN_W, SCREEN_H, WORLD_W, WORLD_H, FPS
from .state import GameState
from .camera import Camera
from .entities import Player, Enemy, Projectile, XPOrb, BossProjectile
from .assets import Assets
from .renderer import Renderer
from .powers import PowerManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Sobreviva ao Semestre!")
        self.clock = pygame.time.Clock()

        Assets.init()
        self.renderer = Renderer(self.screen)

        self.state = GameState.TITLE
        self.player = Player()
        self.camera = Camera()
        self.enemies = []
        self.projectiles = []
        self.xp_orbs = []
        self.spawn_timer = 0
        self.spawn_rate = 60
        self.frame = 0
        self.score = 0
        self.title_anim = 0.0
        self.menu_selection = 0
        self.boss_spawned = False
        self.boss_alive = False
        self.semester_timer = 0
        self.boss_spawn_time = 60 * 90
        self.boss_projectiles = []
        self.powers = PowerManager()
        self.power_choices = []
        self.power_selection = 0
        self.regen_accum = 0.0

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
        self.boss_projectiles = []
        self.powers = PowerManager()
        self.power_choices = []
        self.power_selection = 0
        self.regen_accum = 0.0

    def spawn_enemy(self):
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
        ex = WORLD_W / 2
        ey = WORLD_H / 2

        boss_hp = 50000 + self.player.level * 500
        boss = Enemy(ex, ey, boss_hp, 0, 20, kind=0, is_boss=True)
        # Limpar inimigos normais — só o boss fica
        self.enemies = [e for e in self.enemies if e.is_boss]
        self.enemies.append(boss)
        self.boss_spawned = True
        self.boss_alive = True

    def auto_attack(self):
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
            base_angle = math.atan2(closest.y - self.player.y, closest.x - self.player.x)
            dmg = int(self.player.damage * self.powers.damage_mult())
            self.projectiles.append(
                Projectile(self.player.x, self.player.y, base_angle,
                           self.player.proj_speed, dmg)
            )
            cooldown = max(3, int(self.player.attack_cooldown / self.powers.attack_speed_mult()))
            self.player.attack_timer = cooldown

    def update(self):
        if self.state == GameState.TITLE:
            self.title_anim += 0.03
            return
        if self.state != GameState.PLAYING:
            return

        self.frame += 1
        self.semester_timer += 1
        keys = pygame.key.get_pressed()
        self.player.speed = 3.0 * self.powers.speed_mult()
        self.player.update(keys)
        self.camera.update(self.player.x, self.player.y)

        # Regeneração de HP (Noite de Estudo)
        regen = self.powers.hp_regen_per_sec()
        if regen > 0:
            self.regen_accum += regen / 60.0
            if self.regen_accum >= 1.0:
                heal = int(self.regen_accum)
                self.player.hp = min(self.player.hp + heal, self.player.max_hp)
                self.regen_accum -= heal

        if keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS]:
            self.camera.target_zoom = min(3.0, self.camera.target_zoom + 0.02)
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
            self.camera.target_zoom = max(0.3, self.camera.target_zoom - 0.02)

        # Boss spawn
        if not self.boss_spawned and self.semester_timer >= self.boss_spawn_time:
            self.spawn_boss()

        # Spawn inimigos normais (durante boss: frequência menor)
        self.spawn_timer += 1
        boss_spawn_rate = self.spawn_rate * 3 if self.boss_spawned else self.spawn_rate
        if self.spawn_timer >= boss_spawn_rate:
            self.spawn_timer = 0
            num = 1 if self.boss_spawned else 1 + self.player.level // 3
            for _ in range(num):
                self.spawn_enemy()
            if not self.boss_spawned and self.spawn_rate > 15:
                self.spawn_rate -= 1

        self.auto_attack()

        # Atualiza inimigos
        for e in self.enemies:
            e.update(self.player.x, self.player.y)
            dx = e.x - self.player.x
            dy = e.y - self.player.y
            if dx * dx + dy * dy < 20 * 20 and self.player.invincible <= 0:
                self.player.hp -= e.damage
                self.player.invincible = 30

            # Boss atira projéteis — padrões variados alternando rápido
            if e.is_boss and e.attack_timer <= 0:
                bullet_slow = 2.5
                bullet_med = 3.2
                bullet_fast = 3.8

                e.pattern_timer += 1
                phase = e.pattern_timer % 360

                if phase < 60:
                    # Espiral tripla horária
                    e.spiral_angle += 0.12
                    for arm in range(3):
                        base = e.spiral_angle + arm * (2 * math.pi / 3)
                        self.boss_projectiles.append(
                            BossProjectile(e.x, e.y, base, bullet_slow, 10)
                        )
                    e.attack_timer = 4

                elif phase < 120:
                    # Anel completo (20 balas de uma vez)
                    num_ring = 20
                    e.spiral_angle += 0.1
                    for i in range(num_ring):
                        ang = (2 * math.pi / num_ring) * i + e.spiral_angle
                        self.boss_projectiles.append(
                            BossProjectile(e.x, e.y, ang, bullet_med, 10)
                        )
                    e.attack_timer = 15

                elif phase < 180:
                    # Espiral anti-horária quádrupla
                    e.spiral_angle -= 0.1
                    for arm in range(4):
                        ang = e.spiral_angle + arm * (math.pi / 2)
                        self.boss_projectiles.append(
                            BossProjectile(e.x, e.y, ang, bullet_fast, 12)
                        )
                    e.attack_timer = 3

                elif phase < 240:
                    # Estrela (5 pontas, 2 camadas de velocidade)
                    e.spiral_angle += 0.07
                    for arm in range(5):
                        ang = e.spiral_angle + arm * (2 * math.pi / 5)
                        self.boss_projectiles.append(
                            BossProjectile(e.x, e.y, ang, bullet_slow, 8)
                        )
                        self.boss_projectiles.append(
                            BossProjectile(e.x, e.y, ang, bullet_fast, 8)
                        )
                    e.attack_timer = 6

                elif phase < 300:
                    # Cruz giratória (4 feixes grossos)
                    e.spiral_angle += 0.06
                    for arm in range(4):
                        base = e.spiral_angle + arm * (math.pi / 2)
                        for spread in [-0.1, 0, 0.1]:
                            self.boss_projectiles.append(
                                BossProjectile(e.x, e.y, base + spread, bullet_med, 10)
                            )
                    e.attack_timer = 4

                else:
                    # Chuva caótica 360°
                    for _ in range(12):
                        ang = random.uniform(0, 2 * math.pi)
                        spd = random.uniform(bullet_slow * 0.7, bullet_fast)
                        self.boss_projectiles.append(
                            BossProjectile(e.x, e.y, ang, spd, 12)
                        )
                    e.attack_timer = 6

        # Atualiza projéteis do boss
        for bp in self.boss_projectiles:
            bp.update()
            dx = bp.x - self.player.x
            dy = bp.y - self.player.y
            if dx * dx + dy * dy < 14 * 14 and self.player.invincible <= 0:
                self.player.hp -= bp.damage
                self.player.invincible = 20
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

        # Atualiza projéteis
        for p in self.projectiles:
            p.update()
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
                for _ in range(20):
                    ox = e.x + random.uniform(-30, 30)
                    oy = e.y + random.uniform(-30, 30)
                    self.xp_orbs.append(XPOrb(ox, oy, 5))
            else:
                self.xp_orbs.append(XPOrb(e.x, e.y, 1 + self.player.level // 2))
                self.score += 10

        self.enemies = [e for e in self.enemies if e.hp > 0]
        self.projectiles = [p for p in self.projectiles if p.lifetime > 0]

        # Verificar vitória
        if self.boss_spawned and not self.boss_alive and not any(e.is_boss for e in self.enemies):
            if self.semester_timer > self.boss_spawn_time + 120:
                self.state = GameState.VICTORY

        # Coletar XP
        xp_range = 50 * self.powers.xp_range_mult()
        for orb in self.xp_orbs[:]:
            dx = orb.x - self.player.x
            dy = orb.y - self.player.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < xp_range:
                orb.x -= dx * 0.2
                orb.y -= dy * 0.2
            if dist < 15:
                leveled = self.player.gain_xp(orb.value)
                self.xp_orbs.remove(orb)
                if leveled:
                    choices = self.powers.pick_choices(3)
                    if choices:
                        self.power_choices = choices
                        self.power_selection = 0
                        self.state = GameState.LEVEL_UP

        # Limitar entidades distantes
        self.enemies = [e for e in self.enemies
                        if abs(e.x - self.player.x) < 800 and abs(e.y - self.player.y) < 800]
        self.xp_orbs = [o for o in self.xp_orbs
                        if abs(o.x - self.player.x) < 600 and abs(o.y - self.player.y) < 600]

        if self.player.hp <= 0:
            self.state = GameState.GAME_OVER

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

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.TITLE

                elif self.state == GameState.LEVEL_UP:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.power_selection = (self.power_selection - 1) % len(self.power_choices)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.power_selection = (self.power_selection + 1) % len(self.power_choices)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        chosen = self.power_choices[self.power_selection]
                        self.powers.upgrade(chosen)
                        self.state = GameState.PLAYING

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
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
