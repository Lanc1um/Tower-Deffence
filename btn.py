import pygame

class Button(pygame.sprite.Sprite):
    def __init__(
        self, position, size, text, font,
        on_click=lambda: print("Нажато"),
        text_color=pygame.Color("Black"),
        hover_color=pygame.Color("Red")
    ):
        super().__init__()
        self.size = size
        self.text = text
        self.text_color = text_color
        self.hover_color = hover_color
        self.on_click = on_click
        self.font = font
        self.is_clicked = False

        # Прозрачный фон
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect(center=position)


    def clicked(self):
        if not self.is_clicked:
            self.is_clicked = True
            self.on_click()

    def draw(self, screen):
        # Определяем цвет текста в зависимости от наведения
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        current_color = self.hover_color if is_hovered else self.text_color

        # Очистка поверхности (сохраняем прозрачность)
        self.image.fill((0, 0, 0, 0))  # прозрачный фон

        # Отрисовка текста
        text_surface = self.font.render(self.text, True, current_color)
        text_rect = text_surface.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
        self.image.blit(text_surface, text_rect)

        # Отображаем кнопку
        screen.blit(self.image, self.rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.clicked()
        if event.type == pygame.MOUSEBUTTONUP:
            self.is_clicked = False
