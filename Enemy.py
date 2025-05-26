import pygame
import math

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, position, rotation = 0):
        super().__init__()
        self.pos = position
        self.dest_list = {">":(0, 2, 0),
                          "<":(180, -2, 0),
                          "^":(90, 0, -2),
                          "|":(270, 0, 2),
                          }
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.rotation = rotation
        self.velx = 1
        self.vely = 0
        self.hp = 100

    def move(self):
        self.rect.x += self.velx
        self.rect.y += self.vely
        self.pos = (self.rect.x, self.rect.y)

    def update(self):
        self.move()

    def rotate(self, dest):
        self.rotation = self.dest_list[dest][0]
        self.velx = self.dest_list[dest][1]
        self.vely = self.dest_list[dest][2]

    def collide(self, block):
        if self.rotation == 0:
            collide_coords = self.rect.midleft
        if self.rotation == 90:
            collide_coords = self.rect.midbottom
        if self.rotation == 180:
            collide_coords = self.rect.midleft
        if self.rotation == 270:
            collide_coords = self.rect.midtop

        if block.rect.collidepoint(collide_coords):
            return True
        else:
            return False

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