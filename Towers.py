import pygame
import math
from Enemy import *
import time

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, rotation):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(pygame.color.Color("Black"))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.rotation = rotation
        self.speed = 10
        self.vel = (math.sin(math.radians(rotation + 90))*self.speed, math.cos(math.radians(rotation + 90))*self.speed)
        self.damage = 100

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if self.rect.x < 0 or self.rect.x > 800 or self.rect.y < 0 or self.rect.y > 640:
            self.kill()

    def hit(self, target):
        target.hp -= self.damage

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class BaseTower(pygame.sprite.Sprite):
    def __init__(self, position, rotation = 0):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.color.Color("Red"))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*50
        self.rect.y = position[1]*50
        self.rotation = rotation
        self.reach = 300
        self.enemy_located = False
        self.target = None
        self.last_target = BaseEnemy(position)
        self.bullets = pygame.sprite.Group()
        self.shoot_speed = 1
        self.last_shot = 0

    def locate(self, pos):
        center_x = self.rect.centerx
        center_y = self.rect.centery

        # Конечная точка зелёной линии
        end_x = center_x + self.reach * math.cos(math.radians(self.rotation))
        end_y = center_y - self.reach * math.sin(math.radians(self.rotation))

        # Вектор линии
        line_vec = (end_x - center_x, end_y - center_y)
        line_len = math.hypot(*line_vec)

        # Вектор от начала линии до pos
        point_vec = (pos[0] - center_x, pos[1] - center_y)
        point_len = math.hypot(*point_vec)

        cross = line_vec[0] * point_vec[1] - line_vec[1] * point_vec[0]

        distance_to_line = abs(cross) / line_len

        if distance_to_line > 5:
            self.rotate(pos)
            return False

        dot = line_vec[0] * point_vec[0] + line_vec[1] * point_vec[1]
        if dot < 0 or dot > line_len ** 2:
            self.rotate(pos)
            return False

        return True

    def find_distance(self, point):
        return math.sqrt((self.rect.centerx - point[0])**2 + (self.rect.centery - point[1])**2)

    def find_target(self, enemy_group):
        self.target = None

        for enemy in enemy_group.sprites():
            distance = self.find_distance(enemy.rect.center)
            if distance <= self.reach:
                if self.target != None:
                    if distance < self.find_distance(self.target.rect.center):
                        self.target = enemy
                else:
                    self.target = enemy

        if self.target != None:
            self.enemy_located = True
            self.last_target.rect = self.target.rect.copy()
            return self.target.rect.center

        else:
            self.enemy_located = False
            return self.last_target.rect.center

    def rotate(self, pos):
        center_x = self.rect.centerx
        center_y = self.rect.centery

        # Конечная точка зелёной линии
        end_x = center_x + self.reach * math.cos(math.radians(self.rotation))
        end_y = center_y - self.reach * math.sin(math.radians(self.rotation))

        # Вектор линии
        line_vec = (end_x - center_x, end_y - center_y)
        line_len = math.hypot(*line_vec)

        # Вектор от начала линии до pos
        point_vec = (pos[0] - center_x, pos[1] - center_y)
        point_len = math.hypot(*point_vec)

        cross = line_vec[0] * point_vec[1] - line_vec[1] * point_vec[0]
        if cross < 0:
            self.rotation += 2
        else:
            self.rotation -= 2
        if self.rotation >= 360 or self.rotation <= -360:
            self.rotation = 0

    def update(self):
        if self.enemy_located:
            self.shoot()

    def shoot(self):
        current_time = time.time()  # Получаем текущее время
        if current_time - self.last_shot >= self.shoot_speed:
            self.bullets.add(Bullet(self.rect.center, self.rotation))
            self.last_shot = current_time

    def draw(self, screen):
        # Начальная точка линии в центре спрайта
        center_x = self.rect.centerx
        center_y = self.rect.centery

        # Конечная точка линии
        end_x = center_x + self.reach * math.cos(math.radians(self.rotation))
        end_y = center_y - self.reach * math.sin(math.radians(self.rotation))  # Отнимаем, так как Y ось направлена вниз

        # Рисуем линию
        pygame.draw.line(screen, pygame.color.Color("Green"), (center_x, center_y), (end_x, end_y), 5)

        screen.blit(self.image, (self.rect.x, self.rect.y))
        self.bullets.draw(screen)