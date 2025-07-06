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
from UI import *
from Cards import *
from Slider import *


class Game():
    def __init__(self):
        with open("settings.json", 'r', encoding='utf-8') as file:
            self.settings = json.load(file)
        with open("Content/Textures/Towers/Towers.json", 'r', encoding='utf-8') as file:
            self.towers = json.load(file)
        with open("Content/Textures/Towers/Effects.json", 'r', encoding='utf-8') as file:
            self.effects = json.load(file)
        self.WIN_WIDTH = self.settings["graphics"]["resolution"]["width"]
        self.WIN_HEIGHT = self.settings["graphics"]["resolution"]["height"]
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("Content/Music/flight.wav")
        initial_volume = self.settings["audio"]["musicVolume"]
        self.volume_slider = VolumeSlider(self.WIN_WIDTH//2-150, 200, 300, initial_value=initial_volume)
        if not self.settings["audio"]["mute"]:
            pygame.mixer.music.set_volume(initial_volume)
        else:
            pygame.mixer.music.set_volume(0)
        # Воспроизведение (циклично)
        pygame.mixer.music.play(-1)
        self.title = self.settings["game"]["title"]
        pygame.display.set_caption(self.title)
        self.font = pygame.font.Font("Content/Textures/UI/PressStart2P-Regular.ttf", 24)

        self.BACKGROUND_COLOR = pygame.color.Color("White")
        self.screen = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.bg = Background(self.WIN_WIDTH, self.WIN_HEIGHT, self.BACKGROUND_COLOR)
        self.window = "Start"
        self.fps = self.settings["graphics"]["fps"]
        self.selecting = False
        self.tower_selected = None
        self.button_group = pygame.sprite.Group()
        self.tower_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemies_killed = 0
        self.input_buffer = []
        self.code = [1073741906, 1073741906, 1073741905, 1073741905, 1073741904, 1073741903, 1073741904, 1073741903, 98, 97]
        self.max_length = len(self.code)
        self.secret_flag = False

        self.spawn_interval = 1000  # миллисекунды
        self.running = False
        self.ui = UI((self.WIN_WIDTH, self.WIN_HEIGHT))

        self.can_start_wave = True
        self.wave_started = False
        self.game_finished = False

        self.money = 500

        self.level_path = 'Content/Levels'

        files = os.listdir(self.level_path)
        self.levels = [f for f in files if os.path.isfile(os.path.join(self.level_path, f))]

        self.change_screen("Start")
        self.mainloop()

    def draw_start_menu(self):
        bg_image = pygame.image.load("Content/Textures/UI/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))
        button_text = self.font.render(f"{self.title}", True, pygame.color.Color("Black"))
        self.screen.blit(button_text, (self.WIN_WIDTH//2- button_text.get_width()//2, 100))
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_settings_menu(self):
        bg_image = pygame.image.load("Content/Textures/UI/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))

        button_text = self.font.render("Settings page", True, pygame.color.Color("Black"))
        self.screen.blit(button_text, (self.WIN_WIDTH//2-button_text.get_width()//2, 100))

        # Отрисовка ползунка
        self.volume_slider.draw(self.screen)

        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def show_end_screen(self, screen, result, screen_size=(800, 640)):
        font = pygame.font.Font("Content/Textures/UI/PressStart2P-Regular.ttf", 64)
        small_font = pygame.font.Font("Content/Textures/UI/PressStart2P-Regular.ttf", 24)

        if result == "win":
            text = font.render("Победа!", True, (0, 255, 0))
        else:
            text = font.render("Поражение", True, (255, 0, 0))

        results = small_font.render(f"Врагов убито:{self.enemies_killed}", True, (255, 0, 0))

        prompt = small_font.render("Нажмите любую кнопку чтобы продолжить", True, (255, 255, 255))


        self.screen.fill((0, 0, 0))
        self.screen.blit(text, (screen_size[0] // 2 - text.get_width() // 2, 100))


        self.screen.blit(results, (screen_size[0] // 2 - results.get_width() // 2, 240))

        self.screen.blit(prompt, (screen_size[0] // 2 - prompt.get_width() // 2, screen_size[1] - 80))

    def draw_level_choice_menu(self):
        bg_image = pygame.image.load("Content/Textures/UI/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_game_screen(self, dt=0):
        for tower in self.tower_group.sprites():
            tower.draw(self.screen)
            tower.locate(tower.find_target(self.enemy_group))
            tower.update()
            tower.bullets.update()
            bullet_col = pygame.sprite.groupcollide(tower.bullets, self.enemy_group, True, False)

            if bullet_col:
                for bullet, _ in bullet_col.items():
                    hit_pos = bullet.rect.center  # центр попадания пули
                    for enemy in self.enemy_group:
                        distance = math.hypot(enemy.rect.centerx - hit_pos[0], enemy.rect.centery - hit_pos[1])
                        if distance <= bullet.aoe:
                            if bullet.effect != "":
                                enemy.add_effect(bullet.effect, bullet.effect_time)
                            self.money += bullet.hit(enemy)

                    # (необязательно) нарисовать круг для визуализации зоны поражения
                    pygame.draw.circle(self.screen, (255, 0, 0), hit_pos, bullet.aoe, 2)

        for enemy in self.enemy_group.sprites():
            if enemy.is_alive():
                enemy.draw(self.screen)
            else:
                enemy.kill()
                self.enemies_killed += 1

        collision = pygame.sprite.groupcollide(self.enemy_group, self.bg.road_group, False, False)
        base_col = pygame.sprite.groupcollide(self.enemy_group, self.bg.base_group, True, False)

        if base_col:
            for enemy in base_col:
                self.bg.base_group.update(enemy.damage)
        else:
            self.bg.base_group.update()

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

            enemy.update(dt)
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
        # Сохраняем громкость перед выходом
        self.settings["audio"]["musicVolume"] = self.volume_slider.get_value()
        with open("settings.json", 'w', encoding='utf-8') as file:
            json.dump(self.settings, file, ensure_ascii=False, indent=4)

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
            start_button = Button((self.WIN_WIDTH//2, 200),
                                  (300, 100),
                                  "Начать",
                                  font=self.font,
                                  on_click=functools.partial(self.change_screen, "Levels"))
            setting_button = Button((self.WIN_WIDTH//2, 300),
                                    (300, 100),
                                    "Настройки",
                                    font=self.font,
                                    on_click=functools.partial(self.change_screen, "Settings"))
            quit_button = Button((self.WIN_WIDTH//2, 400),
                                 (300, 100),
                                 "Выйти",
                                 font=self.font,
                                 on_click=self.quit)
            self.button_group.add(start_button, setting_button, quit_button)

        elif target_screen == "Levels":
            c = 0
            for level in self.levels:
                self.button_group.add(Button((self.WIN_WIDTH//2, 50 + 100 * c),
                                             (200, 100),
                                             str(level.split(".")[0]),
                                             font=self.font,
                                             on_click=functools.partial(self.bg.choose_level, f"{level}", self.secret_flag)))
                c += 1
            self.button_group.add(Button((self.WIN_WIDTH//2, 50 + 100 * (len(self.levels))),
                                         (200, 100),
                                         "Начать", font=self.font,

                                         on_click=functools.partial(self.change_screen, "Game")))

        elif target_screen == "Settings":
            quit_button = Button((self.WIN_WIDTH//2, 400),
                                 (200, 100),
                                 "Exit",
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
        dt = clock.tick(self.fps)

        self.selecting_card = False

        last_spawn_time = pygame.time.get_ticks()

        while self.running:
            self.screen.fill(pygame.color.Color("White"))

            current_time = pygame.time.get_ticks()
            if self.window == "Game" and current_time - last_spawn_time > self.spawn_interval and self.wave_started:
                self.bg.spawn_enemies(self.enemy_group)
                last_spawn_time = current_time


            for event in pygame.event.get():
                # print(event)
                if self.window == "Settings":
                    self.volume_slider.handle_event(event)

                if self.window == "Start":
                    if event.type == pygame.KEYDOWN:
                        if event.key == 13:
                            if self.input_buffer == self.code:
                                self.secret_flag = True
                                print(self.secret_flag)
                        else:
                            char = event.key
                            self.input_buffer.append(char)
                            self.input_buffer = self.input_buffer[-self.max_length:]

                if event.type == pygame.QUIT:
                    self.quit()

                if event.type == 768 and event.key == pygame.K_SPACE:
                    if self.window == "Game":
                        if self.can_start_wave:
                            self.wave_started = True
                            self.can_start_wave = False
                            self.bg.update_wave()

                if event.type == 1026 and event.button == 1:
                    if self.window == "Game":
                        clicked_something = False

                        if self.selecting:
                            clicked_card = self.ui.handle_click(event.pos)
                            if clicked_card:
                                if self.tower_selected:
                                    if self.tower_selected.upgrades_left > 0:
                                        if self.money >= clicked_card.cost:
                                            self.money -= clicked_card.cost
                                            if clicked_card.upgrade_field == "damage":
                                                self.tower_selected.damage = clicked_card.damage
                                            if clicked_card.upgrade_field == "attack_speed":
                                                self.tower_selected.attack_speed = clicked_card.attack_speed
                                            if clicked_card.upgrade_field == "attack_radius":
                                                self.tower_selected.reach = clicked_card.attack_radius
                                            self.tower_selected.upgrades_left -= 1
                                            self.selecting = False
                                            self.tower_selected.show_radius = False
                                            if self.tower_selected:
                                                self.tower_selected.show_radius = False
                                            self.tower_selected = None
                                            self.ui.hide_upgrade_cards()
                                else:
                                    self.ui.hide_buy_cards()
                                    self.add_tower(BaseTower(self.place,
                                                             clicked_card.title,
                                                             clicked_card.damage,
                                                             clicked_card.attack_radius,
                                                             clicked_card.cost,
                                                             clicked_card.attack_speed,
                                                             clicked_card.orig_path,
                                                             clicked_card.proj_path,
                                                             clicked_card.effect,
                                                             clicked_card.effect_time))
                                    self.selecting = False
                                    self.place = None

                        else:
                            for cell in self.bg.cell_group.sprites():
                                if cell.rect.collidepoint(event.pos):
                                    clicked_something = True
                                    if cell.tower_base and not cell.tower:
                                        self.place = cell.pos
                                        self.ui.generate_buy_cards(self.towers, self.effects)
                                        self.ui.show_buy_cards()
                                        self.selecting = True
                                        if self.tower_selected:
                                            self.tower_selected.show_radius = False
                                        self.tower_selected = None
                                    elif cell.tower_base and cell.tower:
                                        for tower in self.tower_group.sprites():
                                            if pygame.sprite.collide_rect(cell, tower):
                                                self.tower_selected = tower
                                                self.tower_selected.show_radius = True
                                                self.ui.generate_upgrade_cards(self.tower_selected)
                                                self.ui.show_upgrade_cards()
                                                self.selecting = True
                                    else:
                                        self.selecting = False
                                        if self.tower_selected:
                                            self.tower_selected.show_radius = False
                                        self.tower_selected = None
                                        self.ui.hide_buy_cards()
                                        self.ui.hide_upgrade_cards()

                        if not clicked_something:
                            self.selecting = False
                            if self.tower_selected:
                                self.tower_selected.show_radius = False
                            self.tower_selected = None
                            self.place = None
                            self.ui.hide_buy_cards()
                            self.ui.hide_upgrade_cards()
                    for button in self.button_group.sprites():
                        if button.rect.collidepoint(event.pos):
                            button.clicked()

            self.bg.update()
            self.bg.draw(self.screen)

            if self.window == "Start":
                self.draw_start_menu()
            if self.window == "Settings":
                self.draw_settings_menu()
            if self.window == "Game":
                if self.bg.finished_spawning:
                    if len(self.enemy_group) == 0:
                        if self.bg.wave >= self.bg.map["waves_count"]:
                            self.game_finished = True
                            self.show_end_screen(self.screen, "win", (self.WIN_WIDTH, self.WIN_HEIGHT))
                        else:
                            self.can_start_wave = True
                            self.wave_started = False

                if self.bg.base_group.sprites()[0].hp > 0:
                    if not self.game_finished:
                        self.draw_game_screen(dt)
                else:
                    self.game_finished = True
                    self.show_end_screen("Defeat", (self.WIN_WIDTH, self.WIN_HEIGHT))
            if self.window == "Levels":
                self.draw_level_choice_menu()

            pygame.display.update()
            pygame.display.flip()
            clock.tick(self.fps)


game = Game()