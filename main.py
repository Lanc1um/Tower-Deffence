import sys
import pygame
import random
import functools
import os
import json

from map import *
from btn import *
from Towers import *
from Enemy import *



class Card:
    def __init__(self, width, height, title, damage, attack_radius, cost, attack_speed, image_path, proj_path):
        self.rect = pygame.Rect(0, 0, width, height)  # x и y будут заданы в UI
        self.title = title
        self.damage = damage
        self.attack_radius = attack_radius
        self.cost = cost
        self.attack_speed = attack_speed
        self.orig_path = image_path
        self.proj_path = proj_path

        self.original_image = pygame.image.load(image_path).convert_alpha()  # оригинал (для ресайза)
        self.image = self.original_image  # потом масштабируем в UI

        self.CARD_COLOR = (200, 200, 255)
        self.BORDER_COLOR = (50, 50, 200)
        self.font = pygame.font.SysFont(None, 20)
    def is_clicked(self, mouse_pos):
        """Проверяет, кликнули ли по карточке"""
        return self.rect.collidepoint(mouse_pos)
    def scale_image(self):
        """Пропорциональное масштабирование изображения под размеры карточки"""
        max_width = int(self.rect.width * 0.8)
        max_height = int(self.rect.height * 0.5)

        img_width, img_height = self.original_image.get_size()

        scale_ratio = min(max_width / img_width, max_height / img_height)  # выбрать наименьший масштаб
        new_size = (int(img_width * scale_ratio), int(img_height * scale_ratio))

        self.image = pygame.transform.scale(self.original_image, new_size)

    def draw(self, surface):
        # Тело карточки
        pygame.draw.rect(surface, self.CARD_COLOR, self.rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 4)

        # Заголовок
        title_surface = self.font.render(f"{self.title}", True, pygame.Color("black"))
        surface.blit(title_surface, (self.rect.x + 10, self.rect.y + 5))

        # Картинка (после пропорционального масштабирования)
        image_x = self.rect.x + 10
        image_y = self.rect.y + 30
        surface.blit(self.image, (image_x, image_y))

        # Статы
        stats = [
            f"Урон: {self.damage}",
            f"Радиус: {self.attack_radius}",
            f"Цена: {self.cost}",
            f"Скорость: {self.attack_speed}"
        ]

        for i, stat in enumerate(stats):
            stat_surface = self.font.render(stat, True, pygame.Color("black"))
            surface.blit(stat_surface, (self.rect.x + 10, image_y + self.image.get_height() + 5 + i * 20))



class UI():
    def __init__(self, screen_size):
        super().__init__()
        self.win_width = screen_size[0]
        self.win_height = screen_size[1]
        self.cards = []           # список всех карточек
        self.cards_visible = False  # по умолчанию карточки скрыты

        # Footer параметры
        self.footer_height = self.win_height // 5
        self.footer_rect = pygame.Rect(0, self.win_height - self.footer_height, self.win_width, self.footer_height)

    def show_cards(self):
        self.cards_visible = True   # включаем отображение карточек

    def hide_cards(self):
        self.cards_visible = False  # скрываем карточки

    def add_card(self, card):
        self.cards.append(card)     # метод для добавления карточек в UI

    def draw_right_menu(self, surface, wave, hp, money):
        # Правая панель
        right_menu_height = self.win_height - self.footer_height
        right_menu_width = self.win_width // 5
        right_menu = pygame.Surface((right_menu_width, right_menu_height))
        right_menu.fill((183, 105, 0))
        right_menu_rect = right_menu.get_rect(topright=(self.win_width, 0))
        surface.blit(right_menu, right_menu_rect.topleft)

        # Параметры игры
        font = pygame.font.SysFont(None, 28)
        texts = [
            f"Волна: {wave}",
            f"HP: {hp}",
            f"Деньги: {money}"
        ]

        for idx, text in enumerate(texts):
            text_surf = font.render(text, True, pygame.Color("black"))
            surface.blit(text_surf, (right_menu_rect.x + 10, 20 + idx * 30))

    def handle_click(self, mouse_pos):
        if self.cards_visible:
            for card in self.cards:
                if card.is_clicked(mouse_pos):
                    print(f"Нажата карточка: {card.title}")
                    # Здесь можно вызвать какое-то действие или вернуть карточку
                    return card  # например, вернуть нажатую карточку
        return None

    def create_game_menu(self, surface):
        # Нижняя панель (footer)
        footer = pygame.Surface((self.win_width, self.footer_height))
        footer.fill((183, 105, 0))
        surface.blit(footer, self.footer_rect.topleft)

        # Правая панель
        right_menu_height = self.win_height - self.footer_height
        right_menu = pygame.Surface((self.win_width // 5, right_menu_height))
        right_menu.fill((183, 105, 0))
        right_menu_rect = right_menu.get_rect(topright=(self.win_width, 0))
        surface.blit(right_menu, right_menu_rect.topleft)

    def draw(self, surface, wave=1, hp=100, money=0):  # добавлены параметры
        self.create_game_menu(surface)
        self.draw_right_menu(surface, wave, hp, money)  # вызов новой функции

        if self.cards_visible:
            card_width = self.footer_height * 0.8
            card_height = self.footer_height - 20
            card_x = 10
            card_y = self.footer_rect.y + 10

            for index, card in enumerate(self.cards):
                card.rect.x = card_x + index * (card_width + 10)
                card.rect.y = card_y
                card.rect.width = int(card_width)
                card.rect.height = int(card_height)

                card.scale_image()
                card.draw(surface)

class Game():
    def __init__(self):
        with open("settings.json", 'r', encoding='utf-8') as file:
            self.settings = json.load(file)
        with open("Content/Textures/Towers/Towers.json", 'r', encoding='utf-8') as file:
            self.towers = json.load(file)
        self.WIN_WIDTH = self.settings["graphics"]["resolution"]["width"]
        self.WIN_HEIGHT = self.settings["graphics"]["resolution"]["height"]
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("Content/Music/flight.wav")

        # Установка громкости (0.0 до 1.0)
        if not self.settings["audio"]["mute"]:
            pygame.mixer.music.set_volume(self.settings["audio"]["musicVolume"])
        else:
            pygame.mixer.music.set_volume(self.settings["audio"]["musicVolume"])
        # Воспроизведение (циклично)
        pygame.mixer.music.play(-1)
        pygame.display.set_caption(self.settings["game"]["title"])
        self.font = pygame.font.Font("Content/Textures/UI/PressStart2P-Regular.ttf", 24)

        self.BACKGROUND_COLOR = pygame.color.Color("White")
        self.screen = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.bg = Background(self.WIN_WIDTH, self.WIN_HEIGHT, self.BACKGROUND_COLOR)
        self.window = "Start"
        self.fps = self.settings["graphics"]["fps"]
        self.selecting_card = False
        self.button_group = pygame.sprite.Group()
        self.tower_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        self.spawn_interval = 1000  # миллисекунды

        self.running = False

        self.ui = UI((self.WIN_WIDTH, self.WIN_HEIGHT))

        for tower in self.towers["towers"]:
            self.ui.add_card(Card(150, 200,tower["name"], tower["damage"], tower["attack_radius"], tower["cost"], tower["attack_speed"], tower["sprite"], tower["projectile_sprite"]))


        self.money = 5

        self.level_path = 'Content/Levels'

        files = os.listdir(self.level_path)
        self.levels = [f for f in files if os.path.isfile(os.path.join(self.level_path, f))]

        self.change_screen("Start")
        self.mainloop()

    def draw_start_menu(self):
        bg_image = pygame.image.load("Content/Textures/UI/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))
        button_text = self.font.render("Start page", True, pygame.color.Color("Black"))
        self.screen.blit(button_text, (100, 100))
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_settings_menu(self):
        bg_image = pygame.image.load("Content/Textures/UI/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))
        button_text = self.font.render("Settings page", True, pygame.color.Color("Black"))
        self.screen.blit(button_text, (100, 100))
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_level_choice_menu(self):
        bg_image = pygame.image.load("Content/Textures/UI/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))
        for btn in self.button_group.sprites():
            btn.draw(self.screen)


    def draw_game_screen(self):
        for tower in self.tower_group.sprites():
            tower.draw(self.screen)
            tower.locate(tower.find_target(self.enemy_group))
            tower.update()
            tower.bullets.update()
            bullet_col = pygame.sprite.groupcollide(tower.bullets, self.enemy_group, True, False)

            if len(bullet_col) > 0:
                for bullet, enemy_group in bullet_col.items():
                    for enemy in enemy_group:
                        self.money += bullet.hit(enemy)
                        print("321")

        for enemy in self.enemy_group.sprites():
            if enemy.is_alive():
                enemy.draw(self.screen)
            else:
                enemy.kill()

        collision = pygame.sprite.groupcollide(self.enemy_group, self.bg.road_group, False, False)
        base_col = pygame.sprite.groupcollide(self.enemy_group, self.bg.base_group, True, False)

        if len(base_col) > 0:
            for i in range(len(base_col)):
                self.bg.base_group.update(1)
        else:
            self.bg.base_group.update()

        if not self.bg.base_group.sprites()[0].is_alive():
            self.running = False

        for enemy, block_list in collision.items():
            dest = ""
            count = 0
            for block in block_list:
                if isinstance(block, RoadCell):
                    count += 1

            if count == 1:
                dest = block_list[0].get_dest()
            if dest != "":
                enemy.rotate(dest)

            enemy.update()
            enemy.draw(self.screen)

        # Получаем параметры
        wave = self.bg.bases[0].wave if hasattr(self.bg.bases[0], 'wave') else 1
        hp = self.bg.base_group.sprites()[0].hp if len(self.bg.base_group.sprites()) > 0 else 0
        money = self.money

        self.ui.draw(self.screen, wave, hp, money)

    def add_enemy(self, enemy):
        self.enemy_group.add(enemy)

    def add_tower(self, tower):
        if self.money >= tower.cost:
            for cell in self.bg.cell_group.sprites():
                if cell.pos == tower.pos:
                    if not cell.tower:
                        cell.tower = True
                        self.tower_group.add(tower)
                        self.money -= tower.cost

    def quit(self):
        print("QUIT")
        self.running = False

    def change_screen(self, target_screen):
        self.button_group.empty()
        self.tower_group.empty()
        self.enemy_group.empty()
        self.bg.cell_group.empty()
        self.bg.road_group.empty()
        self.bg.base_group.empty()

        self.window = target_screen

        if target_screen == "Start":
            # создаём кнопки стартового меню
            start_button = Button((200, 200),
                                  (300, 100),
                                  "Начать",
                                  font=self.font,
                                  on_click=functools.partial(self.change_screen, "Levels"))
            setting_button = Button((200, 300),
                                    (300, 100),
                                    "Настройки",
                                    font=self.font,
                                    on_click=functools.partial(self.change_screen, "Settings"))
            quit_button = Button((200, 400),
                                 (300, 100),
                                 "Выйти",
                                 font=self.font,
                                 on_click=self.quit)
            self.button_group.add(start_button, setting_button, quit_button)

        elif target_screen == "Levels":
            c = 0
            for level in self.levels:
                self.button_group.add(Button((200, 200 + 100 * c),
                                             (200, 100),
                                             str(level.split(".")[0]),
                                             font=self.font,

                                             on_click=functools.partial(self.bg.choose_level, f"{level}")))
                c += 1
            self.button_group.add(Button((200, 200 + 100 * (len(self.levels))),
                                         (200, 100),
                                         "Start", font=self.font,

                                         on_click=functools.partial(self.change_screen, "Game")))

        elif target_screen == "Settings":
            quit_button = Button((200, 400),
                                 (200, 100),
                                 "Выйти",
                                 font=self.font,
                                 on_click=functools.partial(self.change_screen, "Start"))
            self.button_group.add(quit_button)

        elif target_screen == "Game":
            pygame.mixer.music.fadeout(250)  # Плавное затухание за 1 секунду (1000 мс)
            pygame.mixer.music.load("Content/Music/pressure.mp3")
            pygame.mixer.music.play(-1, fade_ms=1000)  # Плавный старт
            self.bg.draw_cells()

    def mainloop(self):
        self.running = True
        clock = pygame.time.Clock()

        # Состояние выбора карты
        self.selecting_card = False

        # Таймер спавна врагов

        last_spawn_time = pygame.time.get_ticks()

        while self.running:
            self.screen.fill(pygame.color.Color("White"))

            current_time = pygame.time.get_ticks()
            if self.window == "Game" and current_time - last_spawn_time > self.spawn_interval:
                self.bg.spawn_enemies(self.enemy_group)
                last_spawn_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                if event.type == 1026 and event.button == 1:
                    if self.window == "Game":
                        if self.selecting_card:
                            clicked_card = self.ui.handle_click(event.pos)
                            if clicked_card:
                                self.ui.hide_cards()
                                self.add_tower(BaseTower(self.place,
                                                         clicked_card.title,
                                                         clicked_card.damage,
                                                         clicked_card.attack_radius,
                                                         clicked_card.cost,
                                                         clicked_card.attack_speed,
                                                         clicked_card.orig_path,
                                                         clicked_card.proj_path))
                                self.selecting_card = False
                        else:
                            for cell in self.bg.cell_group.sprites():
                                if cell.rect.collidepoint(event.pos):
                                    if cell.tower_base and not cell.tower:
                                        self.place = cell.pos
                                        self.ui.show_cards()
                                        self.selecting_card = True

                    for button in self.button_group.sprites():
                        if button.rect.collidepoint(event.pos):
                            button.clicked()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.ui.show_cards()

            self.bg.update()
            self.bg.draw(self.screen)

            if self.window == "Start":
                self.draw_start_menu()
            if self.window == "Settings":
                self.draw_settings_menu()
            if self.window == "Game":
                self.draw_game_screen()
            if self.window == "Levels":
                self.draw_level_choice_menu()

            pygame.display.update()
            pygame.display.flip()
            clock.tick(self.fps)


game = Game()