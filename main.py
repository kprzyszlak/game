import pygame
import pygame_menu
import random
import json
import os
import time

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Initialize joystick(s)
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    print(f"Joystick {joystick.get_name()} connected")

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# Fireball setup
fire_ball_event = pygame.USEREVENT
pygame.time.set_timer(fire_ball_event, 200)

fireball = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(fireball, "yellow", (10, 10), 10)
pygame.draw.circle(fireball, "orange", (10, 13), 7)
pygame.draw.circle(fireball, "red", (10, 16), 4)
fireballs = []

# Bullet setup
bullet = pygame.Surface((15, 20))
bullet.fill("white")
bullets = []

# Player class
class Player:
    def __init__(self, x, y, speed, lives, ammo):
        self.pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        self.speed = speed
        self.lives = lives
        self.ammo = ammo
        self.last_shot_time = 0  # in milliseconds
        
    def shoot(self, current_time):
        current_time_ms = pygame.time.get_ticks()  # Get current time in milliseconds
        if self.ammo > 0 and (current_time_ms - self.last_shot_time) >= 100:  # 100 ms delay between shots
            self.ammo -= 1  # Decrease ammo when shooting
            self.last_shot_time = current_time_ms  # Update last shot time
            return pygame.Rect(self.pos.x - 5, self.pos.y - 30, 10, 20)  # Return the bullet's rect
        return None
# Other global variables
score = 0
difficulty = 1  # Default difficulty
score_by_bullet = 0
highscores = []  # High scores list
total_score = 0
total_time = 0

# High scores file
HIGHSCORES_FILE = "highscores.json"

# Load highscores
def load_highscores():
    global highscores
    if os.path.exists(HIGHSCORES_FILE):
        try:
            with open(HIGHSCORES_FILE, "r") as file:
                highscores = json.load(file)
        except json.JSONDecodeError:
            highscores = []  # If there's an issue with the file, reset the highscores
    else:
        highscores = []  # If the file doesn't exist, start fresh

# Save highscores
def save_highscores():
    with open(HIGHSCORES_FILE, "w") as file:
        json.dump(highscores, file)

# Update highscores
def update_highscores(name, score):
    global highscores
    highscores.append({"name": name, "score": score})
    highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:5]  # Keep top 5 scores
    save_highscores()

# Function to set difficulty
def set_difficulty(_, value):
    global difficulty  # Use the global difficulty variable
    difficulty = value

# High score screen
def show_highscores():
    global running
    showing_scores = True

    while showing_scores:
        screen.fill("black")
        font = pygame.font.Font(None, 75)
        title_text = font.render("High Scores", True, (255, 255, 255))
        screen.blit(title_text, (screen.get_width() / 2 - title_text.get_width() / 2, 50))

        font = pygame.font.Font(None, 50)
        for i, entry in enumerate(highscores):
            entry_text = font.render(f"{i + 1}. {entry['name']}: {entry['score']}", True, (255, 255, 255))
            screen.blit(entry_text, (screen.get_width() / 2 - entry_text.get_width() / 2, 150 + i * 50))

        # Options
        font = pygame.font.Font(None, 35)
        menu_text = font.render("Press M to return to menu or Q to quit", True, (200, 200, 200))
        screen.blit(menu_text, (screen.get_width() / 2 - menu_text.get_width() / 2, screen.get_height() - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showing_scores = False
                running = False
                total_score = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # Return to menu
                    showing_scores = False
                    running = False
                    running = True
                    total_score = 0
                elif event.key == pygame.K_q:  # Quit game
                    showing_scores = False
                    running = False
                    total_score = 0
            elif event.type == pygame.JOYBUTTONDOWN:  # Joystick button events
                if event.button == 1:  # Return to menu
                    showing_scores = False
                    running = False
                    running = True
                    total_score = 0
                elif event.button == 9:  # Quit game
                    showing_scores = False
                    running = False
                    total_score = 0

# Start game function
def start_the_game():
    global running, score, ammo, score_by_bullet, difficulty, total_score, total_time
    player = Player(screen.get_width() / 2, screen.get_height() / 2, 400, 3, 5)  # Create player object
    
    # Reset game state
    fireballs.clear()
    bullets.clear()
    total_time = 0
    time_counter = 0
    score = 0  # Reset score at the start of a new game
    score_by_bullet = 0  # Reset bullet-related score
    total_score = 0  # Reset total score
    current_time = pygame.time.get_ticks() / 1000  # Get the current time in seconds
    
    clock.tick(60)  # Ensure the clock starts fresh with the new game

    while running:
        dt = clock.tick(60) / 1000  # Delta time in seconds (ensures 60 FPS cap)
        total_time += dt  # Track total elapsed time
        time_counter += dt  # Track the time for scoring

        # Add 1 point to score every second
        if time_counter >= 1.0:
            score += 1
            time_counter = 0  # Reset the counter after each second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(event.device_index)
                joystick.init()
                joysticks.append(joystick)
                print(f"Joystick {joystick.get_name()} connected")
            if event.type == pygame.JOYDEVICEREMOVED:
                for joy in joysticks:
                    if joy.get_instance_id() == event.instance_id:
                        joysticks.remove(joy)
                        print("Joystick disconnected")
                        break
            if event.type == fire_ball_event:
                x = random.randrange(10, screen.get_width() - 10)
                fireballs.append(pygame.Rect(x, -20, 20, 20))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Assuming spacebar is used for shooting
                    bullet = player.shoot(current_time)  # Call shoot method
                    if bullet:
                        bullets.append(bullet)

        # Fireball movement
        for fireballrect in fireballs[:]:
            fireballrect.y += 175 * dt * difficulty * (score / 20) + 10  # Speed scales with difficulty
            if fireballrect.top > screen.get_height():
                fireballs.remove(fireballrect)

        # Bullet movement
        for bulletrect in bullets[:]:
            bulletrect.y -= 500 * dt  # Bullets move upward
            if bulletrect.bottom < 0:
                bullets.remove(bulletrect)

        # Check collision between bullets and fireballs
        for bulletrect in bullets[:]:
            for fireballrect in fireballs[:]:
                if bulletrect.colliderect(fireballrect):
                    bullets.remove(bulletrect)
                    fireballs.remove(fireballrect)
                    score_by_bullet += 10  # Add points for destroying a fireball
                    player.ammo += 4 if difficulty == 0.5 else 2  # Add ammo based on difficulty
                    break  # Break out of the loop after collision

        # Update the score with time + bullet points
        total_score = score + score_by_bullet

        # Check collision between player and fireballs
        player_rect = pygame.Rect(player.pos.x - 20, player.pos.y - 20, 40, 40)
        for fireballrect in fireballs[:]:
            if fireballrect.colliderect(player_rect):
                fireballs.remove(fireballrect)  # Remove fireball on hit
                player.lives -= 1  # Player loses a life
                if player.lives <= 0:
                    player_name_input = menu.get_widget("player_name")
                    player_name = player_name_input.get_value() if player_name_input else "Player"
                    update_highscores(player_name, total_score)
                    show_highscores()
                    return

        # Player movement with boundary checks
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player.pos.y > 20:
            player.pos.y -= player.speed * dt
        if keys[pygame.K_s] and player.pos.y < screen.get_height() - 20:
            player.pos.y += player.speed * dt
        if keys[pygame.K_a] and player.pos.x > 20:
            player.pos.x -= player.speed * dt
        if keys[pygame.K_d] and player.pos.x < screen.get_width() - 20:
            player.pos.x += player.speed * dt

        # Handle joystick input for movement
        for joystick in joysticks:
            hor_move = joystick.get_axis(0)  # Horizontal movement
            vert_move = joystick.get_axis(1)  # Vertical movement

            # Deadzone filtering
            if abs(hor_move) > 0.1:
                player.pos.x += hor_move * player.speed * dt
            if abs(vert_move) > 0.1:
                player.pos.y += vert_move * player.speed * dt

            # Constrain player position within screen bounds
            player.pos.x = max(20, min(screen.get_width() - 20, player.pos.x))
            player.pos.y = max(20, min(screen.get_height() - 20, player.pos.y))

            # Shooting button (e.g., Button 0 on many controllers)
            if joystick.get_button(0) and player.ammo > 0:
                bullets.append(pygame.Rect(player.pos.x - 5, player.pos.y - 30, 10, 20))
                player.ammo -= 1
                time.sleep(0.1)  # Keep this delay as per your request
        bullet = pygame.Surface((15, 20))
        bullet.fill("white")
        # Render everything on screen
        screen.fill("purple")
        pygame.draw.circle(screen, "red", player.pos, 40)
        for fireballrect in fireballs:
            screen.blit(fireball, fireballrect)
        for bulletrect in bullets:
            screen.blit(bullet, bulletrect)

        # Draw lives and score
        font = pygame.font.Font(None, 50)
        lives_text = font.render(f'Lives: {player.lives}', True, (255, 255, 255))
        score_text = font.render(f'Score: {total_score}', True, (255, 255, 255))
        ammo_text = font.render(f'Ammo: {player.ammo}', True, (255, 255, 255))
        time_text = font.render(f'Time: {int(total_time)}s', True, (255, 255, 255))

        screen.blit(lives_text, (10, 10))
        screen.blit(score_text, (10, 50))
        screen.blit(ammo_text, (10, 90))
        screen.blit(time_text, (10, 130))

        pygame.display.flip()



# Load highscores
load_highscores()

# Main menu setup
menu = pygame_menu.Menu('Space Dividers', 400, 300, theme=pygame_menu.themes.THEME_GREEN)
menu.add.text_input('Name :', default="Player", textinput_id="player_name")
menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 0.5)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

# Main loop
while running:
    screen.fill("purple")
    menu.mainloop(screen)

pygame.quit()