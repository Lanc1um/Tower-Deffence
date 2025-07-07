import pygame
from Cards import *
class UI:
    def __init__(self, screen_size):
        super().__init__()
        self.win_width = screen_size[0]
        self.win_height = screen_size[1]
        self.cards = []
        self.upgrade_cards = []
        self.skill_buttons = []
        self.buy_cards_visible = False
        self.upgrade_cards_visible = False

        # Footer параметры
        self.footer_height = self.win_height // 3.8
        self.footer_rect = pygame.Rect(0, self.win_height - self.footer_height, self.win_width, self.footer_height)

        # Настройки скиллов
        self.skill_data = {
            "Замедление": {"cooldown": 60000, "last_used": -float('inf')},
            "Удар": {"cooldown": 80000, "last_used": -float('inf')},
            "Заморозка": {"cooldown": 100000, "last_used": -float('inf')}
        }
        self.unlocked_skills = 0  # количество доступных скиллов

    def generate_buy_cards(self, towers, effects):
        self.cards = [card for card in self.cards if card.card_type != "buy"]
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
                               tower["damage_radius"],
                                  "buy"))

    def generate_upgrade_cards(self, tower):
        """Создает 3 карты для улучшения башни: урон, радиус, скорость"""
        self.cards = [card for card in self.cards if card.card_type != "upgrade"]  # Удаляем старые upgrade-карты

        base_cost = tower.cost
        upgrades = [
            {
                "title": "Улучшить урон",
                "damage": int(tower.damage * 1.25),
                "attack_radius": tower.reach,
                "attack_speed": tower.attack_speed,
                "cost": int(base_cost * 1),
                "field": "damage"
            },
            {
                "title": "Увеличить радиус",
                "damage": tower.damage,
                "attack_radius": int(tower.reach * 1.25),
                "attack_speed": tower.attack_speed,
                "cost": int(base_cost * 1),
                "field": "attack_radius"
            },
            {
                "title": "Ускорить атаку",
                "damage": tower.damage,
                "attack_radius": tower.reach,
                "attack_speed": max(round(tower.attack_speed * 0.75, 2), 0.1),
                "cost": int(base_cost * 1),
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
                upgrade_field=upgrade["field"],
                base_damage=tower.damage,
                base_range=tower.reach,
                base_speed=tower.attack_speed,
                aoe=tower.aoe
            )
            self.add_card(card)

    def generate_sell_cards(self, tower):
        self.cards = [card for card in self.cards if card.card_type != "sell"]
        card = Card(                width=100,  # временно, UI подгонит размер
                height=140,
                title="Продать башню",
                damage=tower.damage,
                attack_radius=tower.reach,
                cost=tower.cost//2,
                attack_speed=tower.attack_speed,
                image_path=tower.orig_path,
                proj_path=tower.projectile,
                effect=tower.effect,
                effect_time=tower.effect_time,
                card_type="sell",
                aoe=tower.aoe
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
        right_menu_height = self.win_height - self.footer_height
        right_menu_width = self.win_width // 3.8
        right_menu = pygame.Surface((right_menu_width, right_menu_height))
        right_menu.fill((192, 192, 192))
        right_menu_rect = right_menu.get_rect(topright=(self.win_width, 0))
        surface.blit(right_menu, right_menu_rect.topleft)

        font = pygame.font.SysFont(None, 28)
        texts = [f"Волна: {wave}", f"HP: {hp}", f"Деньги: {money}"]

        for idx, text in enumerate(texts):
            text_surf = font.render(text, True, pygame.Color("black"))
            surface.blit(text_surf, (right_menu_rect.x + 10, 20 + idx * 30))

        # Скиллы
        button_width = right_menu_width - 20
        button_height = 40
        button_x = right_menu_rect.x + 10
        start_y = 150

        self.skill_buttons = []
        current_time = pygame.time.get_ticks()

        for i, (title, data) in enumerate(self.skill_data.items()):
            if i >= self.unlocked_skills:
                continue

            button_y = start_y + i * (button_height + 10)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            time_passed = current_time - data["last_used"]
            cooldown_remaining = max(0, (data["cooldown"] - time_passed) // 1000)

            if cooldown_remaining > 0:
                color = (150, 150, 150)
                label = f"{title} ({cooldown_remaining}s)"
            else:
                color = (100, 100, 255)
                label = title

            pygame.draw.rect(surface, color, button_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 0, 0), button_rect, 2, border_radius=8)

            text_surf = font.render(label, True, pygame.Color("white"))
            text_rect = text_surf.get_rect(center=button_rect.center)
            surface.blit(text_surf, text_rect)

            self.skill_buttons.append((title, button_rect))

    def handle_click(self, mouse_pos):
        current_time = pygame.time.get_ticks()

        if self.buy_cards_visible:
            for card in self.cards:
                if card.is_clicked(mouse_pos):
                    return card

        if self.upgrade_cards_visible:
            for card in self.cards:
                if card.is_clicked(mouse_pos):
                    return card

        for title, rect in self.skill_buttons:
            if rect.collidepoint(mouse_pos):
                data = self.skill_data[title]
                if current_time - data["last_used"] >= data["cooldown"]:
                    data["last_used"] = current_time
                    # print(f"Скилл {title} активирован!")
                    return title
                else:
                    pass
                    # print(f"Скилл {title} на кулдауне!")
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

    def draw(self, surface, wave=1, hp=100, money=0):
        self.create_game_menu(surface)
        self.draw_right_menu(surface, wave, hp, money)

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

            index = 0
            for card in self.cards:
                if card.card_type not in ("upgrade", "sell"):
                    continue

                card.rect.x = card_x + index * (card_width + 10)
                card.rect.y = card_y
                card.rect.width = int(card_width)
                card.rect.height = int(card_height)

                card.scale_image()
                card.draw(surface)

                index += 1

