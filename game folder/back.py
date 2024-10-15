import pygame
import buttons
import csv

pygame.init()

clock = pygame.time.Clock()
FPS = 60

# Game window settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 630
LOWER_MARGIN = 110
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

# Define game variables
ROWS = 16
MAX_COLS = 150
background_height = SCREEN_HEIGHT - LOWER_MARGIN  # Exclude the lower margin for the background area
VISIBLE_ROWS = background_height // (SCREEN_HEIGHT // ROWS)
TILE_SIZE = background_height // VISIBLE_ROWS  # Ensure the tile size fits the background height properly
TILE_TYPES = 21
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# Load and resize the background image to fit within the game window dimensions
sky_img = pygame.image.load('/Users/asesh/Desktop/game folder/png files/layers/sky.png').convert_alpha()
sky_img = pygame.transform.scale(sky_img, (SCREEN_WIDTH, background_height))

# Store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'png files/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_img = pygame.image.load('png files/save_btn.png').convert_alpha()
load_img = pygame.image.load('png files/load_btn.png').convert_alpha()

# Define colors
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

# Define font
font = pygame.font.SysFont('Futura', 30)

# Create an empty tile list for the level data
world_data = []
for row in range(VISIBLE_ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

# Create ground tiles within the background area
for tile in range(0, MAX_COLS):
    world_data[VISIBLE_ROWS - 1][tile] = 0  # Ensure the ground is within the background bounds

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for drawing the background
def draw_bg():
    screen.fill(GREEN)
    width = sky_img.get_width()
    for x in range(4):
        screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))

# Function for drawing the grid
def draw_grid():
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, background_height))
    for c in range(VISIBLE_ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

# Function for drawing the world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

# Create save and load buttons
save_button = buttons.Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT + LOWER_MARGIN - 40, save_img, 0.5)
load_button = buttons.Button(SCREEN_WIDTH // 2 + 400, SCREEN_HEIGHT + LOWER_MARGIN - 40, load_img, 0.5)

# Create tile selection buttons
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = buttons.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

# Main game loop
run = True
while run:
    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    # Save and load data
    if save_button.draw(screen):
        with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for row in world_data:
                writer.writerow(row)
                
    if load_button.draw(screen):
        scroll = 0  # Reset scroll position
        try:
            with open(f'level{level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
        except FileNotFoundError:
            print(f'Error: level{level}_data.csv file not found.')

    # Draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # Tile selection logic
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    # Highlight the selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    # Scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    # Add new tiles to the screen
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    # Check that the coordinates are within the tile area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
