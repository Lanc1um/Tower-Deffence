import pygame

class Cell(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.w = 50
        self.h = 50
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)  # Allow transparency
        self.image.fill((0, 0, 0, 0))  # Fill with transparent color
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.w, self.h), 1)  # Draw border

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

class BaseCell(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class RoadCell(Cell):
    def __init__(self, pos, destination):
        super().__init__(pos)
        self.destination = destination
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.destination, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.w // 2, self.h // 2))
        self.image.blit(text_surface, text_rect)

    def get_dest(self):
        return self.destination

class FieldCell(Cell):
    def __init__(self, pos):
        super().__init__(pos)


class Background(pygame.sprite.Sprite):
    def __init__(self, w, h, color):
        super().__init__()
        self.width = w
        self.height = h
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.map = open("test.txt", "r")
        self.cell_group = pygame.sprite.Group()
        self.road_group = pygame.sprite.Group()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

        self.cell_group.draw(screen)
        self.road_group.draw(screen)

    def draw_cells(self):
        x = 0
        y = 0
        map = self.map.readlines()
        for row in map:
            y += 1
            for cel in row:
                x += 1
                if map[y-1][x-1] == "0":
                    self.cell_group.add(FieldCell((50*x, 50*y)))

                elif map[y-1][x-1] != "\n":
                    self.road_group.add(RoadCell((50*x, 50*y), map[y-1][x-1]))

            x = 0

    def change_color(self, color):
        self.image.fill(color)