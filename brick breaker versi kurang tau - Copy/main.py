import pygame
import sys
import sqlite3
import hashlib
from datetime import datetime

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Break-Breaker Pro")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Fonts
font_small = pygame.font.Font(None, 32)
font_medium = pygame.font.Font(None, 48)
font_large = pygame.font.Font(None, 64)

# Database setup
def init_db():
    conn = sqlite3.connect('breakbreaker.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    
    # Scores table
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  score INTEGER,
                  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

init_db()

# Game states
MENU = 0
LOGIN = 1
REGISTER = 2
GAME = 3
LEADERBOARD = 4

current_state = MENU
active_input = None
input_text = ""
logged_in_user = None
score = 0

# Game variables
paddle_x = WIDTH // 2 - 50
paddle_speed = 0

# Input boxes
login_boxes = {
    "username": pygame.Rect(WIDTH//2-100, HEIGHT//2-30, 200, 40),
    "password": pygame.Rect(WIDTH//2-100, HEIGHT//2+30, 200, 40)
}

register_boxes = {
    "username": pygame.Rect(WIDTH//2-100, HEIGHT//2-60, 200, 40),
    "password": pygame.Rect(WIDTH//2-100, HEIGHT//2, 200, 40),
    "confirm": pygame.Rect(WIDTH//2-100, HEIGHT//2+60, 200, 40)
}

# Helper functions
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_button(text, rect, color):
    pygame.draw.rect(screen, color, rect)
    draw_text(text, font_small, BLACK, rect.centerx, rect.centery)
    return rect

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect('breakbreaker.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = sqlite3.connect('breakbreaker.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", 
             (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def save_score(user_id, score):
    conn = sqlite3.connect('breakbreaker.db')
    c = conn.cursor()
    c.execute("INSERT INTO scores (user_id, score) VALUES (?, ?)", 
             (user_id, score))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect('breakbreaker.db')
    c = conn.cursor()
    c.execute('''SELECT users.username, scores.score, scores.date 
                 FROM scores JOIN users ON scores.user_id = users.id 
                 ORDER BY scores.score DESC LIMIT 10''')
    leaderboard = c.fetchall()
    conn.close()
    return leaderboard

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if current_state == MENU:
                if login_button.collidepoint(mouse_pos):
                    current_state = LOGIN
                    active_input = None
                elif register_button.collidepoint(mouse_pos):
                    current_state = REGISTER
                    active_input = None
                elif leaderboard_button.collidepoint(mouse_pos):
                    current_state = LEADERBOARD
                elif play_button.collidepoint(mouse_pos) and logged_in_user:
                    current_state = GAME
                    # Reset game variables here
            
            elif current_state == LOGIN:
                for name, box in login_boxes.items():
                    if box.collidepoint(mouse_pos):
                        active_input = name
                        input_text = ""
                if login_submit.collidepoint(mouse_pos):
                    user_id = login_user(login_boxes["username"].collidepoint(mouse_pos) and input_text or "", 
                                        login_boxes["password"].collidepoint(mouse_pos) and input_text or "")
                    if user_id:
                        logged_in_user = user_id
                        current_state = MENU
                
                if back_button.collidepoint(mouse_pos):
                    current_state = MENU
            
            elif current_state == REGISTER:
                for name, box in register_boxes.items():
                    if box.collidepoint(mouse_pos):
                        active_input = name
                        input_text = ""
                if register_submit.collidepoint(mouse_pos):
                    if register_user(register_boxes["username"].collidepoint(mouse_pos) and input_text or "",
                                   register_boxes["password"].collidepoint(mouse_pos) and input_text or ""):
                        current_state = MENU
                
                if back_button.collidepoint(mouse_pos):
                    current_state = MENU
            
            elif current_state == LEADERBOARD:
                if back_button.collidepoint(mouse_pos):
                    current_state = MENU
        
        if event.type == pygame.KEYDOWN:
            if active_input:
                if event.key == pygame.K_RETURN:
                    active_input = None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
    
    # Drawing based on state
    if current_state == MENU:
        draw_text("BREAK-BREAKER PRO", font_large, WHITE, WIDTH//2, 100)
        
        if logged_in_user:
            conn = sqlite3.connect('breakbreaker.db')
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE id=?", (logged_in_user,))
            username = c.fetchone()[0]
            conn.close()
            draw_text(f"Logged in as: {username}", font_small, GREEN, WIDTH//2, 160)
        
        play_button = draw_button("PLAY", pygame.Rect(WIDTH//2-100, 220, 200, 50), GREEN if logged_in_user else (100, 100, 100))
        login_button = draw_button("LOGIN", pygame.Rect(WIDTH//2-100, 290, 200, 50), BLUE)
        register_button = draw_button("REGISTER", pygame.Rect(WIDTH//2-100, 360, 200, 50), BLUE)
        leaderboard_button = draw_button("LEADERBOARD", pygame.Rect(WIDTH//2-100, 430, 200, 50), RED)
    
    elif current_state == LOGIN:
        draw_text("LOGIN", font_large, WHITE, WIDTH//2, 100)
        
        for name, box in login_boxes.items():
            color = RED if active_input == name else WHITE
            pygame.draw.rect(screen, color, box, 2)
            draw_text(name.capitalize() + ":", font_small, WHITE, box.left-60, box.centery)
            if active_input == name:
                text_surface = font_small.render(input_text, True, WHITE)
                screen.blit(text_surface, (box.x+5, box.y+5))
        
        login_submit = draw_button("LOGIN", pygame.Rect(WIDTH//2-100, HEIGHT//2+100, 200, 50), GREEN)
        back_button = draw_button("BACK", pygame.Rect(WIDTH//2-100, HEIGHT//2+160, 200, 50), RED)
    
    elif current_state == REGISTER:
        draw_text("REGISTER", font_large, WHITE, WIDTH//2, 70)
        
        for name, box in register_boxes.items():
            color = RED if active_input == name else WHITE
            pygame.draw.rect(screen, color, box, 2)
            draw_text(name.capitalize() + ":", font_small, WHITE, box.left-60, box.centery)
            if active_input == name:
                text_surface = font_small.render(input_text, True, WHITE)
                screen.blit(text_surface, (box.x+5, box.y+5))
        
        register_submit = draw_button("REGISTER", pygame.Rect(WIDTH//2-100, HEIGHT//2+120, 200, 50), GREEN)
        back_button = draw_button("BACK", pygame.Rect(WIDTH//2-100, HEIGHT//2+180, 200, 50), RED)
    
    elif current_state == LEADERBOARD:
        draw_text("LEADERBOARD", font_large, WHITE, WIDTH//2, 70)
        
        leaderboard = get_leaderboard()
        for i, (username, score, date) in enumerate(leaderboard):
            date_str = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
            draw_text(f"{i+1}. {username}: {score} ({date_str})", font_small, WHITE, WIDTH//2, 150 + i*40)
        
        back_button = draw_button("BACK", pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 50), RED)
    
    elif current_state == GAME:
        # Implement your game logic here
        draw_text("GAME SCREEN", font_large, WHITE, WIDTH//2, HEIGHT//2)
        # When game ends:
        # save_score(logged_in_user, score)
        # current_state = MENU
    
    pygame.display.flip()

pygame.quit()
sys.exit()