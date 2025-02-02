import pygame
import csv
import os
import sys
from classes.button import Button
from classes.character import Character
from classes.enemy import Enemy
from classes.enemy2 import Enemy2
from classes.coin import Coin


pygame.init()
pygame.mixer.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")
FPS = 60
BG = pygame.image.load("assets/Backgrounds/Background.jpg")
button_sound = pygame.mixer.Sound("assets/Sounds/button.wav")
button_sound.set_volume(0.1)
loose_sound = pygame.mixer.Sound("assets/Sounds/loose.wav")
loose_sound.set_volume(0.3)
win_sound = pygame.mixer.Sound("assets/Sounds/win.wav")
win_sound.set_volume(0.3)
background_music = pygame.mixer.Sound("assets/Sounds/background.wav")
background_music.set_volume(0.02)

count = 0
coins_collected = 0
enemy_hits = 0
current_level = 0
fullscreen = False
disable_music = False

WATER_ANIMATION = pygame.image.load("assets/Tiles/water.png").convert_alpha()
WATER_SPRITES = []
sprite_width = WATER_ANIMATION.get_width() // 5
for i in range(5):
    sprite = WATER_ANIMATION.subsurface(pygame.Rect(
        i * sprite_width, 0, sprite_width, WATER_ANIMATION.get_height()))
    WATER_SPRITES.append(sprite)

TILE_SIZE = 48
TILE_MAPPING = {
    ".": None,
    "1": pygame.image.load("assets/Tiles/grass1.png").convert_alpha(),
    "2": pygame.image.load("assets/Tiles/dirt1.png").convert_alpha(),
    "3": pygame.image.load("assets/Tiles/grass_1.png").convert_alpha(),
    "4": pygame.image.load("assets/Tiles/grass_2.png").convert_alpha(),
    "5": pygame.image.load("assets/Tiles/grass_3.png").convert_alpha(),
    "6": pygame.image.load("assets/Tiles/grass_4.png").convert_alpha(),
    "7": pygame.image.load("assets/Tiles/grass_5.png").convert_alpha(),
    "8": None,
    "9": pygame.image.load("assets/Tiles/grass_6.png").convert_alpha()
}


class MapHandler:
    def __init__(self, map_file):
        self.tiles = []
        self.collision_tiles = []
        self.coins = []
        self.water_tiles = []
        self.water_animation_index = 0
        self.water_animation_timer = 0
        self.load_map(map_file)

    def load_map(self, map_file):
        with open(map_file, 'r') as f:
            for y, line in enumerate(f):
                row = []
                for x, char in enumerate(line.strip()):
                    if char in TILE_MAPPING and TILE_MAPPING[char]:
                        tile_image = TILE_MAPPING[char]
                        tile_image = pygame.transform.scale(
                            tile_image, (TILE_SIZE, TILE_SIZE))
                        tile_rect = pygame.Rect(
                            x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        row.append((tile_image, tile_rect))
                        self.collision_tiles.append(tile_rect)
                    elif char == "*":
                        coin = Coin(x * TILE_SIZE, y * TILE_SIZE)
                        self.coins.append(coin)
                        row.append(None)
                    elif char == "8":
                        water_rect = pygame.Rect(
                            x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        self.water_tiles.append(water_rect)
                        row.append(None)
                    else:
                        row.append(None)
                self.tiles.append(row)

    def draw(self, surface, camera):
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile_image, tile_rect = tile
                    surface.blit(tile_image, camera.apply_rect(tile_rect))

        for water_rect in self.water_tiles:
            water_sprite = WATER_SPRITES[self.water_animation_index]
            water_sprite = pygame.transform.scale(
                water_sprite, (TILE_SIZE, TILE_SIZE))
            surface.blit(water_sprite, camera.apply_rect(water_rect))

        for coin in self.coins:
            coin.draw(surface, camera)

    def update_coins(self):
        for coin in self.coins:
            coin.update()

        self.water_animation_timer += 1
        if self.water_animation_timer >= 7:
            self.water_animation_timer = 0
            self.water_animation_index = (
                self.water_animation_index + 1) % len(WATER_SPRITES)


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


class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.top_left = (0, 0)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)

        x = min(0, x)
        y = min(50, y)
        x = max(-(self.map_width - self.width), x)
        y = max(-(self.map_height - self.height), y)

        if y < -60:
            y = -60
        if x < -5870:
            x = -5870

        self.camera = pygame.Rect(x, y, self.map_width, self.map_height)


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def level1():
    global count, coins_collected, enemy_hits, current_level
    current_level = 1
    count = 0
    coins_collected = 0
    pygame.display.set_caption("Level 1-1")
    clock = pygame.time.Clock()

    map_handler = MapHandler("assets/Maps/map.txt")
    map_width = len(map_handler.tiles[0]) * TILE_SIZE
    map_height = len(map_handler.tiles) * TILE_SIZE
    player = Character(x=100, y=500, right_boundary=map_width)

    enemies = [
        Enemy(x=1200, right_boundary=map_width,
              collision_tiles=map_handler.collision_tiles),
        Enemy(x=4800, right_boundary=map_width,
              collision_tiles=map_handler.collision_tiles)
    ]
    enemies2 = [
        Enemy2(x=5200, y=60, left_boundary=4896, right_boundary=6000),
        Enemy2(x=560, y=96, left_boundary=480, right_boundary=1584)
    ]

    exit_door = ExitDoor(x=6912, y=504)

    camera = Camera(int(1280 * 0.9), int(720 * 0.9), map_width, map_height)

    bg_level = pygame.image.load(
        "assets/Backgrounds/background_level.png").convert_alpha()
    bg_level = pygame.transform.scale(bg_level, (1500, 900))
    bg_width, bg_height = bg_level.get_size()

    bg_offset_x = 0
    bg_offset_y = 0
    parallax_factor = 0.15

    background_music.play(loops=-1)

    show_popup = False
    popup_start_time = 0
    popup_duration = 1000

    running = True
    while running:
        keys = pygame.key.get_pressed()

        player.handle_input(keys)
        player.apply_gravity(map_handler.collision_tiles)
        player.update_animation()

        for enemy in enemies:
            enemy.update()

        for enemy2 in enemies2:
            enemy2.update()

        map_handler.update_coins()

        bg_offset_x = -player.rect.centerx * parallax_factor % bg_width
        bg_offset_y = -player.rect.centery * parallax_factor % bg_height

        SCREEN.blit(bg_level, (bg_offset_x, bg_offset_y))
        SCREEN.blit(bg_level, (bg_offset_x - bg_width, bg_offset_y))
        SCREEN.blit(bg_level, (bg_offset_x, bg_offset_y - bg_height))
        SCREEN.blit(bg_level, (bg_offset_x - bg_width,
                    bg_offset_y - bg_height))

        camera.update(player)

        map_handler.draw(SCREEN, camera)

        exit_door.draw(SCREEN, camera)

        SCREEN.blit(player.image, camera.apply(player))

        for enemy in enemies:
            if enemy.is_alive:
                enemy.draw(SCREEN, camera)

        for enemy2 in enemies2:
            if enemy2.is_alive:
                enemy2.draw(SCREEN, camera)

        player_rect = player.rect
        for enemy in enemies:
            if enemy.is_alive:
                enemy_rect = pygame.Rect(
                    enemy.x, enemy.y, enemy.sprites[0].get_width(), enemy.sprites[0].get_height())
                if player_rect.colliderect(enemy_rect) and player.velocity_y > 0:
                    enemy.take_hit()
                    if not enemy.hit_awarded:
                        count += 300
                        enemy.hit_awarded = True
                        enemy_hits += 1
                        player.velocity_y = -10

        for enemy2 in enemies2:
            enemy2_rect = enemy2.rect
            if not enemy2.is_defeat:
                if player_rect.colliderect(enemy2_rect):
                    enemy2.hit(player)
                if not enemy2.is_hit:
                    if player_rect.colliderect(enemy2_rect) and player.velocity_y > 0:
                        enemy2.take_hit(player)
                        if not enemy2.hit_awarded:
                            count += 300
                            enemy2.hit_awarded = True
                            enemy_hits += 1
                            player.velocity_y = -10

        for water_rect in map_handler.water_tiles:
            if player_rect.colliderect(water_rect) and not player.is_defeated:
                player.defeat()

        if player.rect.y > 720 and player.is_defeated:
            background_music.stop()
            defeat()

        for coin in map_handler.coins:
            if not coin.collected:
                coin_rect = pygame.Rect(
                    coin.x, coin.y, coin.sprites[0].get_width(), coin.sprites[0].get_height())
                if player_rect.colliderect(coin_rect):
                    coin.collect()
                    count += 100
                    coins_collected += 1

        if player_rect.colliderect(exit_door.rect):
            if not show_popup:
                show_popup = True
                popup_start_time = pygame.time.get_ticks()

        if show_popup:
            current_time = pygame.time.get_ticks()
            if current_time - popup_start_time < popup_duration:
                text_surface = get_font(30).render(
                    "Press E to exit", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(640, 680))
                SCREEN.blit(text_surface, text_rect)
            else:
                show_popup = False

        if player_rect.colliderect(exit_door.rect) and keys[pygame.K_e]:
            if not exit_door.is_clicked:
                exit_door.is_clicked = True
                background_music.stop()
                update_game_stats()
                game_over()

        score_text = get_font(30).render(
            f"Score: {count}", True, (253, 254, 255))
        SCREEN.blit(score_text, (20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = save_game_state(
                        player, enemies, enemies2, map_handler.coins, map_handler)
                    options(return_to_level=True)
                    restore_game_state(game_state, player,
                                       enemies, enemies2, map_handler)
                    continue

        pygame.display.update()
        clock.tick(FPS)


def level2():
    global count, coins_collected, enemy_hits, current_level
    current_level = 2
    count = 0
    coins_collected = 0
    pygame.display.set_caption("Level 1-2")
    clock = pygame.time.Clock()

    map_handler = MapHandler("assets/Maps/map2.txt")
    map_width = len(map_handler.tiles[0]) * TILE_SIZE
    map_height = len(map_handler.tiles) * TILE_SIZE
    player = Character(x=100, y=500, right_boundary=map_width)

    enemies2 = [
        Enemy2(x=2000, y=384, left_boundary=1872, right_boundary=2592),
        Enemy2(x=4000, y=144, left_boundary=3744, right_boundary=4512)
    ]

    exit_door = ExitDoor(x=6912, y=504)

    camera = Camera(int(1280 * 0.9), int(720 * 0.9), map_width, map_height)

    bg_level = pygame.image.load(
        "assets/Backgrounds/background_level.png").convert_alpha()
    bg_level = pygame.transform.scale(bg_level, (1500, 900))
    bg_width, bg_height = bg_level.get_size()

    bg_offset_x = 0
    bg_offset_y = 0

    parallax_factor = 0.15

    background_music.play(loops=-1)

    show_popup = False
    popup_start_time = 0
    popup_duration = 1000

    running = True
    while running:
        keys = pygame.key.get_pressed()

        player.handle_input(keys)
        player.apply_gravity(map_handler.collision_tiles)
        player.update_animation()

        for enemy2 in enemies2:
            enemy2.update()

        map_handler.update_coins()

        bg_offset_x = -player.rect.centerx * parallax_factor % bg_width
        bg_offset_y = -player.rect.centery * parallax_factor % bg_height

        SCREEN.blit(bg_level, (bg_offset_x, bg_offset_y))
        SCREEN.blit(bg_level, (bg_offset_x - bg_width, bg_offset_y))
        SCREEN.blit(bg_level, (bg_offset_x, bg_offset_y - bg_height))
        SCREEN.blit(bg_level, (bg_offset_x - bg_width,
                    bg_offset_y - bg_height))

        camera.update(player)

        map_handler.draw(SCREEN, camera)

        exit_door.draw(SCREEN, camera)

        SCREEN.blit(player.image, camera.apply(player))

        for enemy2 in enemies2:
            if enemy2.is_alive:
                enemy2.draw(SCREEN, camera)

        player_rect = player.rect
        for enemy2 in enemies2:
            enemy2_rect = enemy2.rect
            if not enemy2.is_defeat:
                if player_rect.colliderect(enemy2_rect):
                    enemy2.hit(player)
                if not enemy2.is_hit:
                    if player_rect.colliderect(enemy2_rect) and player.velocity_y > 0:
                        enemy2.take_hit(player)
                        if not enemy2.hit_awarded:
                            count += 300
                            enemy2.hit_awarded = True
                            enemy_hits += 1
                            player.velocity_y = -10

        for water_rect in map_handler.water_tiles:
            if player_rect.colliderect(water_rect) and not player.is_defeated:
                player.defeat()

        if player.rect.y > 720 and player.is_defeated:
            background_music.stop()
            defeat()

        for coin in map_handler.coins:
            if not coin.collected:
                coin_rect = pygame.Rect(
                    coin.x, coin.y, coin.sprites[0].get_width(), coin.sprites[0].get_height())
                if player_rect.colliderect(coin_rect):
                    coin.collect()
                    count += 100
                    coins_collected += 1

        if player_rect.colliderect(exit_door.rect):
            if not show_popup:
                show_popup = True
                popup_start_time = pygame.time.get_ticks()

        if show_popup:
            current_time = pygame.time.get_ticks()
            if current_time - popup_start_time < popup_duration:
                text_surface = get_font(30).render(
                    "Press E to exit", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(640, 680))
                SCREEN.blit(text_surface, text_rect)
            else:
                show_popup = False

        if player_rect.colliderect(exit_door.rect) and keys[pygame.K_e]:
            if not exit_door.is_clicked:
                exit_door.is_clicked = True
                background_music.stop()
                update_game_stats()
                game_over()

        score_text = get_font(30).render(
            f"Score: {count}", True, (253, 254, 255))
        SCREEN.blit(score_text, (20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = save_game_state(
                        player, [], enemies2, map_handler.coins, map_handler)
                    options(return_to_level=True)
                    restore_game_state(game_state, player,
                                       [], enemies2, map_handler)
                    continue

        pygame.display.update()
        clock.tick(FPS)


def play():
    while True:
        pygame.display.set_caption("Play")
        mouse_pos = pygame.mouse.get_pos()
        SCREEN.blit(BG, (0, 0))

        play_text = get_font(45).render("Choose level", True, "White")
        play_rect = play_text.get_rect(center=(640, 60))
        SCREEN.blit(play_text, play_rect)

        back_button = Button(image=None, clicked_image=None, pos=(140, 680),
                             text_input="BACK", font=get_font(60), base_color="White", hovering_color="#d1b6a0")

        level1_button = Button(image=pygame.image.load("assets/Buttons/button.png"), clicked_image=None, pos=(320, 360),
                               text_input="Level 1-1", font=get_font(30), base_color="White", hovering_color="#d1b6a0")

        level2_button = Button(image=pygame.image.load("assets/Buttons/button.png"), clicked_image=None, pos=(960, 360),
                               text_input="Level 1-2", font=get_font(30), base_color="White", hovering_color="#d1b6a0")

        for button in [back_button, level1_button, level2_button]:
            button.change_color(mouse_pos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_for_input(mouse_pos):
                    button_sound.play()
                    main_menu()
                elif level1_button.check_for_input(mouse_pos):
                    button_sound.play()
                    level1()
                elif level2_button.check_for_input(mouse_pos):
                    button_sound.play()
                    level2()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()

        pygame.display.update()


def options(return_to_level=None):
    global SCREEN, fullscreen, disable_music
    checkbox_fullscreen = Button(image=pygame.image.load("assets/Buttons/check.png"),
                                 clicked_image=pygame.image.load(
                                     "assets/Buttons/check1.png"),
                                 pos=(640, 260),
                                 text_input=None, font=None, base_color=None, hovering_color=None,
                                 initial_state=fullscreen)
    checkbox_music = Button(image=pygame.image.load("assets/Buttons/check.png"),
                            clicked_image=pygame.image.load(
                                "assets/Buttons/check1.png"),
                            pos=(640, 440),
                            text_input=None, font=None, base_color=None, hovering_color=None,
                            initial_state=disable_music)

    while True:
        pygame.display.set_caption("Options")
        mouse_pos = pygame.mouse.get_pos()
        SCREEN.blit(BG, (0, 0))

        options_text = get_font(80).render("OPTIONS", True, "White")
        options_rect = options_text.get_rect(center=(640, 60))

        fullscreen_text = get_font(45).render("Fullscreen", True, "White")
        fullscreen_rect = fullscreen_text.get_rect(center=(640, 180))

        music_text = get_font(45).render("Disable music", True, "White")
        music_rect = music_text.get_rect(center=(640, 360))

        SCREEN.blit(fullscreen_text, fullscreen_rect)
        SCREEN.blit(options_text, options_rect)
        SCREEN.blit(music_text, music_rect)

        back_button = Button(image=None, clicked_image=None, pos=(420, 600),
                             text_input="BACK", font=get_font(60), base_color="White", hovering_color="#d1b6a0")

        exit_button = Button(image=None, clicked_image=None, pos=(860, 600),
                             text_input="EXIT", font=get_font(60), base_color="White", hovering_color="#A31D1D")

        back_button.change_color(mouse_pos)
        back_button.update(SCREEN)
        exit_button.change_color(mouse_pos)
        exit_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_for_input(mouse_pos):
                    button_sound.play()
                    background_music.stop()
                    main_menu()
                if back_button.check_for_input(mouse_pos):
                    button_sound.play()
                    if not disable_music and not background_music.get_num_channels() and return_to_level:
                        background_music.play(loops=-1)
                    if return_to_level:
                        return
                    else:
                        main_menu()
                if checkbox_fullscreen.check_for_input(mouse_pos):
                    fullscreen = not fullscreen
                    button_sound.play()
                    checkbox_fullscreen.handle_click()
                    if fullscreen:
                        SCREEN = pygame.display.set_mode(
                            (1280, 720), pygame.FULLSCREEN)
                    else:
                        SCREEN = pygame.display.set_mode((1280, 720))
                if checkbox_music.check_for_input(mouse_pos):
                    disable_music = not disable_music
                    button_sound.play()
                    checkbox_music.handle_click()
                    if disable_music:
                        pygame.mixer.set_num_channels(0)
                    else:
                        pygame.mixer.set_num_channels(10)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not disable_music and not background_music.get_num_channels() and return_to_level:
                        background_music.play(loops=-1)
                    if return_to_level:
                        return
                    else:
                        main_menu()

        checkbox_fullscreen.update(SCREEN)
        checkbox_music.update(SCREEN)
        pygame.display.update()


def main_menu():
    while True:
        pygame.display.set_caption("Menu")
        SCREEN.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("GRIBOK", True, "#b68f40")
        menu_rect = menu_text.get_rect(center=(640, 100))

        play_button = Button(image=None, clicked_image=None, pos=(640, 250),
                             text_input="PLAY", font=get_font(75), base_color="#f0e7c6", hovering_color="White")
        options_button = Button(image=None, clicked_image=None, pos=(640, 400),
                                text_input="OPTIONS", font=get_font(75), base_color="#f0e7c6", hovering_color="White")
        quit_button = Button(image=None, clicked_image=None, pos=(640, 550),
                             text_input="QUIT", font=get_font(75), base_color="#f0e7c6", hovering_color="White")

        SCREEN.blit(menu_text, menu_rect)

        for button in [play_button, options_button, quit_button]:
            button.change_color(mouse_pos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(mouse_pos):
                    button_sound.play()
                    play()
                if options_button.check_for_input(mouse_pos):
                    button_sound.play()
                    options()
                if quit_button.check_for_input(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def defeat():
    global current_level
    loose_sound.play()
    while True:
        pygame.display.set_caption("Defeat")

        transparent_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        transparent_surface.fill((0, 0, 0, 12))

        SCREEN.blit(transparent_surface, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("GAME OVER", True, "white")
        menu_rect = menu_text.get_rect(center=(640, 280))

        continue_text = get_font(30).render(
            "Do you want to continue?", True, "white")
        continue_rect = continue_text.get_rect(center=(640, 380))

        yes_button = Button(image=None, clicked_image=None, pos=(520, 450),
                            text_input="Yes", font=get_font(30), base_color="white", hovering_color=(220, 220, 220))
        no_button = Button(image=None, clicked_image=None, pos=(760, 450),
                           text_input="No", font=get_font(30), base_color="white", hovering_color=(220, 220, 220))

        for button in [yes_button, no_button]:
            button.change_color(mouse_pos)
            button.update(SCREEN)

        SCREEN.blit(menu_text, menu_rect)
        SCREEN.blit(continue_text, continue_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.check_for_input(mouse_pos):
                    button_sound.play()
                    if current_level == 1:
                        level1()
                    if current_level == 2:
                        level2()
                if no_button.check_for_input(mouse_pos):
                    button_sound.play()
                    main_menu()

        pygame.display.update()


def game_over():
    global count
    win_sound.play()
    while True:
        pygame.display.set_caption("Game Over")

        transparent_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        transparent_surface.fill((0, 0, 0, 12))

        SCREEN.blit(transparent_surface, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("GAME OVER", True, "white")
        menu_rect = menu_text.get_rect(center=(640, 280))

        continue_text = get_font(30).render(
            f"Your score: {count}", True, "white")
        continue_rect = continue_text.get_rect(center=(640, 380))

        menu_button = Button(image=None, clicked_image=None, pos=(520, 450),
                             text_input="Menu", font=get_font(30), base_color="white", hovering_color=(220, 220, 220))
        exit_button = Button(image=None, clicked_image=None, pos=(760, 450),
                             text_input="Exit", font=get_font(30), base_color="white", hovering_color=(220, 220, 220))

        for button in [menu_button, exit_button]:
            button.change_color(mouse_pos)
            button.update(SCREEN)

        SCREEN.blit(menu_text, menu_rect)
        SCREEN.blit(continue_text, continue_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.check_for_input(mouse_pos):
                    button_sound.play()
                    main_menu()
                if exit_button.check_for_input(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def update_game_stats():
    global count, coins_collected, enemy_hits, current_level

    stats = {
        'Total Score': count,
        'Coins Collected': coins_collected,
        'Enemy Hits': enemy_hits,
        'Level': current_level
    }

    file_exists = os.path.exists('game_stats.csv')

    with open('game_stats.csv', mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=stats.keys())

        if not file_exists:
            writer.writeheader()
        writer.writerow(stats)


def save_game_state(player, enemies, enemies2, coins, map_handler):
    state = {
        "player": (player.rect.x, player.rect.y, player.velocity_y, player.is_defeated),
        "enemies": [(enemy.x, enemy.y, enemy.is_alive) for enemy in enemies],
        "enemies2": [(enemy2.x, enemy2.y, enemy2.is_alive) for enemy2 in enemies2],
        "coins": [(coin.x, coin.y, coin.collected) for coin in map_handler.coins],
    }
    return state


def restore_game_state(state, player, enemies, enemies2, map_handler):
    player.rect.x, player.rect.y, player.velocity_y, player.is_defeated = state["player"]
    for i, enemy in enumerate(enemies):
        enemy.x, enemy.y, enemy.is_alive = state["enemies"][i]
    for i, enemy2 in enumerate(enemies2):
        enemy2.x, enemy2.y, enemy2.is_alive = state["enemies2"][i]
    for i, coin in enumerate(map_handler.coins):
        coin.x, coin.y, coin.collected = state["coins"][i]


main_menu()
