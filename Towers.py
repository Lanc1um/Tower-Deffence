import pygame
import math
import numpy

class Bullet(pygame.sprite.Sprite):
    def __init__(self, vel):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(pygame.color.Color("Black"))
        self.rect = self.image.get_rect()
        self.vel = vel

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]


class BaseTower(pygame.sprite.Sprite):
    def __init__(self, position, rotation = 0):
        super().__init__()
        self.pos = position
        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.color.Color("Red"))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.rotation = rotation
        self.reach = 1000

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
            self.rotation += 1
        else:
            self.rotation -= 1
        if self.rotation >= 360 or self.rotation <= -360:
            self.rotation = 0

    def update(self):
        self.pos = (self.rect.x, self.rect.y)

    def shoot(self):
        pass

    def draw(self, screen, target = 0):
        # Начальная точка линии в центре спрайта
        center_x = self.rect.centerx
        center_y = self.rect.centery

        # Конечная точка линии
        end_x = center_x + self.reach * math.cos(math.radians(self.rotation))
        end_y = center_y - self.reach * math.sin(math.radians(self.rotation))  # Отнимаем, так как Y ось направлена вниз

        # Рисуем линию
        pygame.draw.line(screen, pygame.color.Color("Green"), (center_x, center_y), (end_x, end_y), 5)

        screen.blit(self.image, (self.rect.x, self.rect.y))