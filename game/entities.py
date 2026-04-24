import math
import random
import pygame

from .config import WORLD_W, WORLD_H


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
        self.attack_cooldown = 15
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
        self.kind = kind
        self.is_boss = is_boss
        self.angle = 0.0
        self.anim_timer = random.uniform(0, math.pi * 2)
        self.attack_timer = 0
        self.attack_cooldown = 8 if is_boss else 0
        self.boss_phase = 0
        self.spiral_angle = 0.0
        self.pattern_timer = 0

    def update(self, px, py):
        self.anim_timer += 0.05
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if not self.is_boss:
            if dist > 1:
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed
                self.angle = math.atan2(dy, dx)
        else:
            # Boss fica parado, só gira visualmente
            self.angle += 0.02
        if self.attack_timer > 0:
            self.attack_timer -= 1


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


class BossProjectile:
    def __init__(self, x, y, angle, speed=4.5, damage=12):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.lifetime = 2000
        self.angle = angle
        self.bounces = 0
        self.max_bounces = 3

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # Ricochete nas bordas do mundo
        if self.bounces < self.max_bounces:
            if self.x <= 0 or self.x >= WORLD_W:
                self.vx = -self.vx
                self.x = max(1, min(WORLD_W - 1, self.x))
                self.bounces += 1
                self.angle = math.atan2(self.vy, self.vx)
            if self.y <= 0 or self.y >= WORLD_H:
                self.vy = -self.vy
                self.y = max(1, min(WORLD_H - 1, self.y))
                self.bounces += 1
                self.angle = math.atan2(self.vy, self.vx)
