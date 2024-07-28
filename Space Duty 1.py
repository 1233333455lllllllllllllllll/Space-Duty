import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the player
player_x, player_y = WIDTH / 2, HEIGHT - 50
player_speed = 5
player_rect = pygame.Rect(player_x, player_y, 50, 50)
player_health = 5  # Player's health
strong_bullets = False
strong_bullets_timer = 0
multi_shot = False
multi_shot_timer = 0

# Set up the shield
shield_rect = pygame.Rect(player_x - 10, player_y - 20, 70, 20)
shield_health = 3
shield_active = False

# Set up the enemies
enemies = []
enemy_spawn_rate = 100
enemy_speed = 2
enemy_fire_rate = 200  # Increase the value to reduce the frequency of enemy bullets

# Set up the bullets
bullets = []
enemy_bullets = []

# Set up power-ups
power_ups = []
power_up_spawn_rate = 500
power_up_duration = 300  # Frames duration for power-up effect
speed_boost = False
speed_boost_timer = 0

# Set up the score
score = 0

# Track enemy bullets hitting the player
enemy_bullet_count = 0
max_enemy_bullet_count = 20  # Number of enemy bullets after which the player dies

# High score tracking
high_scores = []

def spawn_power_up():
    power_up_x = random.randint(0, WIDTH - 20)
    power_up_y = 0
    power_up_rect = pygame.Rect(power_up_x, power_up_y, 20, 20)
    power_ups.append((power_up_rect, random.choice(["strong_bullets", "speed_boost", "multi_shot"])))

def get_health_color(health):
    """Return color based on health level."""
    if health >= 4:
        return GREEN
    elif health == 3:
        return YELLOW
    else:
        return RED

def draw_explosion(x, y):
    """Draw an explosion effect at the given location."""
    pygame.draw.circle(screen, YELLOW, (x, y), 15)
    pygame.draw.circle(screen, RED, (x, y), 30, 3)

def update_high_scores(score):
    """Update the high score list."""
    high_scores.append(score)
    high_scores.sort(reverse=True)
    if len(high_scores) > 5:
        high_scores.pop()

def draw_player(x, y):
    """Draw the player's ship with custom design."""
    pygame.draw.polygon(screen, BLUE, [(x + 25, y), (x, y + 50), (x + 50, y + 50)])
    # Small weapon-like shapes on the front
    pygame.draw.rect(screen, BLUE, (x + 10, y - 10, 5, 15))
    pygame.draw.rect(screen, BLUE, (x + 35, y - 10, 5, 15))

# Game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_x, bullet_y = player_x + 20, player_y
                bullet_rect = pygame.Rect(bullet_x, bullet_y, 10, 20)
                bullets.append(bullet_rect)
                if multi_shot:
                    bullets.append(pygame.Rect(bullet_x - 20, bullet_y, 10, 20))
                    bullets.append(pygame.Rect(bullet_x + 40, bullet_y, 10, 20))
            elif event.key == pygame.K_s:  # Toggle shield activation
                shield_active = not shield_active
                if shield_active:
                    shield_rect = pygame.Rect(player_x - 10, player_y - 20, 70, 20)
                    shield_health = 3  # Reset shield health when activated

    # Move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
        player_x += player_speed
    player_rect.x = player_x
    if shield_active:
        shield_rect.x = player_x - 10

    # Spawn enemies
    if random.randint(0, enemy_spawn_rate) == 0:
        enemy_x, enemy_y = random.randint(0, WIDTH - 30), 0
        enemy_rect = pygame.Rect(enemy_x, enemy_y, 30, 30)
        enemies.append((enemy_rect, 1))  # Normal enemy

    # Spawn power-ups
    if random.randint(0, power_up_spawn_rate) == 0:
        spawn_power_up()

    # Move the enemies
    for i, (enemy, health) in enumerate(enemies):
        enemy.y += enemy_speed
        if enemy.y > HEIGHT:
            enemies.pop(i)

    # Move the power-ups
    for power_up, ptype in power_ups[:]:
        power_up.y += 2
        if power_up.y > HEIGHT:
            power_ups.remove((power_up, ptype))

    # Enemy fire
    for i, (enemy, health) in enumerate(enemies):
        if random.randint(0, enemy_fire_rate) == 0:
            for _ in range(2):  # Reduced number of bullets
                enemy_bullet_x, enemy_bullet_y = enemy.x + 15, enemy.y + 30
                enemy_bullet_rect = pygame.Rect(enemy_bullet_x, enemy_bullet_y, 10, 20)
                enemy_bullets.append(enemy_bullet_rect)

    # Move the bullets
    for bullet in bullets[:]:
        bullet.y -= 5
        if bullet.y < 0:
            bullets.remove(bullet)

    # Move the enemy bullets
    for enemy_bullet in enemy_bullets[:]:
        enemy_bullet.y += 5
        if enemy_bullet.y > HEIGHT:
            enemy_bullets.remove(enemy_bullet)

    # Check for collisions
    for bullet in bullets[:]:
        for i, (enemy, health) in enumerate(enemies):
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                health -= 5 if strong_bullets else 1
                if health <= 0:
                    draw_explosion(enemy.x + 15, enemy.y + 15)
                    enemies.pop(i)
                    score += 1

    for enemy_bullet in enemy_bullets[:]:
        if shield_active and enemy_bullet.colliderect(shield_rect):
            enemy_bullets.remove(enemy_bullet)
            shield_health -= 1
            if shield_health <= 0:
                shield_active = False
        elif enemy_bullet.colliderect(player_rect):
            enemy_bullets.remove(enemy_bullet)
            enemy_bullet_count += 1
            player_health -= 1
            if enemy_bullet_count >= max_enemy_bullet_count:
                update_high_scores(score)
                print("Game Over!")
                pygame.quit()
                sys.exit()

    for power_up, ptype in power_ups[:]:
        if power_up.colliderect(player_rect):
            power_ups.remove((power_up, ptype))
            if ptype == "strong_bullets":
                strong_bullets = True
                strong_bullets_timer = power_up_duration
            elif ptype == "speed_boost":
                speed_boost = True
                speed_boost_timer = power_up_duration
            elif ptype == "multi_shot":
                multi_shot = True
                multi_shot_timer = power_up_duration

    # Handle strong bullets timer
    if strong_bullets:
        strong_bullets_timer -= 1
        if strong_bullets_timer <= 0:
            strong_bullets = False

    # Handle speed boost timer
    if speed_boost:
        player_speed = 10  # Increased speed
        speed_boost_timer -= 1
        if speed_boost_timer <= 0:
            speed_boost = False
            player_speed = 5  # Reset speed

    # Handle multi shot timer
    if multi_shot:
        multi_shot_timer -= 1
        if multi_shot_timer <= 0:
            multi_shot = False

    # Draw everything
    screen.fill(BLACK)
    # Draw player as custom triangle with small weapon shapes
    draw_player(player_x, player_y)
    # Draw shield
    if shield_active:
        pygame.draw.rect(screen, BLUE, shield_rect)
    # Draw enemies
    for enemy, health in enemies:
        pygame.draw.polygon(screen, WHITE, [(enemy.x + 15, enemy.y), (enemy.x, enemy.y + 30), (enemy.x + 30, enemy.y + 30)])
    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, ORANGE, bullet)
    # Draw enemy bullets
    for enemy_bullet in enemy_bullets:
        pygame.draw.rect(screen, RED, enemy_bullet)
    # Draw power-ups
    for power_up, ptype in power_ups:
        color = GREEN if ptype == "strong_bullets" else YELLOW if ptype == "speed_boost" else BLUE
        pygame.draw.rect(screen, color, power_up)
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    # Draw health
    health_color = get_health_color(player_health)
    pygame.draw.rect(screen, health_color, (10, 50, player_health * 20, 20))
    pygame.draw.rect(screen, WHITE, (10, 50, 100, 20), 2)
    # Draw high scores
    high_score_text = font.render("High Scores", True, WHITE)
    screen.blit(high_score_text, (WIDTH - 150, 10))
    for idx, high_score in enumerate(high_scores):
        high_score_entry = font.render(f"{idx + 1}. {high_score}", True, WHITE)
        screen.blit(high_score_entry, (WIDTH - 150, 40 + idx * 30))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
