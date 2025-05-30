import pygame
import math

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, position, rotation = 0):
        super().__init__()
        self.dest_list = {">":(0, 1, 0),
                          "<":(180, -1, 0),
                          "^":(90, 0, -1),
                          "|":(270, 0, 1),
                          }
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*50
        self.rect.y = position[1]*50
        self.rotation = rotation
        self.velx = 1
        self.vely = 0
        self.hp = 100

    def move(self):
        self.rect.x += self.velx
        self.rect.y += self.vely

    def update(self):
        self.move()

    def rotate(self, dest):
        self.rotation = self.dest_list[dest][0]
        self.velx = self.dest_list[dest][1]
        self.vely = self.dest_list[dest][2]

    def draw(self, screen):
        # Начальная точка линии в центре спрайта
        center_x = self.rect.centerx
        center_y = self.rect.centery
        # Конечная точка линии
        end_x = center_x + 300 * math.cos(math.radians(self.rotation))
        end_y = center_y - 300 * math.sin(math.radians(self.rotation))

        # Рисуем линию
        pygame.draw.line(screen, pygame.color.Color("Green"), (center_x, center_y), (end_x, end_y), 5)
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def is_alive(self):
        if self.hp>0:
            return True
        else:
            return False

    def __del__(self):
        pass