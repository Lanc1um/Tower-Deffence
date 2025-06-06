import pygame
import json


class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, cellsize):
        super().__init__()
        self.w = cellsize
        self.h = cellsize
        self.pos = pos
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)  # Allow transparency
        self.image.fill((0, 0, 0, 0))  # Fill with transparent color
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.w, self.h), 1)  # Draw border

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]*self.w
        self.rect.y = pos[1]*self.h


class BaseCell(Cell):
    def __init__(self, pos, cellsize):
        super().__init__(pos, cellsize)
        self.hp = 100
        font = pygame.font.Font(None, 36)
        text_surface = font.render(str(self.hp), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.w // 2, self.h // 2))
        self.image.blit(text_surface, text_rect)

    def is_alive(self):
        if self.hp > 0:
            return True
        else:
            return False

    def update(self, damage):
        self.damage(damage)
        self.image.fill(pygame.color.Color("White"))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(str(self.hp), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.w // 2, self.h // 2))
        self.image.blit(text_surface, text_rect)
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.w, self.h), 1)

    def damage(self, damage):
        self.hp -= damage


class RoadCell(Cell):
    def __init__(self, pos, destination, cellsize):
        super().__init__(pos, cellsize)
        self.destination = destination
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.destination, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.w // 2, self.h // 2))
        self.image.blit(text_surface, text_rect)
    def get_dest(self):
        return self.destination


class FieldCell(Cell):
    def __init__(self, pos, cellsize):
        super().__init__(pos, cellsize)
        self.tower = False


class Background(pygame.sprite.Sprite):
    def __init__(self, w, h, color):
        super().__init__()
        self.width = w
        self.height = h
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.path = "Test.json"
        with open(self.path, 'r', encoding='utf-8') as file:
            self.map = json.load(file)
        self.cell_group = pygame.sprite.Group()
        self.road_group = pygame.sprite.Group()
        self.base_group = pygame.sprite.Group()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

        self.cell_group.draw(screen)
        self.road_group.draw(screen)
        self.base_group.draw(screen)

    def choose_level(self, level):
        self.path = f"Content/Levels/{level}"
        with open(self.path, 'r', encoding='utf-8') as file:
            self.map = json.load(file)


    def draw_cells(self):
        x = 0
        y = 0
        i = 0
        map = self.map["layers"][1]["data"]
        for cell in map:
            i += 1
            x += 1
            if x > 35:
                x -= 35
                y += 1
            self.road_group.add(RoadCell((x-1, y-1), str(map[i-1]), self.map["tileheight"]))
            x = 0

    def change_color(self, color):
        self.image.fill(color)

