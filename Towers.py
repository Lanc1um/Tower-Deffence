import pygame
import math
from Enemy import *
import time

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, image, damage, target=None, speed=20, rotation=0, homing_distance=100):
        super().__init__()
        self.original_image = pygame.image.load(image).convert_alpha()
        self.image = self.original_image  # временно
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.target = target
        self.homing_distance = homing_distance
        self.damage = damage

        angle_rad = math.radians(rotation + 90)
        self.vel = (
            math.sin(angle_rad) * self.speed,
            math.cos(angle_rad) * self.speed
        )

        self.update_rotation()

    def update(self):
        if self.target and self.target.is_alive():
            target_pos = self.target.rect.center
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance <= self.homing_distance and distance != 0:
                dx /= distance
                dy /= distance
                self.vel = (dx * self.speed, dy * self.speed)

            if distance < self.speed:
                self.hit(self.target)
                self.kill()

        # движение
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        # обновляем поворот изображения по текущему вектору движения
        self.update_rotation()

        # если вылетела за экран — уничтожить
        if self.rect.x < 0 or self.rect.x > 800 or self.rect.y < 0 or self.rect.y > 640:
            self.kill()

    def update_rotation(self):
        # Вычисляем угол направления движения
        angle = math.degrees(math.atan2(-self.vel[1], self.vel[0]))  # "-" потому что ось Y направлена вниз в Pygame
        self.image = pygame.transform.rotate(self.original_image, angle)
        # Обновляем rect чтобы центр не смещался
        self.rect = self.image.get_rect(center=self.rect.center)

    def hit(self, target):
        target.hp -= self.damage
        if not target.is_alive() and not target.counted:  # 💥 проверка на "начислено?"
            target.counted = True  # 💥 чтобы второй раз не начислять
            return target.money
        else:
            return 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)



class BaseTower(pygame.sprite.Sprite):
    def __init__(self, position, title, damage, attack_radius, cost, attack_speed, image_path, projectile, cellsize=16, rotation=0):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()  # загружаем оригинал
        self.image = self.original_image  # временно (будет заменена после scale)

        self.cellsize = cellsize
        self.scale_factor = 2  # увеличим башню на 30% по сравнению с размером клетки


        self.pos = position
        self.title = title
        self.damage = damage
        self.projectile = projectile
        self.rect = self.image.get_rect()

        # позиционируем в центре клетки
        self.rect.x = self.pos[0] * self.cellsize * 1.3
        self.rect.y = self.pos[1] * self.cellsize * 1.3

        self.rotation = rotation
        self.reach = attack_radius
        self.enemy_located = False
        self.target = None
        self.last_target = Dummy(position)
        self.bullets = pygame.sprite.Group()
        self.attack_speed = attack_speed
        self.last_shot = 0
        self.cost = cost
        self.resize_image_proportionally()  # пропорциональное масштабирование
        self.rect = self.image.get_rect()
        self.rect.midbottom = (
            int((self.pos[0] + 0.5) * self.cellsize * 1.3),
            int((self.pos[1] + 1) * self.cellsize * 1.3)
        )

    def resize_image_proportionally(self):
        """Пропорционально изменяет размер изображения башни"""
        max_width = int(self.cellsize * self.scale_factor)
        max_height = int(self.cellsize * self.scale_factor)

        orig_width, orig_height = self.original_image.get_size()

        scale_ratio = min(max_width / orig_width, max_height / orig_height)
        new_size = (int(orig_width * scale_ratio), int(orig_height * scale_ratio))

        self.image = pygame.transform.scale(self.original_image, new_size)

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
            self.rotation += 5
        else:
            self.rotation -= 5
        if self.rotation >= 360 or self.rotation <= -360:
            self.rotation = 0

    def update(self):
        if self.enemy_located:
            self.shoot()

    def shoot(self):
        current_time = time.time()
        if current_time - self.last_shot >= self.attack_speed and self.target:
            print(self.projectile)
            bullet = Bullet(
                image=self.projectile,
                pos=self.rect.center,
                target=self.target,
                rotation=self.rotation,
                damage=self.damage,
                homing_distance=50  # дистанция включения самонаведения
            )
            self.bullets.add(bullet)
            self.last_shot = current_time

    def draw(self, screen):
        # Начальная точка линии в центре спрайта
        center_x = self.rect.centerx
        center_y = self.rect.centery

        # Конечная точка линии
        end_x = center_x + self.reach * math.cos(math.radians(self.rotation))
        end_y = center_y - self.reach * math.sin(math.radians(self.rotation))  # Отнимаем, так как Y ось направлена вниз

        # Рисуем линию
        # pygame.draw.line(screen, pygame.color.Color("Green"), (center_x, center_y), (end_x, end_y), 5)

        screen.blit(self.image, (self.rect.x, self.rect.y))
        self.bullets.draw(screen)