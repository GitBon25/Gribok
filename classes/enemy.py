import pygame


class Enemy:
    def __init__(self, x, image_path="assets/Snail/walk.png", num_sprites=10, scale=2.5, hit_image_path="assets/Snail/top_hit.png", hit_num_sprites=5, right_boundary=None, collision_tiles=None):
        self.x = x
        self.y = 600
        self.scale = scale
        self.sprites = self.load_sprites(image_path, num_sprites)
        self.hit_sprites = self.load_sprites(
            hit_image_path, hit_num_sprites) if hit_image_path else []
        self.current_sprite = 0
        self.animation_timer = 0
        self.hit = False
        self.hit_timer = 0
        self.hit_sound = pygame.mixer.Sound("assets/Sounds/hit.wav")
        self.hit_sound.set_volume(0.3)
        self.falling = True
        self.fall_speed = 0
        self.gravity = 0.3
        self.right_boundary = right_boundary
        self.is_alive = True
        self.direction = 1
        self.speed = 2
        self.collision_tiles = collision_tiles
        self.hit_awarded = False

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
        if not self.is_alive:
            return

        elif self.hit:
            self.hit_timer += 1
            if self.hit_timer >= 5:
                self.hit_timer = 0
                if self.current_sprite < len(self.hit_sprites) - 1:
                    self.current_sprite = (
                        self.current_sprite + 1) % len(self.hit_sprites)

            self.fall_speed += self.gravity
            self.y += self.fall_speed

            if self.y > 720:
                self.is_alive = False
                return
        elif self.falling:
            self.fall_speed += self.gravity
            self.y += self.fall_speed

            if self.collision_tiles:
                enemy_rect = pygame.Rect(
                    self.x, self.y, self.sprites[0].get_width(), self.sprites[0].get_height())
                for tile_rect in self.collision_tiles:
                    if enemy_rect.colliderect(tile_rect) and self.fall_speed > 0:
                        self.y = tile_rect.top - self.sprites[0].get_height()
                        self.falling = False
                        self.fall_speed = 0
                        break
        else:
            self.animation_timer += 1
            if self.animation_timer >= 10:
                self.animation_timer = 0
                self.current_sprite = (
                    self.current_sprite + 1) % len(self.sprites)

            self.x += self.speed * self.direction

            if self.x <= 0 or self.x + self.sprites[0].get_width() >= self.right_boundary:
                self.direction *= -1

            if self.collision_tiles:
                enemy_rect = pygame.Rect(
                    self.x, self.y, self.sprites[0].get_width(), self.sprites[0].get_height())
                for tile_rect in self.collision_tiles:
                    if enemy_rect.colliderect(tile_rect):
                        self.direction *= -1
                        break

    def draw(self, screen, camera):
        if not self.is_alive:
            return

        if self.hit:
            sprite = self.hit_sprites[self.current_sprite]
            if self.direction == 1:
                sprite = pygame.transform.flip(sprite, True, False)
        elif self.falling:
            sprite = self.sprites[self.current_sprite]
            if self.direction == 1:
                sprite = pygame.transform.flip(sprite, True, False)
        else:
            sprite = self.sprites[self.current_sprite]
            if self.direction == 1:
                sprite = pygame.transform.flip(sprite, True, False)
        screen.blit(sprite, (self.x + camera.camera.x,
                    self.y + camera.camera.y))

    def take_hit(self):
        if not self.hit:
            self.hit = True
            self.current_sprite = 0
            self.falling = True
            self.fall_speed = 0
            if self.hit_sound:
                self.hit_sound.play()
