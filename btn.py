import pygame
class Button(pygame.sprite.Sprite):
    def __init__(self, position, size, text, on_click = lambda: print("Нажато"), color=pygame.color.Color("White"), text_color=pygame.color.Color("Black")):
        super().__init__()
        self.size = size
        self.color = color
        self.text = text
        self.text_color = text_color
        self.on_click = on_click
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.font = pygame.font.Font(None, 36)
        self.is_clicked = False

    def clicked(self):
        if not self.is_clicked:
            self.is_clicked = True
            self.on_click()

    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
        self.image.blit(text_surface, text_rect)
        screen.blit(self.image, (self.rect.x, self.rect.y))