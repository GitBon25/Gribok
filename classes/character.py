import pygame


class Character:
    def __init__(self, x, y, speed=6, jump_strength=-18, gravity=1, defeat_gravity=1.5, scale=2.5, left_boundary=0, right_boundary=None):
        self.images = [
            pygame.transform.scale(pygame.image.load(
                "assets/Goomba/goomba1.png").convert_alpha(), (int(32 * scale), int(32 * scale))),
            pygame.transform.scale(pygame.image.load(
                "assets/Goomba/goomba2.png").convert_alpha(), (int(32 * scale), int(32 * scale))),
        ]
        self.idle_image = pygame.transform.scale(pygame.image.load(
            "assets/Goomba/goomba.png").convert_alpha(), (int(32 * scale), int(32 * scale)))
        self.jump_image = pygame.transform.scale(pygame.image.load(
            "assets/Goomba/goomba3.png").convert_alpha(), (int(32 * scale), int(32 * scale)))
        self.image = self.idle_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.jump_strength = jump_strength
        self.gravity = gravity
        self.defeat_gravity = defeat_gravity
        self.velocity_y = 0
        self.animation_index = 0
        self.animation_timer = 0
        self.jumping = False
        self.moving = False
        self.jump_sound = pygame.mixer.Sound("assets/Sounds/jump.wav")
        self.jump_sound.set_volume(0.3)
        self.hurt_sound = pygame.mixer.Sound("assets/Sounds/hurt.wav")
        self.hurt_sound.set_volume(0.3)
        self.left_boundary = left_boundary
        self.right_boundary = right_boundary
        self.is_defeated = False
        self.defeat_timer = 0

    def handle_input(self, keys):
        if self.is_defeated:
            return

        self.moving = False
        if keys[pygame.K_LEFT]:
            if self.rect.x - self.speed >= self.left_boundary:
                self.rect.x -= self.speed
                self.moving = True
        if keys[pygame.K_RIGHT]:
            if self.rect.x + self.speed <= self.right_boundary - self.rect.width:
                self.rect.x += self.speed
                self.moving = True
        if not self.jumping and (keys[pygame.K_SPACE] or keys[pygame.K_UP]):
            self.velocity_y = self.jump_strength
            self.jumping = True
            self.jump_sound.play()

    def apply_gravity(self, collision_tiles):
        if self.is_defeated:
            self.velocity_y += self.defeat_gravity
            self.rect.y += self.velocity_y
            return

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for tile_rect in collision_tiles:
            if (self.rect.colliderect(tile_rect) and
                self.rect.bottom >= tile_rect.top and
                    self.velocity_y > 0):
                self.rect.bottom = tile_rect.top
                self.velocity_y = 0
                self.jumping = False

    def update_animation(self):
        if self.is_defeated:
            self.image = self.jump_image
        elif self.jumping:
            self.image = self.jump_image
        elif self.moving:
            self.animation_timer += 1
            if self.animation_timer >= 10:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % 2
                self.image = self.images[self.animation_index]
        else:
            self.image = self.idle_image

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def defeat(self):
        self.is_defeated = True
        self.velocity_y = -10
        self.hurt_sound.play()
