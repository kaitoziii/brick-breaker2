import pygame
import random
from leaderboard import update_score
from events import trigger_special_event

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRICK_COLOR = (200, 0, 0)
PADDLE_COLOR = (0, 200, 0)
BALL_COLOR = (0, 0, 200)

# Game objects
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 60, 30

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

font = pygame.font.SysFont(None, 36)

def draw_text(text, x, y, color=WHITE):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def start(user_id):
    clock = pygame.time.Clock()

    # Paddle
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # Ball
    ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS*2, BALL_RADIUS*2)
    ball_dx, ball_dy = 5, -5

    # Bricks
    bricks = []
    for i in range(5):
        for j in range(10):
            bricks.append(pygame.Rect(j * (BRICK_WIDTH + 5) + 35, i * (BRICK_HEIGHT + 5) + 35, BRICK_WIDTH, BRICK_HEIGHT))

    running = True
    score = 0
    special_active = None
    special_timer = 0

    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-10, 0)
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.move_ip(10, 0)

        # Move ball
        ball.x += ball_dx
        ball.y += ball_dy

        # Collision with walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx *= -1
        if ball.top <= 0:
            ball_dy *= -1
        if ball.bottom >= HEIGHT:
            running = False  # Game over

        # Collision with paddle
        if ball.colliderect(paddle):
            ball_dy *= -1

        # Collision with bricks
        hit_index = ball.collidelist(bricks)
        if hit_index != -1:
            del bricks[hit_index]
            ball_dy *= -1
            score += 10
            # Special event trigger
            special_active = trigger_special_event()
            if special_active:
                special_timer = pygame.time.get_ticks()

        # Apply special events
        if special_active:
            if special_active == "big_paddle":
                paddle.width = 150
            elif special_active == "score_boost":
                score += 5
            elif special_active == "multi_ball":
                score += 10  # Simulate bonus for now

            if pygame.time.get_ticks() - special_timer > 5000:
                special_active = None
                paddle.width = PADDLE_WIDTH

        # Draw paddle, ball, bricks
        pygame.draw.rect(screen, PADDLE_COLOR, paddle)
        pygame.draw.ellipse(screen, BALL_COLOR, ball)
        for brick in bricks:
            pygame.draw.rect(screen, BRICK_COLOR, brick)

        draw_text(f"Score: {score}", 10, 10)

        pygame.display.flip()

    update_score(user_id, score)
    pygame.quit()
