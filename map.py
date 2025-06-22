import random

import pygame
import json
import sys, os

import pygame
from Enemy import *

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


class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, cellsize, image):
        super().__init__()
        self.w = cellsize
        self.h = cellsize
        self.pos = pos
        self.image = image
        # pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.w, self.h), 1)  # Draw border
        # if not isinstance(self, FieldCell):
        #     self.image = pygame.transform.scale(self.image, (cellsize, cellsize))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]*self.w
        self.rect.y = pos[1]*self.h

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class BaseCell(Cell):
    def __init__(self, pos, cellsize, image = "Content/Textures/Environment/Grass/spr_grass_02.png"):

        self.hp = 100
        # font = pygame.font.Font(None, 16)
        # text_surface = font.render(str(self.hp), True, (0, 0, 0))
        # text_rect = text_surface.get_rect(center=(self.w // 2, self.h // 2))
        # self.image.blit(text_surface, text_rect)
        # Загрузка спрайтлиста (один раз!)
        if isinstance(image, str):
            self.sprite_sheet = pygame.image.load(image).convert_alpha()
        else:
            self.sprite_sheet = image.convert_alpha()


        self.sprite_width = 52
        self.sprite_height = 38
        self.frame_numbers = [0, 1, 2, 3]
        self.sprites = []

        for frame in self.frame_numbers:
            sprite = get_image(self.sprite_sheet, frame, self.sprite_width, self.sprite_height, 1.2,
                               (0, 0, 0))
            self.sprites.append(sprite)
        self.image = self.sprites[0]

        super().__init__(pos, cellsize, self.image)

        self.current_frame = 0
        self.animation_speed = 200
        self.last_update = pygame.time.get_ticks()

    def is_alive(self):
        return self.hp > 0

    def update(self, damage=0):
        self.damage(damage)
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.image = self.sprites[self.current_frame]  # Обновляем image текущим кадром

    def damage(self, damage):
        self.hp -= damage


class Decorations(Cell):
    def __init__(self, pos, cellsize, image = "Content/Textures/Environment/Grass/spr_grass_02.png"):
        if isinstance(image, str):
            self.image = pygame.image.load(image)
        else:
            self.image = image
        super().__init__(pos, cellsize, self.image)


class RoadCell(Cell):
    def __init__(self, pos, index, cellsize, image="Content/Textures/Environment/Grass/spr_grass_02.png",):
        self.index = int(index)

        self.destinations = {
            "6":"right",
            "8":"up",
            "10":"down",
            "12":"left",

            "101":"down",
            "102":"up",
            "103":"down",
            "104":"up",
            "105":"left",
            "106":"right",
            "107":"left",
            "108":"right",
        }

        if isinstance(image, str):
            self.image = pygame.image.load(image)
        else:
            self.image = image

        super().__init__(pos, cellsize, self.image)

        self.destination = self.destinations[str(self.index)]

    def get_dest(self):
        return self.destination

    def draw(self, surface):
        surface.blit(self.image, self.rect)



class Enemy_base(RoadCell):
    def __init__(self, pos, index, cellsize, mob_list, image="Content/Textures/Environment/Grass/spr_grass_02.png"):
        super().__init__(pos, index, cellsize)
        self.mob_list = mob_list.copy()  # Копируем, чтобы избежать изменений извне
        self.finished = False  # Флаг окончания спавна

    def spawn(self, enemy_list):
        if not self.mob_list:
            self.finished = True
            return

        # Выбираем случайного моба из оставшихся
        mob = random.choice(list(self.mob_list.keys()))

        # Создаем врага (ты должен заменить BaseEnemy на свой класс врага)
        enemy = BaseEnemy(self.pos)  # или другой конструктор, если нужен конкретный враг
        enemy.type = mob  # можно сохранить имя типа моба
        enemy_list.add(enemy)  # добавляем врага в группу (pygame.sprite.Group или список)

        # Уменьшаем счетчик мобов
        self.mob_list[mob] -= 1
        if self.mob_list[mob] <= 0:
            del self.mob_list[mob]  # удаляем моба, если кончились

        # Если больше мобов нет, флаг окончания
        if not self.mob_list:
            self.finished = True


class FieldCell(Cell):
    def __init__(self, pos, cellsize, image = "Content/Textures/Environment/Grass/spr_grass_02.png", tower_base = False):
        if isinstance(image, str):
            self.image = pygame.image.load(image)
        else:
            self.image = image
        super().__init__(pos, cellsize, self.image)
        self.tower = False
        self.tower_base = tower_base

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
        self.decoration_group = pygame.sprite.Group()
        self.base = ""

        self.images = {}

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

        self.cell_group.draw(screen)
        self.road_group.draw(screen)
        self.base_group.draw(screen)
        self.decoration_group.draw(screen)

    def choose_level(self, level):
        self.path = f"Content/Levels/{level}"
        with open(self.path, 'r', encoding='utf-8') as file:
            self.map = json.load(file)
            self.get_images()

    def get_images(self):
        for cell in self.map["tilesets"]:
            self.images[str(cell["firstgid"])] = cell["source"]

    def draw_cells(self):
        x = 0
        y = 0
        base = ()
        map_bg = self.map["layers"][0]["data"]
        map = self.map["layers"][1]["data"]
        for cell in map_bg:
            x += 1
            if x > 35:
                x -= 35
                y += 1
            if cell == 100:
                base = (x, y)
            if cell == 27:
                tower = True
            else:
                tower= False
            self.cell_group.add(FieldCell((x-1, y), self.map["tileheight"]*1.3, self.images[str(cell)], tower_base=tower))
        x = 0
        y = 0
        for cell in map:
            x += 1
            if x > 35:
                x -= 35
                y += 1
            if str(cell) in self.images.keys():
                if cell == 14:
                    self.base_group.add(BaseCell((x-1, y), self.map["tileheight"]*1.3, self.images[str(cell)]))
                else:
                    image = pygame.image.load(self.images[str(cell)])
                    image_scaled = pygame.transform.scale(image, (self.map["tileheight"]*1.4, self.map["tileheight"]*1.4))
                    if "Decoration" in self.images[str(cell)].split("/"):
                        self.decoration_group.add(Decorations((x-1, y), self.map["tileheight"]*1.3, image_scaled))
                    if "Grass" in self.images[str(cell)].split("/"):
                        self.cell_group.add(FieldCell((x-1, y), self.map["tileheight"]*1.3, image_scaled))
                    if "Roads" in self.images[str(cell)].split("/"):
                        self.road_group.add(RoadCell((x-1, y), str(cell), self.map["tileheight"]*1.3, image=image_scaled))


