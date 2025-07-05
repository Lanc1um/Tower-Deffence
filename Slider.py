import pygame
class VolumeSlider:
    def __init__(self, x, y, width, initial_value=0.5, label="Громкость"):
        self.rect = pygame.Rect(x, y, width, 10)
        self.handle_radius = 12
        self.value = initial_value  # От 0.0 до 1.0
        self.dragging = False
        self.label = label
        self.font = pygame.font.SysFont("Content/Textures/UI/PressStart2P-Regular.ttf", 24)

    def draw(self, screen):
        # Линия ползунка
        pygame.draw.rect(screen, (180, 180, 180), self.rect)

        # Бегунок
        handle_x = self.rect.x + int(self.value * self.rect.width)
        handle_pos = (handle_x, self.rect.centery)
        pygame.draw.circle(screen, (100, 200, 255), handle_pos, self.handle_radius)

        # Подпись с процентом
        text = self.font.render(f"{self.label}: {int(self.value * 100)}%", True, (0, 0, 0))
        screen.blit(text, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                handle_x = self.rect.x + int(self.value * self.rect.width)
                if self.rect.collidepoint(mx, my) or abs(mx - handle_x) < self.handle_radius:
                    self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx = event.pos[0]
                mx = max(self.rect.x, min(mx, self.rect.x + self.rect.width))
                self.value = (mx - self.rect.x) / self.rect.width
                pygame.mixer.music.set_volume(self.value)  # 💡 динамическое изменение

    def get_value(self):
        return self.value