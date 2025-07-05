import pygame
from Cards import *
class UI:
    def __init__(self, screen_size):
        super().__init__()
        self.win_width = screen_size[0]
        self.win_height = screen_size[1]
        self.cards = []           # список всех карточек
        self.upgrade_cards = []
        self.buy_cards_visible = False  # по умолчанию карточки скрыты
        self.upgrade_cards_visible = False

        # Footer параметры
        self.footer_height = self.win_height // 3.8
        self.footer_rect = pygame.Rect(0, self.win_height - self.footer_height, self.win_width, self.footer_height)

    def generate_buy_cards(self, towers, effects):
        for tower in towers["towers"]:
            cur_effect = effects["effects"][0]
            for effect in effects["effects"]:
                if effect["name"] == tower["effect"]:
                    cur_effect = effect
                    break
            self.add_card(Card(150,
                                  200,
                                  tower["name"],
                                  tower["damage"],
                                  tower["attack_radius"],
                                  tower["cost"],
                                  tower["attack_speed"],
                                  tower["sprite"],
                                  tower["projectile_sprite"],
                                  tower["effect"],
                                  cur_effect["duration_ms"],
                                  "buy"))

    def generate_upgrade_cards(self, tower):
        """Создает 3 карты для улучшения башни: урон, радиус, скорость"""
        self.cards = [card for card in self.cards if card.card_type != "upgrade"]  # Удаляем старые upgrade-карты

        base_cost = tower.cost
        upgrades = [
            {
                "title": "Улучшить урон",
                "damage": int(tower.damage * 1.5),
                "attack_radius": tower.reach,
                "attack_speed": tower.attack_speed,
                "cost": int(base_cost * 0.5),
                "field": "damage"
            },
            {
                "title": "Увеличить радиус",
                "damage": tower.damage,
                "attack_radius": int(tower.reach * 1.3),
                "attack_speed": tower.attack_speed,
                "cost": int(base_cost * 0.4),
                "field": "attack_radius"
            },
            {
                "title": "Ускорить атаку",
                "damage": tower.damage,
                "attack_radius": tower.reach,
                "attack_speed": max(round(tower.attack_speed * 0.8, 2), 0.1),
                "cost": int(base_cost * 0.6),
                "field": "attack_speed"
            },
        ]

        for upgrade in upgrades:
            card = Card(
                width=100,  # временно, UI подгонит размер
                height=140,
                title=upgrade["title"],
                damage=upgrade["damage"],
                attack_radius=upgrade["attack_radius"],
                cost=upgrade["cost"],
                attack_speed=upgrade["attack_speed"],
                image_path=tower.orig_path,
                proj_path=tower.projectile,
                effect=tower.effect,
                effect_time=tower.effect_time,
                card_type="upgrade",
                upgrade_field=upgrade["field"]
            )
            self.add_card(card)

    def show_buy_cards(self):
        self.buy_cards_visible = True   # включаем отображение карточек

    def hide_buy_cards(self):
        self.buy_cards_visible = False  # скрываем карточки
        self.cards = []

    def show_upgrade_cards(self):
        self.upgrade_cards_visible = True   # включаем отображение карточек

    def hide_upgrade_cards(self):
        self.upgrade_cards_visible = False  # скрываем карточки
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)     # метод для добавления карточек в UI

    def draw_right_menu(self, surface, wave, hp, money):
        # Правая панель
        right_menu_height = self.win_height - self.footer_height
        right_menu_width = self.win_width // 3.8
        right_menu = pygame.Surface((right_menu_width, right_menu_height))
        right_menu.fill((192, 192, 192))
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
        if self.buy_cards_visible:
            for card in self.cards:
                if card.is_clicked(mouse_pos):
                    # print(f"Нажата карточка: {card.title}")
                    # Здесь можно вызвать какое-то действие или вернуть карточку
                    return card  # например, вернуть нажатую карточку

        if self.upgrade_cards_visible:
            for card in self.cards:
                if card.is_clicked(mouse_pos):
                    return card
        return None

    def create_game_menu(self, surface):
        # Нижняя панель (footer)
        footer = pygame.Surface((self.win_width, self.footer_height))
        footer.fill((192, 192, 192))
        surface.blit(footer, self.footer_rect.topleft)

        # Правая панель
        right_menu_height = self.win_height - self.footer_height
        right_menu = pygame.Surface((self.win_width // 5, right_menu_height))
        right_menu.fill((192, 192, 192))
        right_menu_rect = right_menu.get_rect(topright=(self.win_width, 0))
        surface.blit(right_menu, right_menu_rect.topleft)

    def draw(self, surface, wave=1, hp=100, money=0):  # добавлены параметры
        self.create_game_menu(surface)
        self.draw_right_menu(surface, wave, hp, money)  # вызов новой функции

        if self.buy_cards_visible:

            card_width = self.footer_height * 0.8
            card_height = self.footer_height - 20
            card_x = 10
            card_y = self.footer_rect.y + 10

            for index, card in enumerate(self.cards):
                if card.card_type != "buy":
                    continue
                card.rect.x = card_x + index * (card_width + 10)
                card.rect.y = card_y
                card.rect.width = int(card_width)
                card.rect.height = int(card_height)

                card.scale_image()
                card.draw(surface)

        if self.upgrade_cards_visible:
            card_width = self.footer_height * 0.8
            card_height = self.footer_height - 20
            card_x = 10
            card_y = self.footer_rect.y + 10
            upgrade_cards = [card for card in self.cards if card.card_type == "upgrade"]

            for index, card in enumerate(upgrade_cards):
                card.rect.x = card_x + index * (card_width + 10)
                card.rect.y = card_y
                card.rect.width = int(card_width)
                card.rect.height = int(card_height)

                card.scale_image()
                card.draw(surface)