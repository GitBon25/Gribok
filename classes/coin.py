import pygame


class Coin:
    def __init__(self, x, y, image_path="assets/Tiles/coin.png", num_sprites=12, scale=3.5):
        self.x = x
        self.y = y
        self.scale = scale
        self.sprites = self.load_sprites(image_path, num_sprites)
        self.current_sprite = 0
        self.animation_timer = 0
        self.animation_speed = 10
        self.collected = False
        self.sound = pygame.mixer.Sound("assets/Sounds/coin.wav")
        self.sound.set_volume(0.5)

    def load_sprites(self, image_path, num_sprites):
        sprite_sheet = pygame.image.load(image_path).convert_alpha()
        sprite_width = sprite_sheet.get_width() // num_sprites
        sprites = []
        for i in range(num_sprites):
            sprite = sprite_sheet.subsurface(pygame.Rect(
                i * sprite_width, 0, sprite_width, sprite_sheet.get_height()))
            sprite = pygame.transform.scale(
                sprite, (sprite.get_width() * self.scale, sprite.get_height() * self.scale))
            sprites.append(sprite)
        return sprites

    def update(self):
        if not self.collected:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_sprite = (
                    self.current_sprite + 1) % len(self.sprites)

    def draw(self, screen, camera):
        if not self.collected:
            sprite = self.sprites[self.current_sprite]
            screen.blit(sprite, (self.x + camera.camera.x,
                        self.y + camera.camera.y))

    def collect(self):
        self.sound.play()
        self.collected = True
