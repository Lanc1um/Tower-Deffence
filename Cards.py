import pygame
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