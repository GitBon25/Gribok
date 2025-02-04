import pygame


class ExitDoor:
    def __init__(self, x, y, image_path="assets/Tiles/door.png", scale=3):
        self.is_clicked = False
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(
            self.image,
            (int(self.image.get_width() * scale),
             int(self.image.get_height() * scale))
        )
        self.rect = pygame.Rect(
            x, y, self.image.get_width(), self.image.get_height())

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_rect(self.rect))