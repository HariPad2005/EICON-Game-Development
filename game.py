import pygame
import random
import time
import controls  # Import gesture controls

# Initialize Pygame
pygame.init()

# Get device screen size and set up display
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Catch the Eggs")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Load images
dragon_img = pygame.image.load("dragon-removebg.png")
egg_img = pygame.image.load("egg.png")
fireball_img = pygame.image.load("fb1.gif")  # Fireball as a static image

# Resize images
dragon_width = int(WIDTH * 0.15)
dragon_height = int(HEIGHT * 0.15)
dragon_img = pygame.transform.scale(dragon_img, (dragon_width, dragon_height))

egg_radius = int(WIDTH * 0.03)
egg_img = pygame.transform.scale(egg_img, (egg_radius * 2, egg_radius * 2))

fireball_width = int(WIDTH * 0.05)
fireball_height = int(HEIGHT * 0.05)
fireball_img = pygame.transform.scale(fireball_img, (fireball_width, fireball_height))

# Game clock and font
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)

# Game variables
cart_x = WIDTH // 2 - dragon_width // 2
cart_y = HEIGHT - 100
ball_speed = 5
fireball_speed = 5
balls = []  # Eggs
fireballs = []  # Fireballs
score = 0
game_time = 120  # 2 minutes = 120 seconds
lives = 3  # Total lives
player_name = ''  # Store player name

# Function to create new egg
def create_egg():
    x = random.randint(0, WIDTH - egg_radius * 2)
    return {"x": x, "y": -egg_radius}

# Function to create new fireball
def create_fireball():
    x = random.randint(0, WIDTH - fireball_width)
    return {"x": x, "y": -fireball_height}

# Function to check if an object is caught by the dragon
def is_object_caught(object_x, object_y, cart_x, cart_y, cart_width, cart_height):
    return cart_x < object_x < cart_x + cart_width and cart_y < object_y < cart_y + cart_height

# Function to ask for player name
def get_player_name():
    global player_name
    screen.fill(WHITE)
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 32, 200, 64)
    name = ''
    active = True
    font = pygame.font.Font(None, 60)
    input_font = pygame.font.Font(None, 48)

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_name = name  # Store the name for use in the game
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

        # Display prompt and input
        screen.fill(WHITE)
        prompt_text = font.render("Enter your name: ", True, BLACK)
        input_text = input_font.render(name, True, BLACK)
        screen.blit(prompt_text, (WIDTH // 2 - 200, HEIGHT // 2 - 100))
        screen.blit(input_text, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, BLACK, input_box, 2)
        pygame.display.flip()
        clock.tick(30)

# Function to increase speed over time
def increase_speed(elapsed_time):
    global ball_speed
    global fireball_speed
    speed_factor = (game_time - elapsed_time) / game_time
    ball_speed = 5 + (5 * (1 - speed_factor))  # Egg speed increases moderately
    fireball_speed = 5 + (8 * (1 - speed_factor))  # Fireball speed increases faster

# Function to reset the game
def reset_game():
    global balls, fireballs, score, cart_x, start_time, lives, ball_speed, fireball_speed
    balls = []
    fireballs = []
    score = 0
    cart_x = WIDTH // 2 - dragon_width // 2
    start_time = time.time()
    lives = 3
    ball_speed = 5
    fireball_speed = 5

# Main game loop
def game_loop():
    global cart_x, score, lives, ball_speed, fireball_speed
    running = True
    start_time = time.time()

    # Ask for player name once, before the game starts
    if not player_name:
        get_player_name()

    while running:
        screen.fill(WHITE)  # Fill the screen with white color

        # Calculate remaining time
        elapsed_time = time.time() - start_time
        remaining_time = game_time - int(elapsed_time)
        if remaining_time <= 0:
            remaining_time = 0
            running = False  # Stop the game when time is up

        # Increase speed as time decreases
        increase_speed(elapsed_time)

        # Get gesture direction and move the dragon
        gesture_direction = controls.get_gesture_direction()  # Get gesture direction from controls.py
        move_speed = 50 + 60 * (1 - remaining_time / game_time)  # Speed based on time remaining
        if gesture_direction == "left" and cart_x > 0:
            cart_x -= move_speed
        if gesture_direction == "right" and cart_x < WIDTH - dragon_width:
            cart_x += move_speed

        # Draw the dragon
        screen.blit(dragon_img, (cart_x, cart_y))

        # Create and update falling eggs
        if random.random() < 0.02:  # Probability of a new egg appearing
            balls.append(create_egg())

        for ball in balls[:]:
            ball["y"] += ball_speed
            screen.blit(egg_img, (ball["x"], ball["y"]))

            # Check if egg is caught by the dragon
            if is_object_caught(ball["x"], ball["y"], cart_x, cart_y, dragon_width, dragon_height):
                score += 1
                balls.remove(ball)
            
            # Remove the egg if it goes off the screen
            elif ball["y"] > HEIGHT:
                balls.remove(ball)

        # Create and update fireballs
        if random.random() < 0.01:  # Probability of a fireball appearing
            fireballs.append(create_fireball())

        for fireball in fireballs[:]:
            fireball["y"] += fireball_speed
            screen.blit(fireball_img, (fireball["x"], fireball["y"]))

            # Check if fireball hits the dragon
            if is_object_caught(fireball["x"], fireball["y"], cart_x, cart_y, dragon_width, dragon_height):
                lives -= 1
                fireballs.remove(fireball)

            # Remove fireball if it goes off the screen
            elif fireball["y"] > HEIGHT:
                fireballs.remove(fireball)

        # End the game if lives run out
        if lives <= 0:
            running = False

        # Display score, timer, and lives
        score_text = font.render(f"Score: {score}", True, BLACK)
        timer_text = font.render(f"Time: {remaining_time}", True, BLACK)
        lives_text = font.render(f"Lives: {lives}", True, BLACK)
        player_text = font.render(f"Player: {player_name}", True, BLUE)
        screen.blit(score_text, (10, 10))
        screen.blit(timer_text, (WIDTH - 150, 10))
        screen.blit(lives_text, (WIDTH // 2 - 50, 10))
        screen.blit(player_text, (10, 50))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                controls.release_camera()  # Release the camera before quitting
                pygame.quit()
                quit()

        pygame.display.flip()
        clock.tick(60)

    return game_over_screen()  # Show game over screen when the game ends

# Game over screen with restart option
def game_over_screen():
    screen.fill(WHITE)
    game_over_text = font.render(f"Game Over! Final Score: {score}", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
    restart_text = font.render("Press R to Restart or Q to Quit", True, BLACK)
    screen.blit(restart_text, (WIDTH // 2 - 200, HEIGHT // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_loop()  # Restart the game loop
                if event.key == pygame.K_q:
                    waiting = False  # Exit waiting loop and quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

# Start the game
if __name__ == "__main__":
    game_loop()
