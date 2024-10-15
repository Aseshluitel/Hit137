import pygame
import os
import random

pygame.init()

# Set up screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Create the display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('azzattack')

# Set framerate
clock = pygame.time.Clock()
FPS = 60

# Define game variables
GRAVITY = 0.75
TILE_SIZE = 40
moving_left = False
moving_right = False
shoot = False
grenade_thrown = False

# Load images
bullet_img = pygame.image.load('/Users/asesh/Desktop/game folder/png files/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('/Users/asesh/Desktop/game folder/png files/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('/Users/asesh/Desktop/game folder/png files/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('/Users/asesh/Desktop/game folder/png files/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('/Users/asesh/Desktop/game folder/png files/icons/grenade_box.png').convert_alpha()

item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# Define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Define font
font = pygame.font.SysFont('Futura', 15)

# Function to draw text on the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to draw the background
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))  # Ground line

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.grenades = grenades
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True  # Check if the player is in the air
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0  # Track AI movement distance
        self.idling = False
        self.idling_counter = 0

        # Load all images for the player's animations
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            animation_folder = os.path.join('/Users/asesh/Desktop/game folder/png files', self.char_type, animation)
            num_of_frames = len(os.listdir(animation_folder))
            for i in range(num_of_frames):
                img_path = os.path.join(animation_folder, f'{i}.png')
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def throw_grenade(self):
        if self.grenades > 0:
            grenade = Grenade(self.rect.centerx, self.rect.centery, self.direction)
            grenade_group.add(grenade)
            self.grenades -= 1  # Reduce grenade count

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

    def fire_bullet(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False  # End idling after the counter reaches zero
            else:
                if random.randint(1, 200) == 1:
                    # 1 in 200 chance to idle
                    self.idling = True
                    self.idling_counter = 50  # Idle for 50 frames
                else:
                    # Move the AI soldier in its direction
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right

                    # Move the AI and update action
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run animation
                    self.move_counter += 1

                    # Change direction when moving for a certain distance or hitting screen edge
                    if self.move_counter > TILE_SIZE or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                        self.direction *= -1
                        self.move_counter = 0  # Reset move counter

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Itembox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Check if the player collides with the item box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            # Remove the item box after it's collected
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health  # update with new health
        # Calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        # Remove the bullet if it goes off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Check for collision with enemies only
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 30
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        self.rect.x += dx
        self.rect.y += dy
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 0.5)
            explosion_group.add(explosion)
            # Only apply damage if player is alive and within range
            if player.alive and abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
               abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            # Apply damage to all enemies
            for enemy in enemy_group:
                if enemy.alive and abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                   abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'/Users/asesh/Desktop/game folder/png files/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # Update explosion animation
        EXPLOSION_SPEED = 4
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # If the animation is complete, delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# Create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

# Temp - create item boxes
item_box = Itembox('Health', 100, 260)
item_box_group.add(item_box)
item_box = Itembox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = Itembox('Grenade', 600, 260)
item_box_group.add(item_box)

# Create the player and enemies with ammo and grenades
player = Soldier('player', 200, 200, scale=1.65, speed=2, ammo=20, grenades=5)
health_bar = HealthBar(10, 10, player.health, player.health)
enemy1 = Soldier('enemy', 400, 200, scale=1.65, speed=1, ammo=20, grenades=0)
enemy2 = Soldier('enemy', 300, 200, scale=1.65, speed=1, ammo=20, grenades=0)
enemy_group.add(enemy1)
enemy_group.add(enemy2)

# Game loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()

    # Show health bar, ammo, and grenades
    health_bar.draw(player.health)
    draw_text('AMMO: ', font, RED, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_img, (55 + (x * 15), 25))
    draw_text('GRENADES: ', font, RED, 10, 60)
    for x in range(player.grenades):
        screen.blit(grenade_img, (100+ (x * 15), 60))

    # Update player
    player.update()

    # AI and draw for each enemy
    for enemy in enemy_group:
        enemy.ai()  # Call the AI function to handle enemy movement
        enemy.update()
        enemy.draw(screen)

    # Handle user inputs
    keys = pygame.key.get_pressed()
    moving_left = keys[pygame.K_a]
    moving_right = keys[pygame.K_d]
    shoot = keys[pygame.K_SPACE]

    # Update player movement and actions
    player.move(moving_left, moving_right)

    if shoot and player.shoot_cooldown == 0:
        player.fire_bullet()

    # Draw player
    player.draw(screen)

    # Update and draw all sprite groups
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()

    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)

    # Player's actions
    if player.alive:
        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and not player.in_air:
                player.jump = True
            if event.key == pygame.K_k and not grenade_thrown and player.grenades > 0:
                player.throw_grenade()
                grenade_thrown = True
            if event.key == pygame.K_ESCAPE:
                run = False

    # Handle key releases to reset grenade throw status
    if not pygame.key.get_pressed()[pygame.K_k]:
        grenade_thrown = False  # Reset the grenade throw once key is released

    pygame.display.update()

pygame.quit()
