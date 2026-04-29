import math
import random
import pygame

from .config import PLAY_W, PLAY_H


class Player:
    def __init__(self):
        self.x = PLAY_W / 2
        self.y = PLAY_H * 0.8
        self.speed = 4.0
        self.focus_speed = 1.8  # shift = foco (mais lento, hitbox visível)
        self.hp = 1250
        self.max_hp = 1250
        self.damage = 80
        self.attack_cooldown = 8
        self.attack_timer = 0
        self.proj_speed = 8.0
        self.invincible = 0
        self.angle = -math.pi / 2  # aponta pra cima
        self.focused = False
        self.regen_accum = 0.0
        self.regen_rate = 10.0  # HP por segundo

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

        self.focused = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        spd = self.focus_speed if self.focused else self.speed

        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            self.x += dx * spd
            self.y += dy * spd

        # Limitar à área de jogo
        self.x = max(10, min(PLAY_W - 10, self.x))
        self.y = max(10, min(PLAY_H - 10, self.y))

        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.invincible > 0:
            self.invincible -= 1

        # Regeneração
        self.regen_accum += self.regen_rate / 60.0
        if self.regen_accum >= 1.0:
            heal = int(self.regen_accum)
            self.hp = min(self.hp + heal, self.max_hp)
            self.regen_accum -= heal


class Boss:
    def __init__(self, hp=40000):
        self.x = PLAY_W / 2
        self.y = PLAY_H * 0.15
        self.hp = hp
        self.max_hp = hp
        self.angle = 0.0
        self.anim_timer = 0.0
        self.attack_timer = 0
        self.spiral_angle = 0.0
        self.pattern_timer = 0
        self.regen_accum = 0.0
        self.regen_rate = 5.0  # HP por segundo (baixo comparado a 80k)

    def update(self):
        self.anim_timer += 0.05
        self.angle += 0.02
        if self.attack_timer > 0:
            self.attack_timer -= 1

        # Regen do boss
        self.regen_accum += self.regen_rate / 60.0
        if self.regen_accum >= 1.0:
            heal = int(self.regen_accum)
            self.hp = min(self.hp + heal, self.max_hp)
            self.regen_accum -= heal


class Projectile:
    def __init__(self, x, y, angle, speed, damage):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.lifetime = 120
        self.angle = angle

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1


class BossProjectile:
    def __init__(self, x, y, angle, speed=4.5, damage=15):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.lifetime = 600
        self.angle = angle
        self.bounces = 0
        self.max_bounces = 1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # Ricochete nas bordas da área de jogo
        if self.bounces < self.max_bounces:
            if self.x <= 0 or self.x >= PLAY_W:
                self.vx = -self.vx
                self.x = max(1, min(PLAY_W - 1, self.x))
                self.bounces += 1
                self.angle = math.atan2(self.vy, self.vx)
            if self.y <= 0 or self.y >= PLAY_H:
                self.vy = -self.vy
                self.y = max(1, min(PLAY_H - 1, self.y))
                self.bounces += 1
                self.angle = math.atan2(self.vy, self.vx)

