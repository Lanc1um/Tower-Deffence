import pygame
class UI:
    def __init__(self, screen_size):
        super().__init__()
        self.win_width = screen_size[0]
        self.win_height = screen_size[1]
        self.cards = []           # список всех карточек
        self.cards_visible = False  # по умолчанию карточки скрыты

        # Footer параметры
        self.footer_height = self.win_height // 3.8
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
        if self.cards_visible:
            for card in self.cards:
                if card.is_clicked(mouse_pos):
                    # print(f"Нажата карточка: {card.title}")
                    # Здесь можно вызвать какое-то действие или вернуть карточку
                    return card  # например, вернуть нажатую карточку
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