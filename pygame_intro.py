import pygame
from sys import exit
from random import randint, choice

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
GROUND_HEIGHT = 300


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load(
            "graphics/Player/player_walk_1.png"
        ).convert_alpha()
        player_walk_2 = pygame.image.load(
            "graphics/Player/player_walk_2.png"
        ).convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load("graphics/Player/jump.png").convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound("audio/jump.mp3")
        self.jump_sound.set_volume(0.2)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= GROUND_HEIGHT:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= GROUND_HEIGHT:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < GROUND_HEIGHT:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == "fly":
            fly_frame_1 = pygame.image.load("graphics/Fly/Fly1.png").convert_alpha()
            fly_frame_2 = pygame.image.load("graphics/Fly/Fly2.png").convert_alpha()
            self.frames = [fly_frame_1, fly_frame_2]
            y_pos = 210
        else:
            snail_frame_1 = pygame.image.load(
                "graphics/snail/snail1.png"
            ).convert_alpha()
            snail_frame_2 = pygame.image.load(
                "graphics/snail/snail2.png"
            ).convert_alpha()
            self.frames = [snail_frame_1, snail_frame_2]
            y_pos = GROUND_HEIGHT

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()


def display_score():
    current_time = (pygame.time.get_ticks() - start_time) // 100
    score_surface = score_font.render(f"{current_time}", False, (64, 64, 64))
    score_rect = score_surface.get_rect(center=(WINDOW_WIDTH / 2, 50))
    screen.blit(score_surface, score_rect)
    return current_time


def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    return True


# Initialisation
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pixel Runner")
clock = pygame.time.Clock()
score_font = pygame.font.Font("font/Pixeltype.ttf", 50)
game_active = False
start_time = 0
score = 0
bg_music = pygame.mixer.Sound("audio/music.wav")
bg_music.set_volume(0.2)
bg_music.play(loops=-1)

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

# Sky and ground background surfaces
sky_surface = pygame.image.load("graphics/Sky.png").convert()
ground_surface = pygame.image.load("graphics/ground.png").convert()

# Intro screen
player_stand = pygame.image.load("graphics/Player/player_stand.png").convert_alpha()
player_stand = pygame.transform.scale2x(player_stand)
player_stand_rect = player_stand.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

game_name = score_font.render("Pixel Runner", False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(WINDOW_WIDTH / 2, 70))

game_message = score_font.render("Press space to play", False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(WINDOW_WIDTH / 2, 340))

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # while game is active, create obstacles
        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(["fly", "snail", "snail", "snail"])))

        # if game is not active and space bar is pressed
        # begin game and update start time
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = pygame.time.get_ticks()

    if game_active:
        # Render backgrounds and score
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, GROUND_HEIGHT))
        score = display_score()

        # Render player
        player.draw(screen)
        player.update()

        # Render obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()

        # Alter active game state if collision
        game_active = collision_sprite()

    else:
        # Game is over or has just been started

        # Intro screen
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)

        # Score message
        score_message = score_font.render(f"Score: {score}", False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(WINDOW_WIDTH / 2, 330))

        # Render game name
        screen.blit(game_name, game_name_rect)

        # If new game, don't display score
        # Else, display score
        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            screen.blit(score_message, score_message_rect)

    pygame.display.update()  # update display
    clock.tick(60)  # cap fps at 60
