import pygame
import sys
import time
import math
import random

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Blade of Darkness - Shadow Ninja Edition")

# --- BACKGROUND MUSIC ---
music_volume = 0.5
try:
    pygame.mixer.music.load("menu_anthem.mp3")
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)
except:
    pass

# --- IMAGES LOAD ---
try:
    logo_img = pygame.image.load("42295.png").convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (550, 340))
except:
    logo_img = None

try:
    menu_bg_img = pygame.image.load("42285.jpg").convert()
except:
    menu_bg_img = None

try:
    gameplay_bg_img = pygame.image.load("gameplay_theme.jpg").convert()
except:
    gameplay_bg_img = None

def load_btn_img(filename):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, (70, 70))
    except:
        return None

img_left = load_btn_img("btn_left.png")
img_right = load_btn_img("btn_right.png")
img_jump = load_btn_img("btn_jump.png")
img_attack = load_btn_img("btn_attack.png")

# Colors
BG_COLOR = (10, 25, 15)
DARK_BLACK = (10, 10, 10)
GROUND_COLOR = (5, 15, 8)
HOUSE_COLOR = (15, 30, 18)
TEXT_COLOR = (240, 240, 240)
GOLD_COLOR = (218, 165, 32)
SCROLL_BG = (245, 222, 179)
SCROLL_BORDER = (139, 69, 19)
WHITE_BTN = (240, 240, 240)
RED_TEXT = (180, 20, 20)
GREEN_BTN = (34, 110, 60)
SPIKE_COLOR = (200, 40, 40)
ENEMY_COLOR = (15, 15, 15)

font = pygame.font.SysFont(None, 26)
font_large = pygame.font.SysFont("Georgia", 40, bold=True)
font_ninja = pygame.font.SysFont("Georgia", 22, bold=True)

# Game States
STATE_NAME_INPUT = -1
STATE_STORY = 0
STATE_SPLASH = 1
STATE_MENU = 2
STATE_LEVEL_SELECT = 3
STATE_SHOP = 4
STATE_LIVE_STORE = 5
STATE_COIN_STORE = 6
STATE_PLAYING = 7
STATE_PAUSED = 8
STATE_LEVEL_COMPLETE = 9
STATE_SETTINGS = 10
STATE_GAMEOVER = 11
STATE_POLICY = 12
STATE_RATEUS = 13
STATE_TRANSACTION = 14

current_state = STATE_NAME_INPUT
ninja_name = ""
splash_start_time = time.time()

lives = 3
max_lives = 3
life_regen_time = 900  # 15 minutes
last_life_lost_time = 0

coins = 300
first_time_life_bought = False
current_level = 1
highest_unlocked_level = 1
max_levels = 100
level_page = 0

player_x, player_y = 100, SCREEN_HEIGHT - 220
player_width, player_height = 45, 65
player_vel_y = 0
gravity = 0.5
is_jumping = False
jump_count = 0
facing_right = True
shurikens = []

world_width = 4500  
camera_x = 0
base_speed = 5
base_jump = -12

level_start_time = 0
level_elapsed_time = 0
level_coins_earned = 0
upgrade_shuriken_level = 0

unlocked_items = {"skill_speed": False, "skill_jump": False, "dress_shadow": False, "dress_blood": False}
selected_star_rating = 0
transaction_id_input = ""
purchasing_item_name = ""

platforms = []
level_spikes = []
level_coins = []
level_enemies = []
level_pits = []
goal_flag = None

def setup_level(lvl):
    global platforms, level_spikes, level_coins, level_enemies, level_pits, goal_flag
    platforms = [
        pygame.Rect(400, 480, 200, 22),
        pygame.Rect(800, 380, 220, 22),
        pygame.Rect(1250, 320, 190, 22),
        pygame.Rect(1650, 400, 210, 22),
        pygame.Rect(2100, 340, 200, 22),
        pygame.Rect(2600, 390, 220, 22),
        pygame.Rect(3100, 310, 200, 22),
        pygame.Rect(3550, 420, 190, 22)
    ]
    
    level_spikes = []
    spike_count = min(4 + lvl, 15)
    for _ in range(spike_count):
        sx = random.randint(600, world_width - 600)
        level_spikes.append(pygame.Rect(sx, SCREEN_HEIGHT - 135, 25, 20))

    level_pits = [
        pygame.Rect(1050, SCREEN_HEIGHT - 120, 130, 150),
        pygame.Rect(2200, SCREEN_HEIGHT - 120, 150, 150),
        pygame.Rect(3300, SCREEN_HEIGHT - 120, 140, 150)
    ]

    level_coins = []
    for p in platforms:
        level_coins.append([p.x + p.width//2 - 10, p.y - 45, False])
    for cx in range(350, world_width - 400, 250):
        level_coins.append([cx, SCREEN_HEIGHT - 165, False])

    level_enemies = []
    if lvl >= 2:
        enemy_count = min(1 + (lvl // 2), 8)
        for i in range(enemy_count):
            ex = 700 + (i * 450)
            level_enemies.append({"x": ex, "y": SCREEN_HEIGHT - 180, "width": 40, "height": 60, "alive": True, "dir": 1, "range": 150, "start_x": ex})

    goal_flag = pygame.Rect(world_width - 200, SCREEN_HEIGHT - 220, 30, 100)

def reset_level_position():
    global player_x, player_y, player_vel_y, is_jumping, jump_count, shurikens, level_start_time, level_elapsed_time, level_coins_earned, camera_x
    player_x = 100
    player_y = SCREEN_HEIGHT - 220
    player_vel_y = 0
    is_jumping = False
    jump_count = 0
    shurikens = []
    camera_x = 0
    level_start_time = time.time()
    level_elapsed_time = 0
    level_coins_earned = 0
    setup_level(current_level)

def draw_button(text, x, y, w, h, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    is_hovered = rect.collidepoint(mouse_pos)
    
    color = (max(bg_color[0]-30, 0), max(bg_color[1]-30, 0), max(bg_color[2]-30, 0)) if is_hovered else bg_color
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, GOLD_COLOR, rect, 2, border_radius=8)
    
    text_surf = custom_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
    if is_hovered and click[0] == 1:
        pygame.time.delay(150)
        return True
    return False

setup_level(current_level)
clock = pygame.time.Clock()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        
        if current_state == STATE_NAME_INPUT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(ninja_name.strip()) > 0:
                    current_state = STATE_STORY
                elif event.key == pygame.K_BACKSPACE:
                    ninja_name = ninja_name[:-1]
                else:
                    if len(ninja_name) < 20 and (event.unicode.isalnum() or event.unicode in ["-", "_", " "]):
                        ninja_name += event.unicode

        elif current_state == STATE_TRANSACTION:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(transaction_id_input.strip()) > 0:
                    if purchasing_item_name == "dress_shadow":
                        unlocked_items["dress_shadow"] = True
                    current_state = STATE_SHOP
                    transaction_id_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    transaction_id_input = transaction_id_input[:-1]
                else:
                    if len(transaction_id_input) < 25 and (event.unicode.isalnum() or event.unicode in ["-", "_"]):
                        transaction_id_input += event.unicode

    if current_state == STATE_NAME_INPUT:
        screen.fill(BG_COLOR)
        screen.blit(font_large.render("ENTER YOUR NINJA NAME", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 270, 180))
        
        box_rect = pygame.Rect(SCREEN_WIDTH//2 - 220, 270, 440, 60)
        pygame.draw.rect(screen, WHITE_BTN, box_rect, border_radius=8)
        pygame.draw.rect(screen, GOLD_COLOR, box_rect, 2, border_radius=8)
        
        name_surf = font_large.render(ninja_name, True, (20, 20, 20))
        screen.blit(name_surf, (box_rect.x + 15, box_rect.y + 8))
        
        if draw_button("CONTINUE", SCREEN_WIDTH//2 - 125, 370, 250, 50, custom_font=font_ninja, text_color=TEXT_COLOR, bg_color=GREEN_BTN):
            if len(ninja_name.strip()) > 0:
                current_state = STATE_STORY

    elif current_state == STATE_STORY:
        screen.fill(DARK_BLACK)
        screen.blit(font_large.render("CHAPTER 1: THE AWAKENING", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 280, 120))
        story_lines = [
            f"Hail, Master {ninja_name}! Darkness has consumed the bamboo valley.",
            "The ancient shadow clan has stolen the sacred scrolls of power.",
            "Equipped with your sharp blade and shurikens, you must fight through",
            "deadly traps, bottomless pits, and fierce enemies to restore peace.",
            "Your legendary journey begins now..."
        ]
        for idx, line in enumerate(story_lines):
            screen.blit(font.render(line, True, TEXT_COLOR), (SCREEN_WIDTH//2 - 380, 220 + idx * 45))
        
        if draw_button("START ADVENTURE", SCREEN_WIDTH//2 - 150, 480, 300, 50, custom_font=font_ninja, text_color=TEXT_COLOR, bg_color=GREEN_BTN):
            current_state = STATE_SPLASH
            splash_start_time = time.time()

    elif current_state == STATE_SPLASH:
        screen.fill(DARK_BLACK)
        if time.time() - splash_start_time > 3.0:
            current_state = STATE_MENU
            
        if logo_img:
            bg_rect = pygame.Rect(SCREEN_WIDTH//2 - 290, SCREEN_HEIGHT//2 - 200, 580, 360)
            pygame.draw.rect(screen, DARK_BLACK, bg_rect, border_radius=15)
            pygame.draw.rect(screen, GOLD_COLOR, bg_rect, 3, border_radius=15)
            logo_rect = logo_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(logo_img, logo_rect)
        
        sub_text = font.render(f"Ninja: {ninja_name} | Presented by Sagar Gaming", True, GOLD_COLOR)
        screen.blit(sub_text, (SCREEN_WIDTH//2 - sub_text.get_width()//2, SCREEN_HEIGHT//2 + 180))

    elif current_state == STATE_TRANSACTION:
        screen.fill(DARK_BLACK)
        screen.blit(font_large.render("ENTER TRANSACTION ID (Rs 10)", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 270, 160))
        screen.blit(font.render("Please enter your payment Transaction ID below to verify and unlock:", True, TEXT_COLOR), (SCREEN_WIDTH//2 - 290, 240))
        
        t_box = pygame.Rect(SCREEN_WIDTH//2 - 220, 310, 440, 60)
        pygame.draw.rect(screen, WHITE_BTN, t_box, border_radius=8)
        pygame.draw.rect(screen, GOLD_COLOR, t_box, 2, border_radius=8)
        
        t_surf = font_large.render(transaction_id_input, True, (20, 20, 20))
        screen.blit(t_surf, (t_box.x + 15, t_box.y + 8))
        
        if draw_button("VERIFY & UNLOCK", SCREEN_WIDTH//2 - 135, 410, 270, 45, custom_font=font_ninja, text_color=TEXT_COLOR, bg_color=GREEN_BTN):
            if len(transaction_id_input.strip()) > 0:
                if purchasing_item_name == "dress_shadow":
                    unlocked_items["dress_shadow"] = True
                current_state = STATE_SHOP
                transaction_id_input = ""

        if draw_button("Cancel", SCREEN_WIDTH//2 - 100, 470, 200, 40, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_SHOP

    elif current_state == STATE_MENU:
        if menu_bg_img:
            scaled_bg = pygame.transform.scale(menu_bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        else:
            screen.fill(BG_COLOR)

        lives_box_rect = pygame.Rect(30, 25, 210, 45)
        pygame.draw.rect(screen, (20, 35, 25), lives_box_rect, border_radius=6)
        pygame.draw.rect(screen, GOLD_COLOR, lives_box_rect, 2, border_radius=6)
        screen.blit(font.render(f"Lives: {max(0, lives)}/{max_lives}", True, TEXT_COLOR), (45, 36))
        
        plus_live_btn = pygame.Rect(lives_box_rect.right - 35, lives_box_rect.y + 6, 32, 32)
        pygame.draw.circle(screen, (30, 100, 200), plus_live_btn.center, 16)
        screen.blit(font.render("+", True, TEXT_COLOR), (plus_live_btn.centerx - 6, plus_live_btn.centery - 10))
        if plus_live_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] == 1:
            pygame.time.delay(150)
            current_state = STATE_LIVE_STORE

        if lives < max_lives and last_life_lost_time > 0:
            elapsed = time.time() - last_life_lost_time
            time_left = max(0, int(life_regen_time - elapsed))
            if time_left == 0:
                lives = max_lives
                last_life_lost_time = 0
            else:
                m_timer, s_timer = time_left // 60, time_left % 60
                timer_display_str = f"Refill in: {m_timer:02d}:{s_timer:02d}"
                screen.blit(font.render(timer_display_str, True, GOLD_COLOR), (30, 75))

        coins_box_rect = pygame.Rect(SCREEN_WIDTH - 210, 25, 180, 45)
        pygame.draw.rect(screen, (20, 35, 25), coins_box_rect, border_radius=6)
        pygame.draw.rect(screen, GOLD_COLOR, coins_box_rect, 2, border_radius=6)
        screen.blit(font.render(f"Coins: {coins}", True, GOLD_COLOR), (SCREEN_WIDTH - 195, 36))

        plus_coin_btn = pygame.Rect(coins_box_rect.right - 35, coins_box_rect.y + 6, 32, 32)
        pygame.draw.circle(screen, (30, 100, 200), plus_coin_btn.center, 16)
        screen.blit(font.render("+", True, TEXT_COLOR), (plus_coin_btn.centerx - 6, plus_coin_btn.centery - 10))
        if plus_coin_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] == 1:
            pygame.time.delay(150)
            current_state = STATE_COIN_STORE

        if draw_button("SHOP", SCREEN_WIDTH - 180, 85, 150, 40, custom_font=font_ninja, text_color=GOLD_COLOR, bg_color=(20, 35, 25)):
            current_state = STATE_SHOP

        title_surf = font_large.render("BLADE OF DARKNESS", True, GOLD_COLOR)
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 80))

        btn_w, btn_h = 320, 50
        center_x = SCREEN_WIDTH//2 - btn_w//2

        if draw_button("New Game", center_x, 180, btn_w, btn_h):
            if lives > 0:
                current_level = highest_unlocked_level
                reset_level_position()
                current_state = STATE_PLAYING
            else:
                current_state = STATE_GAMEOVER

        if draw_button("Settings", center_x, 250, btn_w, btn_h):
            current_state = STATE_SETTINGS

        if draw_button("Quit", center_x, 320, btn_w, btn_h):
            pygame.quit()
            sys.exit()

    elif current_state == STATE_LIVE_STORE:
        screen.fill(DARK_BLACK)
        screen.blit(font_large.render("LIVE STORE (PREMIUM)", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 200, 50))
        box_w, box_h = 650, 400
        box_x, box_y = SCREEN_WIDTH//2 - 325, 130
        pygame.draw.rect(screen, (20, 25, 20), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, GOLD_COLOR, (box_x, box_y, box_w, box_h), 2, border_radius=12)

        offset_y = box_y + 30
        if not first_time_life_bought:
            if draw_button("Buy 3 Lives for 300 Coins (First Time Offer)", box_x + 40, offset_y, box_w - 80, 50, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
                if coins >= 300:
                    coins -= 300
                    lives = max_lives
                    first_time_life_bought = True
                    last_life_lost_time = 0
            offset_y += 70

        if draw_button("3 Lives - Premium Pack (Rs 20)", box_x + 40, offset_y, box_w - 80, 50, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            lives = max_lives
            last_life_lost_time = 0
        offset_y += 70

        if draw_button("1 Hour Unlimited Lives - Premium (Rs 60)", box_x + 40, offset_y, box_w - 80, 50, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            lives = 99
        offset_y += 70

        if draw_button("24 Hours Unlimited Lives - Premium (Rs 120)", box_x + 40, offset_y, box_w - 80, 50, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            lives = 999
        offset_y += 70

        if draw_button("Back", box_x + 225, offset_y, 200, 40, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_MENU

    elif current_state == STATE_COIN_STORE:
        screen.fill(DARK_BLACK)
        screen.blit(font_large.render("COIN STORE (PREMIUM)", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 200, 60))
        box_w, box_h = 600, 320
        box_x, box_y = SCREEN_WIDTH//2 - 300, 150
        pygame.draw.rect(screen, (20, 25, 20), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, GOLD_COLOR, (box_x, box_y, box_w, box_h), 2, border_radius=12)

        if draw_button("1,000 Coins - Premium Pack (Rs 10)", box_x + 50, box_y + 50, box_w - 100, 55, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            coins += 1000
        if draw_button("5,000 Coins - Premium Pack (Rs 40)", box_x + 50, box_y + 130, box_w - 100, 55, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            coins += 5000
        if draw_button("Back", box_x + 200, box_y + 230, 200, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_MENU

    elif current_state == STATE_SHOP:
        screen.fill(BG_COLOR)
        screen.blit(font_large.render("SKILL & DRESS SHOP", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 180, 40))
        screen.blit(font.render(f"Coins: {coins}", True, GOLD_COLOR), (40, 45))
        
        box_w, box_h = 820, 440
        box_x, box_y = SCREEN_WIDTH//2 - 410, 110
        pygame.draw.rect(screen, (20, 35, 25), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(screen, GOLD_COLOR, (box_x, box_y, box_w, box_h), 2, border_radius=12)

        pygame.draw.rect(screen, (200, 40, 180), (box_x + 50, box_y + 20, 35, 20), border_radius=4)
        screen.blit(font.render("Ninja Speed Skill (500 Coins)", True, TEXT_COLOR), (box_x + 95, box_y + 20))
        status1 = "Unlocked" if unlocked_items["skill_speed"] else ("Buy (500 Coins)" if coins >= 500 else "🔒 Locked")
        if draw_button(status1, box_x + box_w - 240, box_y + 20, 210, 40, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            if not unlocked_items["skill_speed"] and coins >= 500:
                coins -= 500
                unlocked_items["skill_speed"] = True

        pygame.draw.rect(screen, (200, 40, 180), (box_x + 50, box_y + 90, 35, 20), border_radius=4)
        screen.blit(font.render("Double Jump Mastery (500 Coins)", True, TEXT_COLOR), (box_x + 95, box_y + 90))
        status2 = "Unlocked" if unlocked_items["skill_jump"] else ("Buy (500 Coins)" if coins >= 500 else "🔒 Locked")
        if draw_button(status2, box_x + box_w - 240, box_y + 90, 210, 40, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            if not unlocked_items["skill_jump"] and coins >= 500:
                coins -= 500
                unlocked_items["skill_jump"] = True

        pygame.draw.rect(screen, (40, 200, 220), (box_x + 50, box_y + 160, 35, 20), border_radius=4)
        screen.blit(font.render("Shadow Ninja Outfit - Premium (Rs 10)", True, GOLD_COLOR), (box_x + 95, box_y + 160))
        status3 = "Equipped" if unlocked_items["dress_shadow"] else "Buy Rs 10"
        if draw_button(status3, box_x + box_w - 240, box_y + 160, 210, 40, custom_font=font, text_color=TEXT_COLOR, bg_color=GREEN_BTN):
            if not unlocked_items["dress_shadow"]:
                purchasing_item_name = "dress_shadow"
                current_state = STATE_TRANSACTION

        pygame.draw.rect(screen, (220, 180, 30), (box_x + 50, box_y + 230, 35, 20), border_radius=4)
        screen.blit(font.render("Blood Assassin Outfit (500 Coins)", True, TEXT_COLOR), (box_x + 95, box_y + 230))
        status4 = "Unlocked" if unlocked_items["dress_blood"] else ("Buy (500 Coins)" if coins >= 500 else "🔒 Locked")
        if draw_button(status4, box_x + box_w - 240, box_y + 230, 210, 40, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            if not unlocked_items["dress_blood"] and coins >= 500:
                coins -= 500
                unlocked_items["dress_blood"] = True

        if draw_button("Back to Menu", SCREEN_WIDTH//2 - 125, box_y + 350, 250, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_MENU

    elif current_state == STATE_SETTINGS:
        screen.fill(BG_COLOR)
        screen.blit(font_large.render("Settings, Policy & Rate Us", True, TEXT_COLOR), (SCREEN_WIDTH//2 - 240, 60))
        
        vol_label = font.render(f"Music Volume: {int(music_volume * 100)}%", True, GOLD_COLOR)
        screen.blit(vol_label, (SCREEN_WIDTH//2 - 160, 160))

        slider_x, slider_y, slider_w, slider_h = SCREEN_WIDTH//2 - 200, 210, 400, 16
        pygame.draw.rect(screen, (40, 60, 50), (slider_x, slider_y, slider_w, slider_h), border_radius=6)
        filled_w = int(slider_w * music_volume)
        pygame.draw.rect(screen, GREEN_BTN, (slider_x, slider_y, filled_w, slider_h), border_radius=6)
        pygame.draw.circle(screen, TEXT_COLOR, (slider_x + filled_w, slider_y + slider_h//2), 12)

        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if pygame.Rect(slider_x - 10, slider_y - 10, slider_w + 20, slider_h + 20).collidepoint(mouse_pos) and click[0] == 1:
            music_volume = max(0.0, min(1.0, (mouse_pos[0] - slider_x) / slider_w))
            pygame.mixer.music.set_volume(music_volume)

        if draw_button("Rate Us (5 Stars)", SCREEN_WIDTH//2 - 175, 270, 350, 45, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_RATEUS

        if draw_button("Game Policy & Terms", SCREEN_WIDTH//2 - 175, 330, 350, 45, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_POLICY

        if draw_button("Back to Menu", SCREEN_WIDTH//2 - 125, 410, 250, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_MENU

    elif current_state == STATE_POLICY:
        screen.fill(BG_COLOR)
        screen.blit(font_large.render("GAME POLICY & TERMS", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 180, 80))
        policy_text = [
            "1. Blade of Darkness is an action shadow ninja platformer game developed by Sagar Gaming.",
            "2. All user progress, high scores, and local purchases are securely saved on your device.",
            "3. Microtransactions and premium packs are simulated securely within authorized guidelines.",
            "4. Unauthorized redistribution, decompilation, or copying of source code is strictly prohibited."
        ]
        for idx, pt in enumerate(policy_text):
            screen.blit(font.render(pt, True, TEXT_COLOR), (SCREEN_WIDTH//2 - 450, 160 + idx * 45))
        if draw_button("Back", SCREEN_WIDTH//2 - 100, 420, 200, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_SETTINGS

    elif current_state == STATE_RATEUS:
        screen.fill(BG_COLOR)
        screen.blit(font_large.render("RATE OUR GAME", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 140, 100))
        screen.blit(font_ninja.render("Tap stars to rate your experience with Blade of Darkness:", True, TEXT_COLOR), (SCREEN_WIDTH//2 - 250, 170))
        
        star_start_x = SCREEN_WIDTH//2 - 160
        star_y = 250
        for i in range(1, 6):
            star_rect = pygame.Rect(star_start_x + (i - 1) * 65, star_y, 50, 50)
            is_filled = i <= selected_star_rating
            star_color = (220, 40, 40) if is_filled else (150, 150, 150)
            
            pygame.draw.rect(screen, (30, 40, 35), star_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD_COLOR, star_rect, 2, border_radius=8)
            star_surf = font_large.render("★", True, star_color)
            screen.blit(star_surf, star_surf.get_rect(center=star_rect.center))
            
            if star_rect.collidepoint(mouse_pos) and click[0] == 1:
                pygame.time.delay(120)
                selected_star_rating = i

        if selected_star_rating > 0:
            thank_msg = font_ninja.render(f"Thank you for giving {selected_star_rating} Stars!", True, GOLD_COLOR)
            screen.blit(thank_msg, (SCREEN_WIDTH//2 - thank_msg.get_width()//2, 330))

        if draw_button("Back", SCREEN_WIDTH//2 - 100, 410, 200, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_SETTINGS

    elif current_state == STATE_LEVEL_SELECT:
        screen.fill(BG_COLOR)
        screen.blit(font_large.render(f"Select Level (1 - 100) - {ninja_name}", True, GOLD_COLOR), (SCREEN_WIDTH//2 - 260, 30))

        levels_per_page = 20
        start_idx = level_page * levels_per_page + 1
        end_idx = min(start_idx + levels_per_page - 1, max_levels)

        grid_x = 160
        grid_y = 120
        btn_w, btn_h = 160, 65

        for i in range(start_idx, end_idx + 1):
            col = (i - 1) % 5
            row = ((i - 1) // 5) % 4
            bx = grid_x + col * 190
            by = grid_y + row * 85

            is_unlocked = (i <= highest_unlocked_level)
            btn_bg = GREEN_BTN if is_unlocked else (50, 50, 50)
            status_text = f"Level {i}" if is_unlocked else f"🔒 {i}"
            if draw_button(status_text, bx, by, btn_w, btn_h, custom_font=font, text_color=TEXT_COLOR if not is_unlocked else RED_TEXT, bg_color=btn_bg):
                if is_unlocked:
                    if lives > 0:
                        current_level = i
                        reset_level_position()
                        current_state = STATE_PLAYING
                    else:
                        current_state = STATE_GAMEOVER

        if level_page > 0:
            if draw_button("<- Prev", 160, 510, 140, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
                level_page -= 1
        if end_idx < max_levels:
            if draw_button("Next ->", SCREEN_WIDTH - 300, 510, 140, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
                level_page += 1

        if draw_button("Back to Menu", SCREEN_WIDTH//2 - 125, 510, 250, 45, custom_font=font, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_MENU

    elif current_state == STATE_PLAYING:
        if gameplay_bg_img:
            scaled_gp_bg = pygame.transform.scale(gameplay_bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_gp_bg, (0, 0))
        else:
            screen.fill(BG_COLOR)

        keys = pygame.key.get_pressed()
        spd_bonus = 1.25 if unlocked_items["skill_speed"] else 0
        jmp_bonus = 1.5 if unlocked_items["skill_jump"] else 0
        current_player_speed = base_speed + spd_bonus
        current_jump_strength = base_jump - jmp_bonus

        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = STATE_PAUSED
                if event.key == pygame.K_SPACE:
                    max_allowed_jumps = 3 if unlocked_items["skill_jump"] else 2
                    if not is_jumping or jump_count < max_allowed_jumps:
                        player_vel_y = current_jump_strength
                        is_jumping = True
                        jump_count += 1
                if event.key == pygame.K_f:
                    s_x = player_x + player_width if facing_right else player_x
                    s_y = player_y + 30
                    s_dir = (14 + upgrade_shuriken_level) if facing_right else (-14 - upgrade_shuriken_level)
                    shurikens.append([s_x, s_y, s_dir])

        btn_size = 70
        left_btn = pygame.Rect(40, SCREEN_HEIGHT - 100, btn_size, btn_size)
        right_btn = pygame.Rect(130, SCREEN_HEIGHT - 100, btn_size, btn_size)
        jump_btn = pygame.Rect(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 110, btn_size, btn_size)
        attack_btn = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 100, btn_size, btn_size)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if mouse_clicked:
            if left_btn.collidepoint(mouse_pos): move_left = True
            if right_btn.collidepoint(mouse_pos): move_right = True
            max_allowed_jumps = 3 if unlocked_items["skill_jump"] else 2
            if jump_btn.collidepoint(mouse_pos) and (not is_jumping or jump_count < max_allowed_jumps):
                player_vel_y = current_jump_strength
                is_jumping = True
                jump_count += 1
                pygame.time.delay(120)
            if attack_btn.collidepoint(mouse_pos):
                s_x = player_x + player_width if facing_right else player_x
                s_y = player_y + 30
                s_dir = (14 + upgrade_shuriken_level) if facing_right else (-14 - upgrade_shuriken_level)
                shurikens.append([s_x, s_y, s_dir])
                pygame.time.delay(150)

        if move_left:
            player_x -= current_player_speed
            facing_right = False
        if move_right:
            player_x += current_player_speed
            facing_right = True

        player_x = max(0, min(player_x, world_width - player_width))
        camera_x = player_x - SCREEN_WIDTH // 3
        camera_x = max(0, min(camera_x, world_width - SCREEN_WIDTH))

        player_x_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        
        if goal_flag and player_x_rect.colliderect(goal_flag):
            if current_level >= highest_unlocked_level:
                highest_unlocked_level = min(max_levels, current_level + 1)
            current_state = STATE_LEVEL_COMPLETE

        for plat in platforms:
            if player_x_rect.colliderect(plat):
                if move_right and player_x < plat.x:
                    player_x = plat.x - player_width
                elif move_left and player_x > plat.x:
                    player_x = plat.x + plat.width

        player_vel_y += gravity
        player_y += player_vel_y

        ground_level = SCREEN_HEIGHT - 120
        
        in_pit = False
        for pit in level_pits:
            if player_x + player_width//2 > pit.x and player_x + player_width//2 < pit.x + pit.width:
                if player_y >= ground_level - player_height:
                    in_pit = True
                    break

        if in_pit:
            player_y += 5
            if player_y > SCREEN_HEIGHT:
                lives -= 1
                if lives <= 0:
                    lives = 0
                    last_life_lost_time = time.time()
                    current_state = STATE_GAMEOVER
                else:
                    last_life_lost_time = time.time()
                    reset_level_position()
        else:
            if player_y >= ground_level - player_height:
                player_y = ground_level - player_height
                player_vel_y = 0
                is_jumping = False
                jump_count = 0

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for plat in platforms:
            if player_rect.colliderect(plat):
                if player_vel_y > 0 and (player_y + player_height - player_vel_y <= plat.y + 12):
                    player_y = plat.y - player_height
                    player_vel_y = 0
                    is_jumping = False
                    jump_count = 0
                elif player_vel_y < 0 and (player_y - player_vel_y >= plat.y + plat.height - 12):
                    player_y = plat.y + plat.height
                    player_vel_y = 0

        for spike in level_spikes:
            if player_rect.colliderect(spike):
                lives -= 1
                if lives <= 0:
                    lives = 0
                    last_life_lost_time = time.time()
                    current_state = STATE_GAMEOVER
                else:
                    last_life_lost_time = time.time()
                    reset_level_position()
                break

        for enemy in level_enemies:
            if enemy["alive"]:
                enemy["x"] += enemy["dir"] * (1.5 + current_level * 0.1)
                if abs(enemy["x"] - enemy["start_x"]) > enemy["range"]:
                    enemy["dir"] *= -1
                e_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["width"], enemy["height"])
                if player_rect.colliderect(e_rect):
                    lives -= 1
                    if lives <= 0:
                        lives = 0
                        last_life_lost_time = time.time()
                        current_state = STATE_GAMEOVER
                    else:
                        last_life_lost_time = time.time()
                        reset_level_position()
                    break

        for s in shurikens[:]:
            s[0] += s[2]
            if s[0] < 0 or s[0] > world_width:
                shurikens.remove(s)
            else:
                for enemy in level_enemies:
                    if enemy["alive"]:
                        e_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["width"], enemy["height"])
                        if e_rect.collidepoint(s[0], s[1]):
                            enemy["alive"] = False
                            shurikens.remove(s)
                            break
            if s in shurikens:
                pygame.draw.circle(screen, (220, 220, 220), (int(s[0] - camera_x), int(s[1])), 6)

        for coin in level_coins:
            if not coin[2]:
                coin_rect = pygame.Rect(coin[0], coin[1], 20, 20)
                if player_rect.colliderect(coin_rect):
                    coin[2] = True
                    coins += 10
                    level_coins_earned += 10

        pygame.draw.rect(screen, GROUND_COLOR, (0 - camera_x, ground_level, world_width, 150))
        for pit in level_pits:
            pygame.draw.rect(screen, (255, 255, 255), (pit.x - camera_x, ground_level, pit.width, 150))

        if goal_flag:
            flag_rx = goal_flag.x - camera_x
            pygame.draw.rect(screen, (180, 180, 180), (flag_rx + 10, goal_flag.y, 8, goal_flag.height))
            pygame.draw.polygon(screen, (220, 30, 30), [
                (flag_rx + 18, goal_flag.y),
                (flag_rx + 75, goal_flag.y + 25),
                (flag_rx + 18, goal_flag.y + 50)
            ])

        for spike in level_spikes:
            pygame.draw.polygon(screen, SPIKE_COLOR, [
                (spike.x - camera_x, spike.y + spike.height),
                (spike.x + spike.width//2 - camera_x, spike.y),
                (spike.x + spike.width - camera_x, spike.y + spike.height)
            ])
            pygame.draw.rect(screen, (100, 100, 100), (spike.x + spike.width//2 - 2 - camera_x, spike.y + spike.height, 4, 10))

        for plat in platforms:
            pygame.draw.rect(screen, HOUSE_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))

        for coin in level_coins:
            if not coin[2]:
                pygame.draw.circle(screen, GOLD_COLOR, (int(coin[0] - camera_x + 10), int(coin[1] + 10)), 10)

        for enemy in level_enemies:
            if enemy["alive"]:
                ex, ey = enemy["x"] - camera_x, enemy["y"]
                pygame.draw.rect(screen, ENEMY_COLOR, (ex + 5, ey + 15, enemy["width"] - 10, enemy["height"] - 15), border_radius=4)
                pygame.draw.circle(screen, ENEMY_COLOR, (ex + 20, ey + 10), 9)
                pygame.draw.line(screen, (200, 200, 200), (ex - 5, ey + 30), (ex + 25, ey + 30), 3)

        nx, ny = player_x - camera_x, player_y
        body_color = (180, 30, 150) if unlocked_items["dress_shadow"] else (0, 0, 0)
        pygame.draw.rect(screen, body_color, (nx + 12, ny + 20, player_width - 24, player_height - 20), border_radius=6)
        pygame.draw.circle(screen, (0, 0, 0), (nx + 22, ny + 12), 12)
        hat_color = (40, 200, 220) if unlocked_items["dress_shadow"] else (30, 40, 32)
        hat_pts = [(nx + 22, ny - 6), (nx - 8, ny + 8), (nx + 52, ny + 8)]
        pygame.draw.polygon(screen, hat_color, hat_pts)

        screen.blit(font.render(f"Ninja: {ninja_name}", True, GOLD_COLOR), (30, 20))
        screen.blit(font.render(f"Coins: {coins}", True, GOLD_COLOR), (30, 50))
        screen.blit(font.render(f"Lives: {max(0, lives)}/{max_lives}", True, TEXT_COLOR), (210, 20))
        screen.blit(font.render(f"Level: {current_level}", True, TEXT_COLOR), (SCREEN_WIDTH - 140, 20))

        pause_btn_rect = pygame.Rect(SCREEN_WIDTH - 70, 60, 45, 45)
        pygame.draw.rect(screen, (30, 50, 40), pause_btn_rect, border_radius=10)
        pygame.draw.rect(screen, GOLD_COLOR, pause_btn_rect, 2, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, (pause_btn_rect.x + 12, pause_btn_rect.y + 11, 7, 23))
        pygame.draw.rect(screen, TEXT_COLOR, (pause_btn_rect.x + 26, pause_btn_rect.y + 11, 7, 23))

        if pause_btn_rect.collidepoint(mouse_pos) and mouse_clicked:
            pygame.time.delay(150)
            current_state = STATE_PAUSED

        control_buttons = [
            (left_btn, img_left, "<-"),
            (right_btn, img_right, "->"),
            (jump_btn, img_jump, "^"),
            (attack_btn, img_attack, "⚔")
        ]

        for b_rect, b_img, fallback_symbol in control_buttons:
            if b_img:
                img_rect = b_img.get_rect(center=b_rect.center)
                screen.blit(b_img, img_rect)
            else:
                pygame.draw.circle(screen, (30, 50, 35), b_rect.center, b_rect.width//2)
                pygame.draw.circle(screen, GOLD_COLOR, b_rect.center, b_rect.width//2, 2)
                sym_surf = font_ninja.render(fallback_symbol, True, TEXT_COLOR)
                screen.blit(sym_surf, sym_surf.get_rect(center=b_rect.center))

    elif current_state == STATE_LEVEL_COMPLETE:
        scroll_w, scroll_h = 500, 380
        scroll_x, scroll_y = SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 190
        pygame.draw.rect(screen, SCROLL_BG, (scroll_x, scroll_y, scroll_w, scroll_h), border_radius=15)
        pygame.draw.rect(screen, SCROLL_BORDER, (scroll_x, scroll_y, scroll_w, scroll_h), 4, border_radius=15)
        screen.blit(font_ninja.render("LEVEL COMPLETED!", True, (120, 20, 20)), (SCREEN_WIDTH//2 - 110, scroll_y + 30))
        if draw_button("Next Level", scroll_x + 40, scroll_y + 290, scroll_w - 80, 50, custom_font=font_ninja, text_color=TEXT_COLOR, bg_color=GREEN_BTN):
            if current_level < max_levels:
                current_level += 1
            reset_level_position()
            current_state = STATE_PLAYING

    elif current_state == STATE_PAUSED:
        scroll_w, scroll_h = 450, 360
        scroll_x, scroll_y = SCREEN_WIDTH//2 - 225, SCREEN_HEIGHT//2 - 180
        pygame.draw.rect(screen, SCROLL_BG, (scroll_x, scroll_y, scroll_w, scroll_h), border_radius=15)
        pygame.draw.rect(screen, SCROLL_BORDER, (scroll_x, scroll_y, scroll_w, scroll_h), 4, border_radius=15)

        screen.blit(font_ninja.render("PAUSE", True, (80, 40, 10)), (SCREEN_WIDTH//2 - 35, scroll_y + 25))

        btn_w = scroll_w - 80
        if draw_button("Resume", scroll_x + 40, scroll_y + 85, btn_w, 45, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_PLAYING
        if draw_button("Restart", scroll_x + 40, scroll_y + 145, btn_w, 45, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            reset_level_position()
            current_state = STATE_PLAYING
        if draw_button("Settings", scroll_x + 40, scroll_y + 205, btn_w, 45, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_SETTINGS
        if draw_button("Main Menu", scroll_x + 40, scroll_y + 265, btn_w, 45, custom_font=font_ninja, text_color=RED_TEXT, bg_color=WHITE_BTN):
            current_state = STATE_MENU

    elif current_state == STATE_GAMEOVER:
        scroll_w, scroll_h = 550, 400
        scroll_x, scroll_y = SCREEN_WIDTH//2 - 275, SCREEN_HEIGHT//2 - 200
        pygame.draw.rect(screen, SCROLL_BG, (scroll_x, scroll_y, scroll_w, scroll_h), border_radius=15)
        pygame.draw.rect(screen, SCROLL_BORDER, (scroll_x, scroll_y, scroll_w, scroll_h), 4, border_radius=15)
        
        screen.blit(font_large.render("GAME OVER", True, (150, 20, 20)), (SCREEN_WIDTH//2 - 120, scroll_y + 20))

        time_left = 0
        if last_life_lost_time > 0:
            elapsed = time.time() - last_life_lost_time
            time_left = max(0, int(life_regen_time - elapsed))
            if time_left == 0:
                lives = max_lives
                last_life_lost_time = 0
                current_state = STATE_MENU

        mins, secs = time_left // 60, time_left % 60
        timer_str = f"Next Life in: {mins:02d}:{secs:02d}" if time_left > 0 else "Lives Refilled!"
        
        screen.blit(font.render(timer_str, True, (60, 60, 60)), (scroll_x + 50, scroll_y + 90))

        btn_w = scroll_w - 100
        if draw_button("Get Lives in Store", scroll_x + 50, scroll_y + 160, btn_w, 50, custom_font=font_ninja, text_color=TEXT_COLOR, bg_color=(50, 100, 150)):
            current_state = STATE_LIVE_STORE

        if draw_button("Main Menu", scroll_x + 50, scroll_y + 235, btn_w, 50, custom_font=font_ninja, text_color=TEXT_COLOR, bg_color=(150, 40, 40)):
            current_state = STATE_MENU

    pygame.display.flip()
    clock.tick(60)