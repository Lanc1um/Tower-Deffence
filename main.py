import sys
import pygame
import random
import functools
import os

from map import *
from btn import *
from Towers import *
from Enemy import *


class Game():
    def __init__(self):
        self.WIN_WIDTH = 800
        self.WIN_HEIGHT = 640
        self.BACKGROUND_COLOR = pygame.color.Color("White")
        self.screen = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.bg = Background(self.WIN_WIDTH, self.WIN_HEIGHT, self.BACKGROUND_COLOR)
        self.window = "Start"
        self.fps = 30
        self.main_group = pygame.sprite.Group()
        self.button_group = pygame.sprite.Group()
        self.tower_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.running = False

        folder_path = './Levels'

        files = os.listdir(folder_path)
        self.levels = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]

        pygame.init()
        pygame.display.set_caption("hz")
        self.mainloop()

    def draw_start_menu(self):
        font = pygame.font.Font(None, 36)
        button_text = font.render("Start page", True, pygame.color.Color("Black"))
        start_button = Button((200, 200), (200, 100), "Начать", color=pygame.color.Color("Red"), on_click=functools.partial(self.change_screen, "Levels"))
        self.button_group.add(start_button)
        setting_button = Button((200, 300), (200, 100), "Настройки", color=pygame.color.Color("Red"), on_click=functools.partial(self.change_screen, "Settings"))
        self.button_group.add(setting_button)
        quit_button = Button((200, 400), (200, 100), "Выйти", color=pygame.color.Color("Red"), on_click=self.quit)
        self.button_group.add(quit_button)
        self.screen.blit(button_text, (100, 100))
        self.button_group.update()
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_settings_menu(self):
        font = pygame.font.Font(None, 36)
        button_text = font.render("Settings page", True, pygame.color.Color("Black"))
        quit_button = Button((200, 400), (200, 100), "Выйти", color=pygame.color.Color("Red"), on_click=functools.partial(self.change_screen, "Start"))
        self.button_group.add(quit_button)
        self.screen.blit(button_text, (100, 100))
        self.button_group.update()
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_level_choice_menu(self):
        for i in range(len(self.levels)):
            self.button_group.add(Button((200, 200+100*i), (200, 100), str(self.levels[i]), color=pygame.color.Color("Red"), on_click=functools.partial(self.bg.choose_level, f"{self.levels[i]}")))

        self.button_group.add(Button((200, 200+100*(len(self.levels)+1)),
                                      (200, 100),
                                     "Start",
                                     color = pygame.color.Color("Red"),
                                     on_click = functools.partial(self.change_screen, "Game")))
        self.button_group.update()
        for btn in self.button_group.sprites():
            btn.draw(self.screen)

    def draw_game_screen(self):
        self.bg.draw_cells()

        for tower in self.tower_group.sprites():
            tower.draw(self.screen)
            tower.locate(tower.find_target(self.enemy_group))
            tower.update()
            tower.bullets.update()
            bullet_col = pygame.sprite.groupcollide(tower.bullets, self.enemy_group, True, False)

            if len(bullet_col) > 0:
                print(bullet_col)
                for bullet, enemy_group in bullet_col.items():
                    for enemy in enemy_group:
                        bullet.hit(enemy)

        for enemy in self.enemy_group.sprites():
            if enemy.is_alive():
                enemy.draw(self.screen)
            else:
                enemy.kill()

        self.tower_group.update()

        collision = pygame.sprite.groupcollide(self.enemy_group, self.bg.road_group, False, False)

        base_col = pygame.sprite.groupcollide(self.enemy_group, self.bg.base_group, True, False)

        if len(base_col) > 0:
            for i in range(len(base_col)):
                self.bg.base_group.update(1)

        if not self.bg.base_group.sprites()[0].is_alive():
            self.running = False

        for enemy, block_list in collision.items():
            dest = ""
            if len(block_list) == 1:
                dest = block_list[0].get_dest()
            if dest != "":
                enemy.rotate(dest)
            enemy.update()
            enemy.draw(self.screen)

    def add_enemy(self, position, rotation):
        self.enemy_group.add(BaseEnemy((position[0], position[1]), rotation))

    def add_tower(self, position, rotation):
        self.tower_group.add(BaseTower((position[0], position[1]), rotation))

    def quit(self):
        print("QUIT")
        self.running = False

    def change_screen(self, target_screen):
        self.button_group.empty()
        self.tower_group.empty()
        self.enemy_group.empty()

        self.window = target_screen

        if target_screen == "Game":
            self.add_tower((2, 4), 0)
            self.add_enemy((1, 4), 0)

    def mainloop(self):
        self.running = True
        clock = pygame.time.Clock()
        while self.running:
            self.screen.fill(pygame.color.Color("White"))
            for event in pygame.event.get():
                # print(event)
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == 1026 and event.button == 1:
                    for button in self.button_group.sprites():
                        if button.rect.collidepoint(event.pos):
                            button.clicked()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.add_enemy((1, 4), 0)

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