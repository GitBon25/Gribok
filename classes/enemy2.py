import pygame


class Enemy2:
    def __init__(self, x, y, image_path="assets/BlueBird/flying.png", num_sprites=9, scale=2.5,
                 left_boundary=None, right_boundary=None, hit_image_path="assets/BlueBird/hit.png", hit_sprites=5):
        self.x = x
        self.y = y
        self.is_alive = True
        self.is_defeat = False
        self.scale = scale
        self.sprites = self.load_sprites(image_path, num_sprites)
        self.current_sprite = 0
        self.animation_timer = 0
        self.direction = 1
        self.speed = 2.5
        self.left_boundary = left_boundary
        self.right_boundary = right_boundary
        self.rotation_angle = 0

        self.hit_sprites = self.load_sprites(
            hit_image_path, hit_sprites) if hit_image_path else []
        self.is_hit = False
        self.is_take_hit = False
        self.hit_timer = 0
        self.hit_sprite_index = 0
        self.hit_animation_done = False
        self.falling = False
        self.fall_speed = 0
        self.gravity = 0.3
        self.hit_awarded = False
        self.hit_sound = pygame.mixer.Sound("assets/Sounds/hit.wav")
        self.hit_sound.set_volume(0.3)
        self.rect = pygame.Rect(
            self.x, self.y, self.sprites[0].get_width(), self.sprites[0].get_height())

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
        if self.is_hit or self.is_take_hit:
            self.hit_timer += 1
            if self.hit_timer >= 4:
                self.hit_timer = 0
                self.hit_sprite_index += 1

                if self.hit_sprite_index >= len(self.hit_sprites):
                    self.is_hit = False
                    self.is_take_hit = False
                    self.hit_sprite_index = 0
                    self.hit_animation_done = True
                    self.falling = True
            return

        if self.falling:
            self.fall_speed += self.gravity
            self.y += self.fall_speed

            if self.y > 720:
                self.is_alive = False
            return

        self.x += self.speed * self.direction

        if self.x <= self.left_boundary or self.x + self.sprites[0].get_width() >= self.right_boundary:
            self.direction *= -1

        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen, camera):
        if (self.is_hit or self.is_take_hit) and not self.hit_animation_done:
            sprite = self.hit_sprites[self.hit_sprite_index]
            if self.direction == 1:
                sprite = pygame.transform.flip(sprite, True, False)
        else:
            sprite = self.sprites[self.current_sprite]
            if self.direction == 1:
                sprite = pygame.transform.flip(sprite, True, False)

        sprite = pygame.transform.rotate(sprite, self.rotation_angle)
        screen.blit(sprite, (self.x + camera.camera.x,
                    self.y + camera.camera.y))

    def take_hit(self, player):
        self.is_defeat = True
        if not self.is_take_hit and not self.is_hit:
            if player.rect.bottom > self.rect.top:
                self.is_take_hit = True
                self.hit_timer = 0
                self.hit_sprite_index = 0
                self.hit_animation_done = False
                if self.hit_sound:
                    self.hit_sound.play()

    def hit(self, player):
        if not self.is_hit and not self.is_take_hit and not self.is_defeat:
            if self.direction == 1 and player.rect.left > self.x:
                self.is_hit = True
                self.hit_timer = 0
                self.hit_sprite_index = 0
                self.hit_animation_done = False
                player.defeat()
            elif self.direction == -1 and player.rect.right < self.x + self.sprites[0].get_width():
                self.is_hit = True
                self.hit_timer = 0
                self.hit_sprite_index = 0
                self.hit_animation_done = False
                player.defeat()
