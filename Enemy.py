import pygame
import math

def get_image(sheet, frame, width, height, scale, color, row=0):
    """Извлекает отдельный спрайт из спрайт листа.

    Args:
        sheet: Объект pygame.Surface, представляющий спрайт-лист.
        frame: Индекс кадра спрайта, который нужно извлечь (начиная с 0).
        width: Ширина одного спрайта в спрайт-листе.
        height: Высота одного спрайта в спрайт-листе.
        scale: Множитель масштабирования спрайта.
        color: Цвет, который нужно сделать прозрачным (обычно цвет фона).
        row: Номер строки в спрайт-листе, из которой нужно извлечь спрайт (начиная с 0).  По умолчанию 0.

    Returns:
        Объект pygame.Surface, представляющий извлеченный и масштабированный спрайт.
    """
    image = pygame.Surface((width, height)).convert_alpha()  # Создаем пустую поверхность
    image.blit(sheet, (0, 0), ((frame * width), (row * height), width, height))  # Копируем часть спрайт листа на поверхность
    image = pygame.transform.scale(image, (width * scale, height * scale))  # Масштабируем изображение
    image.set_colorkey(color)  # Устанавливаем цвет прозрачности (если нужно)
    return image

class Dummy(pygame.sprite.Sprite):
    def __init__(self, position, cellsize = 16, rotation = 0):
        super().__init__()
        self.speed = 5
        self.dest_list = {"right":(0, self.speed, 0),
                          "left":(180, -self.speed, 0),
                          "up":(90, 0, -self.speed),
                          "down":(270, 0, self.speed),
                          }
        self.image = pygame.Surface((cellsize*1, cellsize*1))
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*cellsize
        self.rect.y = position[1]*cellsize
        self.rotation = rotation
        self.velx = 1
        self.vely = 0
        self.hp = 100
        self.money = 5

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

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, position, image, width, height, sprites, money, speed, cellsize = 16, rotation = 0):
        super().__init__()
        if isinstance(image, str):
            self.sprite_sheet = pygame.image.load(image).convert_alpha()
        else:
            self.sprite_sheet = image.convert_alpha()
        self.frame_numbers = []
        self.sprite_width = width
        self.sprite_height = height
        self.counted = False
        sp = sprites
        self.sprites = []
        for i in range(sp):
            self.frame_numbers.append(i)

        for frame in self.frame_numbers:
            sprite = get_image(self.sprite_sheet,
                               frame,
                               self.sprite_width,
                               self.sprite_height,
                               1.4,
                               (0, 0, 0))
            self.sprites.append(sprite)
        self.image = self.sprites[0]

        self.current_frame = 0
        self.animation_speed = 200
        self.last_update = pygame.time.get_ticks()

        self.speed = speed
        self.dest_list = {"right":(0, self.speed, 0),
                          "left":(180, -self.speed, 0),
                          "up":(90, 0, -self.speed),
                          "down":(270, 0, self.speed),
                          }

        self.rect = self.image.get_rect()
        self.rect.x = position[0]*cellsize*1.3
        self.rect.y = position[1]*cellsize*1.3
        self.rotation = rotation
        self.velx = 1
        self.vely = 0
        self.hp = 100
        self.money = money

    def move(self):
        self.rect.x += self.velx
        self.rect.y += self.vely

    def update(self):
        self.move()
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.image = self.sprites[self.current_frame]

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
        # pygame.draw.line(screen, pygame.color.Color("Green"), (center_x, center_y), (end_x, end_y), 5)
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def is_alive(self):
        if self.hp>0:
            return True
        else:
            return False

    def __del__(self):
        pass