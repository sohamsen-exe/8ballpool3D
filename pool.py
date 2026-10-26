import pygame
import pymunk
import math

# --- Setup Pygame ---
pygame.init()
VIRTUAL_W, VIRTUAL_H = 1600, 1000 

# Launch Windowed by default (completely fixes macOS transparency bugs)
info = pygame.display.Info()
current_width, current_height = int(info.current_w * 0.8), int(info.current_h * 0.8)

RENDER_FLAGS = pygame.RESIZABLE | pygame.DOUBLEBUF
screen = pygame.display.set_mode((current_width, current_height), RENDER_FLAGS, vsync=1)

game_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H)).convert()
pygame.display.set_caption("8-Ball Pool 3D")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 32, bold=True)
ui_font = pygame.font.SysFont(None, 48, bold=True)
title_font = pygame.font.SysFont(None, 144, bold=True)
button_font = pygame.font.SysFont(None, 56, bold=True)

# --- Setup Physics (Pymunk) ---
space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.6 
space.sleep_time_threshold = 0.5 

# --- Premium Colors ---
FELT_GREEN = (10, 115, 45)
WOOD_BROWN = (85, 45, 20)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
HEADER_BG = (15, 20, 40)
MENU_BG = (15, 20, 40)
CUE_COLOR = (245, 222, 179)
BTN_RED = (200, 50, 50)
BTN_BLUE = (50, 150, 200)
BTN_GREEN = (50, 200, 100)

BALL_COLORS = [
    (255, 215, 0), (0, 0, 255), (220, 0, 0), 
    (128, 0, 128), (255, 140, 0), (0, 128, 0), (128, 0, 0)
]

# --- Game Variables ---
ball_radius = 20
pocket_radius = 38
balls = []           
ball_props = []      
animating_balls = [] 

is_charging = False
aim_angle = 0
charge_start_pos = (0, 0)
current_power = 0

spin_x, spin_y = 0.0, 0.0 
cue_spin_vec = [0.0, 0.0]

# --- SPACIOUS UI LAYOUT ---
spin_ui_center = (VIRTUAL_W - 70, 55) # Moved to Far Right
spin_ui_radius = 28
spin_popup_active = False     
is_dragging_spin = False      
large_spin_center = (VIRTUAL_W // 2, VIRTUAL_H // 2)
large_spin_radius = 180

# --- Menu Buttons ---
play_main_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 - 40, 500, 100)
quit_main_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 + 100, 500, 100)

pvp_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 - 80, 500, 80)
vs_ai_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 + 20, 500, 80)
back_mode_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 + 120, 500, 80)

pause_btn = pygame.Rect(40, 25, 60, 60) # Moved to Far Left
close_spin_btn = pygame.Rect(VIRTUAL_W // 2 - 100, VIRTUAL_H // 2 + 220, 200, 60) 

resume_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 - 120, 500, 80)
restart_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 - 20, 500, 80)
quit_menu_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 + 80, 500, 80)

win_restart_btn = pygame.Rect(VIRTUAL_W//2 - 340, VIRTUAL_H//2 + 20, 320, 80) 
win_menu_btn = pygame.Rect(VIRTUAL_W//2 + 20, VIRTUAL_H//2 + 20, 320, 80) 

# --- PERFECT SYMMETRICAL 2:1 TABLE GEOMETRY ---
pockets = [(175, 215), (800, 215), (1425, 215), (175, 865), (800, 865), (1425, 865)]
pocket_shapes = [] 

CUSHION_POLYS = [
    [(210, 200), (770, 200), (760, 240), (250, 240)],   
    [(830, 200), (1390, 200), (1350, 240), (840, 240)], 
    [(210, 880), (770, 880), (760, 840), (250, 840)],   
    [(830, 880), (1390, 880), (1350, 840), (840, 840)], 
    [(160, 250), (160, 830), (200, 790), (200, 290)],   
    [(1440, 250), (1440, 830), (1400, 790), (1400, 290)]
]

# --- GPU-ACCELERATED STATIC BACKGROUND CACHE ---
table_bg = pygame.Surface((VIRTUAL_W, VIRTUAL_H)).convert()

def build_static_table_cache():
    table_bg.fill(HEADER_BG)
    pygame.draw.rect(table_bg, (30, 15, 10), (70, 110, 1460, 860), border_radius=30) 
    pygame.draw.rect(table_bg, WOOD_BROWN, (80, 120, 1440, 840), border_radius=24)   
    pygame.draw.rect(table_bg, (110, 60, 30), (80, 120, 1440, 840), 6, border_radius=24) 
    pygame.draw.rect(table_bg, FELT_GREEN, (150, 190, 1300, 700), border_radius=15) 
    pygame.draw.rect(table_bg, (110, 60, 30), (150, 190, 1300, 700), 6, border_radius=15)

    silver = (200, 210, 220)
    for dx in [350, 500, 650, 950, 1100, 1250]:
        pygame.draw.circle(table_bg, silver, (dx, 155), 6)  # Centered in top border
        pygame.draw.circle(table_bg, silver, (dx, 925), 6)  # Centered in bottom border
    for dy in [390, 540, 690]:
        pygame.draw.circle(table_bg, silver, (115, dy), 6)   # Centered in left border
        pygame.draw.circle(table_bg, silver, (1485, dy), 6)  # Centered in right border

    marking_color = (8, 90, 35)
    pygame.draw.line(table_bg, marking_color, (500, 240), (500, 840), 4)
    pygame.draw.arc(table_bg, marking_color, (400, 440, 200, 200), math.pi/2, 3*math.pi/2, 4)
    pygame.draw.circle(table_bg, marking_color, (800, 540), 6)  
    pygame.draw.circle(table_bg, marking_color, (1100, 540), 6) 
    pygame.draw.circle(table_bg, marking_color, (1250, 540), 6) 

    for pocket in pockets:
        pygame.draw.circle(table_bg, (140, 150, 160), pocket, pocket_radius + 8) 
        pygame.draw.circle(table_bg, (80, 90, 100), pocket, pocket_radius + 8, 4)
        pygame.draw.circle(table_bg, (10, 10, 15), pocket, pocket_radius)        
        pygame.draw.circle(table_bg, (0, 0, 0), pocket, pocket_radius, 6)        

    CUSHION_GREEN = (8, 100, 38)
    for poly in CUSHION_POLYS:
        pygame.draw.polygon(table_bg, CUSHION_GREEN, poly)

    shadow_dark = (5, 80, 30)
    shadow_light = (7, 95, 35)
    
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[0][3], CUSHION_POLYS[0][2], 4) 
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[1][3], CUSHION_POLYS[1][2], 4) 
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[4][3], CUSHION_POLYS[4][2], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[2][3], CUSHION_POLYS[2][2], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[3][3], CUSHION_POLYS[3][2], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[5][3], CUSHION_POLYS[5][2], 4) 
    
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[0][0], CUSHION_POLYS[0][3], 4) 
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[1][0], CUSHION_POLYS[1][3], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[2][0], CUSHION_POLYS[2][3], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[3][0], CUSHION_POLYS[3][3], 4) 
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[4][0], CUSHION_POLYS[4][3], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[5][0], CUSHION_POLYS[5][3], 4) 
    
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[0][2], CUSHION_POLYS[0][1], 4) 
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[1][2], CUSHION_POLYS[1][1], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[2][2], CUSHION_POLYS[2][1], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[3][2], CUSHION_POLYS[3][1], 4) 
    pygame.draw.line(table_bg, shadow_dark, CUSHION_POLYS[4][2], CUSHION_POLYS[4][1], 4) 
    pygame.draw.line(table_bg, shadow_light, CUSHION_POLYS[5][2], CUSHION_POLYS[5][1], 4) 

build_static_table_cache()

# --- Transition & Fade Variables ---
transition_state = "FADE_IN"
next_game_state = ""
ui_alpha = 255
fade_speed = 15

fade_overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H)).convert_alpha()
fade_overlay.fill((0, 0, 0))

def change_state(new_state):
    global transition_state, next_game_state
    if transition_state == "NONE":
        next_game_state = new_state
        transition_state = "FADE_OUT"

# --- Game State Variables ---
cheat_code = ""
cheat_hand_of_god = False
cheat_ray_of_hope = False
cheat_aimbot = False
game_state = "MENU"
game_mode = "PVP"
p1_name = "Player 1"
p2_name = "Player 2"
active_input = 1 
turn = 1
p1_type, p2_type = None, None
game_over_msg = ""
shot_taken, scratch_this_turn = False, False
first_hit_ball_this_turn = None
pocketed_this_turn_balls, global_pocketed_balls = [], []
alert_msg, alert_timer = "", 0
ball_in_hand, is_dragging_cue = False, False
is_break_shot = True
cue_is_stopped = True
is_break_shot = True
cue_is_stopped = True
aimbot_target_body = None
aimbot_target_pos = None

# --- GRAPHICS CACHING ---
shadow_surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA).convert_alpha()
pygame.draw.circle(shadow_surf, (0, 0, 0, 120), (ball_radius, ball_radius), ball_radius)

highlight_surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA).convert_alpha()
pygame.draw.circle(highlight_surf, (255, 255, 255, 70), (ball_radius - 6, ball_radius - 6), int(ball_radius * 0.5))
pygame.draw.circle(highlight_surf, (255, 255, 255, 180), (ball_radius - 8, ball_radius - 8), int(ball_radius * 0.2))

ball_cache = {}
rotated_ball_cache = {} 

def get_or_create_ball_surf(color, is_stripe, num):
    if num not in ball_cache:
        surf = pygame.Surface((ball_radius*2, ball_radius*2), pygame.SRCALPHA).convert_alpha()
        if num == 0: 
            pygame.draw.circle(surf, WHITE, (ball_radius, ball_radius), ball_radius)
            pygame.draw.circle(surf, (200, 0, 0), (ball_radius, 6), 4)
            pygame.draw.circle(surf, (200, 0, 0), (ball_radius, ball_radius*2 - 6), 4)
            pygame.draw.circle(surf, (200, 0, 0), (6, ball_radius), 4)
            pygame.draw.circle(surf, (200, 0, 0), (ball_radius*2 - 6, ball_radius), 4)
        elif is_stripe:
            pygame.draw.circle(surf, WHITE, (ball_radius, ball_radius), ball_radius)
            pygame.draw.rect(surf, color, (0, ball_radius - 8, ball_radius*2, 16))
        else: 
            pygame.draw.circle(surf, color, (ball_radius, ball_radius), ball_radius)
        
        if num != 0: 
            pygame.draw.circle(surf, WHITE, (ball_radius, ball_radius), 12) 
            text = font.render(str(num), True, BLACK)
            surf.blit(text, text.get_rect(center=(ball_radius, ball_radius)))
        ball_cache[num] = surf
    return ball_cache[num]

def create_ball(x, y, color, is_stripe=False, number=0):
    mass = 2
    moment = pymunk.moment_for_circle(mass, 0, ball_radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    shape = pymunk.Circle(body, ball_radius)
    shape.elasticity = 0.95 
    shape.friction = 0.2  
    space.add(body, shape)
    balls.append((body, shape))
    ball_props.append((color, is_stripe, number))
    return body, shape

def create_cushion(p1, p2, is_jaw=False):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, p1, p2, 0) 
    shape.elasticity = 0.4 if is_jaw else 0.85 
    shape.friction = 0.5
    space.add(body, shape)

def setup_balls():
    global cue_body, cue_shape, turn, p1_type, p2_type, game_over_msg
    global shot_taken, scratch_this_turn, first_hit_ball_this_turn
    global alert_msg, alert_timer, ball_in_hand, is_dragging_cue, is_charging
    global pocketed_this_turn_balls, global_pocketed_balls, spin_x, spin_y, cue_spin_vec, is_break_shot
    global spin_popup_active, is_dragging_spin
    global aimbot_target_body, aimbot_target_pos 
    
    turn, p1_type, p2_type = 1, None, None
    game_over_msg, alert_msg, alert_timer = "", "", 0
    ball_in_hand, is_dragging_cue, is_charging = True, False, False
    shot_taken, scratch_this_turn, first_hit_ball_this_turn = False, False, None
    spin_x, spin_y = 0.0, 0.0
    cue_spin_vec = [0.0, 0.0]
    spin_popup_active, is_dragging_spin = False, False
    is_break_shot = True
    aimbot_target_body, aimbot_target_pos = None, None 
    
    pocketed_this_turn_balls.clear()
    global_pocketed_balls.clear()
    animating_balls.clear()

    for body, shape in balls: space.remove(body, shape)
    balls.clear()
    ball_props.clear()

    cue_body, cue_shape = create_ball(400, 540, WHITE, number=0) 
    start_x, start_y = 1100, 540
    pattern = [(False,1), (True,9), (False,2), (True,10), (False,8), 
               (True,11), (False,3), (True,12), (False,4), (True,13), 
               (False,5), (True,14), (False,6), (True,15), (False,7)]
    idx = 0
    for row in range(5):
        for col in range(row + 1):
            x = start_x + (row * ball_radius * 2 * math.cos(math.radians(30)))
            y = start_y + (col * ball_radius * 2) - (row * ball_radius)
            is_stripe, num = pattern[idx]
            color = BLACK if num == 8 else BALL_COLORS[(num-1) % 7]
            create_ball(x, y, color, is_stripe, num)
            idx += 1

def draw_tiny_ball(surf, x, y, color, is_stripe, is_8_ball=False):
    r = 14 
    if is_stripe:
        pygame.draw.circle(surf, WHITE, (x, y), r)
        pygame.draw.line(surf, color, (x - r + 2, y), (x + r - 2, y), 10)
    else: pygame.draw.circle(surf, color, (x, y), r)
    if is_8_ball: pygame.draw.circle(surf, WHITE, (x, y), 6)
    pygame.draw.circle(surf, (255, 255, 255, 200), (x - 4, y - 4), 4)

def draw_avatar(surf, x, y, is_active, is_bot=False):
    av_surf = pygame.Surface((80, 80), pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(av_surf, (90, 100, 110), (0, 0, 80, 80)) 
    
    if is_bot:
        # Generic Robot Avatar
        pygame.draw.line(av_surf, (200, 200, 200), (40, 20), (40, 10), 2) # Antenna
        pygame.draw.circle(av_surf, (255, 50, 50), (40, 10), 4) # Antenna Bulb
        pygame.draw.rect(av_surf, (150, 160, 170), (20, 20, 40, 35), border_radius=6) # Head
        pygame.draw.rect(av_surf, (255, 255, 0), (28, 30, 8, 8), border_radius=2) # Left Eye
        pygame.draw.rect(av_surf, (255, 255, 0), (44, 30, 8, 8), border_radius=2) # Right Eye
        pygame.draw.rect(av_surf, (50, 50, 50), (30, 45, 20, 4)) # Mouth
        pygame.draw.rect(av_surf, (120, 130, 140), (15, 60, 50, 30), border_radius=8) # Body
    else:
        # Human Avatar
        pygame.draw.circle(av_surf, (220, 220, 220), (40, 30), 20) 
        pygame.draw.circle(av_surf, (220, 220, 220), (40, 95), 50) 
    
    mask = pygame.Surface((80, 80), pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, 80, 80), border_radius=12)
    av_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    border_color = (255, 215, 0) if is_active else (50, 50, 50)
    border_thick = 4 if is_active else 2
    
    surf.blit(av_surf, (x, y))
    pygame.draw.rect(surf, border_color, (x, y, 80, 80), border_thick, border_radius=12)

def render_single_ball(surf, bx, by, color, is_stripe, num, angle, current_radius):
    if current_radius <= 0: return
    
    angle_deg = int(math.degrees(angle)) % 360
    cache_key = (num, angle_deg, current_radius)
    
    if cache_key not in rotated_ball_cache:
        base_surf = get_or_create_ball_surf(color, is_stripe, num)
        rotated_ball = pygame.transform.rotate(base_surf, -angle_deg)
        scale_factor = current_radius / ball_radius
        if scale_factor < 1.0:
            new_w = max(1, int(rotated_ball.get_width() * scale_factor))
            new_h = max(1, int(rotated_ball.get_height() * scale_factor))
            rotated_ball = pygame.transform.smoothscale(rotated_ball, (new_w, new_h))
        rotated_ball_cache[cache_key] = rotated_ball

    final_ball = rotated_ball_cache[cache_key]
    surf.blit(final_ball, final_ball.get_rect(center=(bx, by)))
    
    if current_radius < ball_radius:
        curr_size = max(1, int(current_radius * 2))
        scaled_high = pygame.transform.smoothscale(highlight_surf, (curr_size, curr_size))
        surf.blit(scaled_high, (bx - current_radius, by - current_radius))
    else:
        surf.blit(highlight_surf, (bx - ball_radius, by - ball_radius))

def draw_cue_stick(surf, cue_pos, aim_angle, power):
    gap = 25 + (power * 0.015)
    length = 400
    
    dx = -math.cos(aim_angle)
    dy = -math.sin(aim_angle)
    nx = -dy
    ny = dx
    
    TIP_COLOR = (40, 150, 200)
    FERRULE_COLOR = (240, 240, 240)
    SHAFT_COLOR = (230, 200, 160)
    BUTT_COLOR = (25, 25, 30)
    BUMPER_COLOR = (10, 10, 10)
    
    segments = [
        (gap, gap + 5, 2.5, 2.7, TIP_COLOR),
        (gap + 5, gap + 15, 2.7, 3.0, FERRULE_COLOR),
        (gap + 15, gap + 200, 3.0, 5.0, SHAFT_COLOR),
        (gap + 200, gap + length - 15, 5.0, 7.5, BUTT_COLOR),
        (gap + length - 15, gap + length, 7.5, 7.5, BUMPER_COLOR)
    ]
    
    for (d1, d2, w1, w2, color) in segments:
        p1_center = (cue_pos[0] + dx * d1, cue_pos[1] + dy * d1)
        p2_center = (cue_pos[0] + dx * d2, cue_pos[1] + dy * d2)
        p1_top = (p1_center[0] + nx * w1, p1_center[1] + ny * w1)
        p1_bot = (p1_center[0] - nx * w1, p1_center[1] - ny * w1)
        p2_top = (p2_center[0] + nx * w2, p2_center[1] + ny * w2)
        p2_bot = (p2_center[0] - nx * w2, p2_center[1] - ny * w2)
        pygame.draw.polygon(surf, color, [p1_top, p2_top, p2_bot, p1_bot])

def draw_dynamic_elements(surf):
    surf.blit(table_bg, (0, 0))

    for body, shape in balls:
        if body.position.x > 0 and body.position.y > 0:
            surf.blit(shadow_surf, (body.position.x - ball_radius + 8, body.position.y - ball_radius + 8))

    for i, (body, shape) in enumerate(balls):
        if body.position.x > 0 and body.position.y > 0:
            color, is_stripe, num = ball_props[i]
            render_single_ball(surf, int(body.position.x), int(body.position.y), color, is_stripe, num, body.angle, ball_radius)

    for anim in animating_balls[:]:
        anim['radius'] -= 1.6 
        if anim['radius'] <= 0:
            animating_balls.remove(anim)
            continue
        color, is_stripe, num = anim['props']
        render_single_ball(surf, int(anim['x']), int(anim['y']), color, is_stripe, num, anim['angle'], anim['radius'])

for poly in CUSHION_POLYS:
    create_cushion(poly[0], poly[3], is_jaw=True)
    create_cushion(poly[3], poly[2], is_jaw=False)
    create_cushion(poly[2], poly[1], is_jaw=True)

for px, py in pockets:
    pb = pymunk.Body(body_type=pymunk.Body.STATIC)
    pb.position = (px, py)
    ps = pymunk.Circle(pb, pocket_radius)
    ps.sensor = True 
    space.add(pb, ps)
    pocket_shapes.append(ps)

setup_balls()

# --- Game Loop ---
running = True
while running:
    # 1. Process Fade Transitions
    if transition_state == "FADE_IN":
        ui_alpha -= fade_speed
        if ui_alpha <= 0:
            ui_alpha = 0
            transition_state = "NONE"
    elif transition_state == "FADE_OUT":
        ui_alpha += fade_speed
        if ui_alpha >= 255:
            ui_alpha = 255
            game_state = next_game_state
            transition_state = "FADE_IN"

    scale_w = current_width / VIRTUAL_W
    scale_h = current_height / VIRTUAL_H
    scale = min(scale_w, scale_h) 
    
    scaled_w = int(VIRTUAL_W * scale)
    scaled_h = int(VIRTUAL_H * scale)
    
    offset_x = (current_width - scaled_w) // 2
    offset_y = (current_height - scaled_h) // 2

    real_mouse_x, real_mouse_y = pygame.mouse.get_pos()
    mouse_x = (real_mouse_x - offset_x) / scale
    mouse_y = (real_mouse_y - offset_y) / scale

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        # Block inputs if the screen is currently fading
        if transition_state != "NONE" and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            continue
            
        elif event.type == pygame.VIDEORESIZE:
            current_width, current_height = event.w, event.h
            screen = pygame.display.set_mode((current_width, current_height), RENDER_FLAGS, vsync=1)
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen() # Safely toggles fullscreen on/off
            elif event.key == pygame.K_ESCAPE:
                if game_state == "MENU":
                    running = False # Safely exit the app from the Main Menu
                elif game_state in ["MODE_SELECT", "NAMES"]:
                    change_state("MENU")
                elif game_state == "PLAYING" and game_over_msg == "":
                    if spin_popup_active: spin_popup_active = False
                    else: game_state = "PAUSED"
                elif game_state == "PAUSED": game_state = "PLAYING"
            elif game_state == "NAMES":
                if event.key == pygame.K_RETURN:
                    if active_input == 1 and p1_name.strip() != "": 
                        if game_mode == "PvAI":
                            setup_balls()
                            change_state("PLAYING")
                        else:
                            active_input = 2
                    elif active_input == 2 and p2_name.strip() != "": 
                        setup_balls()
                        change_state("PLAYING")
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == 1: p1_name = p1_name[:-1]
                    else: p2_name = p2_name[:-1]
                else:
                    if event.unicode.isprintable():
                        if active_input == 1 and len(p1_name) < 12: p1_name += event.unicode
                        elif active_input == 2 and len(p2_name) < 12: p2_name += event.unicode
            else:
                # --- CHEAT CODE LISTENER ---
                if game_state == "PLAYING" and event.unicode.isprintable():
                    cheat_code += event.unicode.lower()
                    cheat_code = cheat_code[-10:]
                    
                    if "godmode" in cheat_code: 
                        cheat_hand_of_god = not cheat_hand_of_god
                        cheat_code = ""
                        alert_msg, alert_timer = f"HAND OF GOD: {'ON' if cheat_hand_of_god else 'OFF'}", 120
                    elif "raycast" in cheat_code: 
                        cheat_ray_of_hope = not cheat_ray_of_hope
                        cheat_code = ""
                        alert_msg, alert_timer = f"RAYCAST: {'ON' if cheat_ray_of_hope else 'OFF'}", 120
                    elif "aimbot" in cheat_code: 
                        cheat_aimbot = not cheat_aimbot
                        cheat_code = ""
                        alert_msg, alert_timer = f"AIMBOT: {'ON' if cheat_aimbot else 'OFF'}", 120
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "MENU":
                if play_main_btn.collidepoint(mouse_x, mouse_y):
                    change_state("MODE_SELECT")
                elif quit_main_btn.collidepoint(mouse_x, mouse_y): 
                    running = False

            elif game_state == "MODE_SELECT":
                if pvp_btn.collidepoint(mouse_x, mouse_y):
                    game_mode = "PVP"
                    p1_name, p2_name, active_input = "", "", 1 
                    change_state("NAMES")
                elif vs_ai_btn.collidepoint(mouse_x, mouse_y):
                    game_mode = "PvAI"
                    p1_name, p2_name, active_input = "", "AI Bot", 1 
                    change_state("NAMES")
                elif back_mode_btn.collidepoint(mouse_x, mouse_y):
                    change_state("MENU")

            elif game_state == "NAMES":
                if pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 - 120, 600, 80).collidepoint(mouse_x, mouse_y): active_input = 1
                elif game_mode == "PVP" and pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 + 40, 600, 80).collidepoint(mouse_x, mouse_y): active_input = 2
                elif pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 + 200, 400, 100).collidepoint(mouse_x, mouse_y):
                    if p1_name.strip() == "": p1_name = "Player 1"
                    if game_mode == "PVP" and p2_name.strip() == "": p2_name = "Player 2"
                    setup_balls(); change_state("PLAYING")

            elif game_state == "PAUSED":
                if resume_btn.collidepoint(mouse_x, mouse_y): change_state("PLAYING")
                elif restart_btn.collidepoint(mouse_x, mouse_y): setup_balls(); change_state("PLAYING")
                elif quit_menu_btn.collidepoint(mouse_x, mouse_y): change_state("MENU")

            elif game_state == "PLAYING":
                if game_over_msg != "":
                    if win_restart_btn.collidepoint(mouse_x, mouse_y): setup_balls(); change_state("PLAYING")
                    elif win_menu_btn.collidepoint(mouse_x, mouse_y): change_state("MENU")
                elif spin_popup_active:
                    if close_spin_btn.collidepoint(mouse_x, mouse_y): spin_popup_active = False
                    elif math.hypot(mouse_x - large_spin_center[0], mouse_y - large_spin_center[1]) <= large_spin_radius:
                        is_dragging_spin = True
                        spin_x = (mouse_x - large_spin_center[0]) / large_spin_radius
                        spin_y = (mouse_y - large_spin_center[1]) / large_spin_radius
                    else: spin_popup_active = False
                else:
                    if pause_btn.collidepoint(mouse_x, mouse_y): 
                        game_state = "PAUSED"
                    elif not (game_mode == "PvAI" and turn == 2):
                        if math.hypot(mouse_x - spin_ui_center[0], mouse_y - spin_ui_center[1]) <= spin_ui_radius:
                            spin_popup_active = True 
                        elif game_over_msg == "" and cue_body in [b[0] for b in balls] and cue_body.velocity.length < 2 and not shot_taken:
                            if (ball_in_hand or cheat_hand_of_god) and math.hypot(mouse_x - cue_body.position.x, mouse_y - cue_body.position.y) <= ball_radius * 3:
                                is_dragging_cue = True
                            else:
                                is_charging = True
                                charge_start_pos = (mouse_x, mouse_y)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if game_state == "PLAYING" and not (game_mode == "PvAI" and turn == 2):
                if is_dragging_spin: is_dragging_spin = False
                elif is_dragging_cue: is_dragging_cue = False 
                elif is_charging:
                    if current_power > 100: 
                        
                        # --- AIMBOT EXECUTION ---
                        if cheat_aimbot:
                            dx, dy = math.cos(aim_angle), math.sin(aim_angle)
                            closest_t, target_ball = 2000, None
                            
                            # 1. Find the ball the cue stick is pointing at
                            for b, s in balls:
                                if b == cue_body: continue
                                vx, vy = cue_body.position.x - b.position.x, cue_body.position.y - b.position.y
                                b_coef = (vx * dx + vy * dy)
                                c_coef = (vx * vx + vy * vy) - (4 * ball_radius * ball_radius) 
                                discriminant = b_coef * b_coef - c_coef
                                if discriminant >= 0:
                                    t1 = -b_coef - math.sqrt(discriminant)
                                    if 0 < t1 < closest_t: closest_t, target_ball = t1, b
                                    
                            # 2. Lock onto the pocket in that specific direction
                            if target_ball:
                                impact_x = cue_body.position.x + dx * closest_t
                                impact_y = cue_body.position.y + dy * closest_t
                                nat_dx = target_ball.position.x - impact_x
                                nat_dy = target_ball.position.y - impact_y
                                nat_dist = math.hypot(nat_dx, nat_dy)
                                
                                if nat_dist > 0:
                                    nat_dx /= nat_dist; nat_dy /= nat_dist
                                    best_align, best_pocket, best_angle = -999, None, aim_angle
                                    
                                    for px, py in pockets:
                                        p_dx, p_dy = px - target_ball.position.x, py - target_ball.position.y
                                        p_dist = math.hypot(p_dx, p_dy)
                                        if p_dist == 0: continue
                                        p_dx /= p_dist; p_dy /= p_dist
                                        
                                        align = (nat_dx * p_dx) + (nat_dy * p_dy)
                                        if align > best_align:
                                            best_align = align
                                            best_pocket = (px, py)
                                            ghost_x = target_ball.position.x - p_dx * (ball_radius * 2)
                                            ghost_y = target_ball.position.y - p_dy * (ball_radius * 2)
                                            best_angle = math.atan2(ghost_y - cue_body.position.y, ghost_x - cue_body.position.x)
                                            
                                    if best_pocket and best_align > 0.3: # Only snap if aiming roughly towards it
                                        aim_angle = best_angle
                                        aimbot_target_body = target_ball
                                        aimbot_target_pos = best_pocket
                        # --- END AIMBOT ---

                        force_vec = (current_power * math.cos(aim_angle), current_power * math.sin(aim_angle))
                        offset_x = spin_x * (ball_radius * 0.9)
                        offset_y = spin_y * (ball_radius * 0.9)
                        up = (math.cos(aim_angle - math.pi/2), math.sin(aim_angle - math.pi/2))
                        fwd = (math.cos(aim_angle), math.sin(aim_angle))
                        hit_ox = (up[0] * offset_x) - (fwd[0] * offset_y)
                        hit_oy = (up[1] * offset_x) - (fwd[1] * offset_y)
                        
                        cue_body.apply_impulse_at_world_point(force_vec, (cue_body.position.x + hit_ox, cue_body.position.y + hit_oy))
                        
                        spin_power = current_power * 3.0
                        cue_spin_vec = [-spin_y * math.cos(aim_angle) * spin_power, -spin_y * math.sin(aim_angle) * spin_power]
                        
                        spin_x, spin_y = 0.0, 0.0 
                        shot_taken, ball_in_hand = True, False 
                        
                    is_charging, current_power = False, 0

    # --- CURSOR HOVER LOGIC (Runs every frame) ---
    hovering_interactive = False

    if game_state == "MENU":
        if play_main_btn.collidepoint(mouse_x, mouse_y) or quit_main_btn.collidepoint(mouse_x, mouse_y):
            hovering_interactive = True

    elif game_state == "MODE_SELECT":
        if pvp_btn.collidepoint(mouse_x, mouse_y) or vs_ai_btn.collidepoint(mouse_x, mouse_y) or back_mode_btn.collidepoint(mouse_x, mouse_y):
            hovering_interactive = True

    elif game_state == "NAMES":
        p1_box = pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 - 120, 600, 80)
        p2_box = pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 + 40, 600, 80)
        start_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 + 200, 500, 100)
        if p1_box.collidepoint(mouse_x, mouse_y) or (game_mode == "PVP" and p2_box.collidepoint(mouse_x, mouse_y)) or start_btn.collidepoint(mouse_x, mouse_y):
            hovering_interactive = True

    elif game_state == "PAUSED":
        if resume_btn.collidepoint(mouse_x, mouse_y) or restart_btn.collidepoint(mouse_x, mouse_y) or quit_menu_btn.collidepoint(mouse_x, mouse_y):
            hovering_interactive = True

    elif game_state == "PLAYING":
        if game_over_msg != "":
            if win_restart_btn.collidepoint(mouse_x, mouse_y) or win_menu_btn.collidepoint(mouse_x, mouse_y):
                hovering_interactive = True
        elif spin_popup_active:
            if close_spin_btn.collidepoint(mouse_x, mouse_y) or math.hypot(mouse_x - large_spin_center[0], mouse_y - large_spin_center[1]) <= large_spin_radius:
                hovering_interactive = True
        else:
            if pause_btn.collidepoint(mouse_x, mouse_y) or math.hypot(mouse_x - spin_ui_center[0], mouse_y - spin_ui_center[1]) <= spin_ui_radius:
                hovering_interactive = True
            
            is_player_turn = not (game_mode == "PvAI" and turn == 2)
            cue_in_table = cue_body in [b[0] for b in balls]
            cue_is_stopped = cue_in_table and (cue_body.velocity.x**2 + cue_body.velocity.y**2 < 4)
            
            if is_player_turn and cue_in_table and cue_is_stopped and not shot_taken:
                dist_to_cue = math.hypot(mouse_x - cue_body.position.x, mouse_y - cue_body.position.y)
                can_drag = (ball_in_hand or cheat_hand_of_god) and dist_to_cue <= ball_radius * 3
                if is_dragging_cue or can_drag:
                    hovering_interactive = True

    if game_state in ["MENU", "MODE_SELECT", "NAMES"]:
        game_surface.fill(MENU_BG) 
        pygame.draw.rect(game_surface, WOOD_BROWN, (30, 30, VIRTUAL_W - 60, VIRTUAL_H - 60), 20, border_radius=30)
        
        if game_state == "MENU":
            shadow = title_font.render("8 BALL POOL 3D", True, BLACK)
            title = title_font.render("8 BALL POOL 3D", True, WHITE)
            game_surface.blit(shadow, shadow.get_rect(center=(VIRTUAL_W//2 + 6, VIRTUAL_H//2 - 200 + 6)))
            game_surface.blit(title, title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 200)))

            pygame.draw.rect(game_surface, BTN_GREEN, play_main_btn, border_radius=20)
            game_surface.blit(button_font.render("PLAY GAME", True, WHITE), button_font.render("PLAY GAME", True, WHITE).get_rect(center=play_main_btn.center))
            
            pygame.draw.rect(game_surface, BTN_RED, quit_main_btn, border_radius=20)
            game_surface.blit(button_font.render("QUIT", True, WHITE), button_font.render("QUIT", True, WHITE).get_rect(center=quit_main_btn.center))
            
        elif game_state == "MODE_SELECT":
            title = title_font.render("SELECT MODE", True, WHITE)
            game_surface.blit(title, title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 240)))

            pygame.draw.rect(game_surface, BTN_GREEN, pvp_btn, border_radius=20)
            game_surface.blit(button_font.render("PLAYER VS PLAYER", True, WHITE), button_font.render("PLAYER VS PLAYER", True, WHITE).get_rect(center=pvp_btn.center))
            
            pygame.draw.rect(game_surface, BTN_BLUE, vs_ai_btn, border_radius=20)
            game_surface.blit(button_font.render("PLAYER VS AI", True, WHITE), button_font.render("PLAYER VS AI", True, WHITE).get_rect(center=vs_ai_btn.center))
            
            pygame.draw.rect(game_surface, BTN_RED, back_mode_btn, border_radius=20)
            game_surface.blit(button_font.render("BACK", True, WHITE), button_font.render("BACK", True, WHITE).get_rect(center=back_mode_btn.center))

        elif game_state == "NAMES":
            title = ui_font.render("ENTER PLAYER NAMES", True, WHITE)
            game_surface.blit(title, title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 240)))

            p1_box = pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 - 120, 600, 80)
            pygame.draw.rect(game_surface, WHITE if active_input == 1 else GRAY, p1_box, border_radius=10)
            game_surface.blit(ui_font.render("P1 Name:", True, WHITE), (p1_box.x - 200, p1_box.y + 20))
            game_surface.blit(ui_font.render(p1_name + ("_" if active_input == 1 else ""), True, BLACK), (p1_box.x + 20, p1_box.y + 20))

            if game_mode == "PVP":
                p2_box = pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 + 40, 600, 80)
                pygame.draw.rect(game_surface, WHITE if active_input == 2 else GRAY, p2_box, border_radius=10)
                game_surface.blit(ui_font.render("P2 Name:", True, WHITE), (p2_box.x - 200, p2_box.y + 20))
                game_surface.blit(ui_font.render(p2_name + ("_" if active_input == 2 else ""), True, BLACK), (p2_box.x + 20, p2_box.y + 20))

            start_btn = pygame.Rect(VIRTUAL_W//2 - 250, VIRTUAL_H//2 + 200, 500, 100)
            pygame.draw.rect(game_surface, BTN_GREEN, start_btn, border_radius=20)
            game_surface.blit(button_font.render("START MATCH", True, WHITE), button_font.render("START MATCH", True, WHITE).get_rect(center=start_btn.center))

    elif game_state in ["PLAYING", "PAUSED"]:
        if game_state == "PLAYING":
            is_ai_turn = (game_mode == "PvAI" and turn == 2)

            # --- AI BOT EXECUTION LOGIC ---
            if is_ai_turn and game_over_msg == "" and cue_body in [b[0] for b in balls] and cue_is_stopped and not shot_taken:
                if not hasattr(cue_body, 'ai_state'): 
                    cue_body.ai_state = "THINKING"
                    cue_body.ai_timer = 90 
                    cue_body.ai_target_angle = 0
                    cue_body.ai_target_power = 0
                
                if cue_body.ai_state == "THINKING":
                    if cue_body.ai_timer > 0:
                        cue_body.ai_timer -= 1
                    else:
                        # --- AI BRAIN INITIALIZATION ---
                        target_nums = []
                        if p2_type is None:
                            target_nums = [i for i in range(1, 16) if i != 8 and i not in global_pocketed_balls]
                        else:
                            # FIX: Dynamically check the AI's actual assigned color
                            if p2_type == "Solids":
                                curr_score = len([b for b in global_pocketed_balls if b < 8])
                                if curr_score < 7: target_nums = [i for i in range(1, 8) if i not in global_pocketed_balls]
                                else: target_nums = [8]
                            else:
                                curr_score = len([b for b in global_pocketed_balls if b > 8])
                                if curr_score < 7: target_nums = [i for i in range(9, 16) if i not in global_pocketed_balls]
                                else: target_nums = [8]

                        def path_is_clear(start, end, ignore_bodies):
                            sx, sy = start
                            ex, ey = end
                            path_len = math.hypot(ex - sx, ey - sy)
                            if path_len == 0: return False
                            dx, dy = (ex - sx) / path_len, (ey - sy) / path_len
                            for b, _ in balls:
                                if b in ignore_bodies: continue
                                # STRICT: Check if a ball is sitting exactly on our destination
                                if math.hypot(b.position.x - ex, b.position.y - ey) < ball_radius * 2.1: return False
                                # STRICT: Check swept path
                                v_x, v_y = b.position.x - sx, b.position.y - sy
                                dot = v_x * dx + v_y * dy
                                if 0 < dot < path_len:
                                    proj_x, proj_y = sx + dot * dx, sy + dot * dy
                                    if math.hypot(b.position.x - proj_x, b.position.y - proj_y) < ball_radius * 2.1:
                                        return False
                            return True

                        best_aim_target = None
                        best_shot_quality = -9999 
                        is_banking = False

                        banks = [
                            (240, lambda x, y: (x, 240 - (y - 240)), 'Y'),
                            (840, lambda x, y: (x, 840 + (840 - y)), 'Y'),
                            (200, lambda x, y: (200 - (x - 200), y), 'X'),
                            (1400, lambda x, y: (1400 + (1400 - x), y), 'X')
                        ]

                        if is_break_shot:
                            for i, (b, s) in enumerate(balls):
                                if ball_props[i][2] == 1:
                                    best_aim_target = (b.position.x, b.position.y)
                                    break
                        else:
                            for i, (b, s) in enumerate(balls):
                                if ball_props[i][2] not in target_nums: continue
                                
                                # 1. EVALUATE DIRECT POCKET SHOTS
                                for px, py in pockets:
                                    dx_p, dy_p = px - b.position.x, py - b.position.y
                                    dist_p = math.hypot(dx_p, dy_p)
                                    if dist_p == 0: continue
                                    dir_px, dir_py = dx_p / dist_p, dy_p / dist_p
                                    
                                    ghost_x = b.position.x - dir_px * (ball_radius * 2)
                                    ghost_y = b.position.y - dir_py * (ball_radius * 2)
                                    
                                    if not path_is_clear((b.position.x, b.position.y), (px, py), [b, cue_body]): continue
                                    if not path_is_clear((cue_body.position.x, cue_body.position.y), (ghost_x, ghost_y), [b, cue_body]): continue
                                    
                                    dx_c, dy_c = ghost_x - cue_body.position.x, ghost_y - cue_body.position.y
                                    dist_c = math.hypot(dx_c, dy_c)
                                    if dist_c == 0: continue
                                    dir_cx, dir_cy = dx_c / dist_c, dy_c / dist_c
                                    
                                    alignment = (dir_cx * dir_px) + (dir_cy * dir_py)
                                    if alignment > 0.1: 
                                        shot_quality = alignment - (dist_p * 0.0002)
                                        
                                        cross = dir_cx * dir_py - dir_cy * dir_px
                                        tx, ty = (-dir_py, dir_px) if cross > 0 else (dir_py, -dir_px)
                                        scratch_risk = False
                                        for p2x, p2y in pockets:
                                            v_x, v_y = p2x - ghost_x, p2y - ghost_y
                                            dot = v_x * tx + v_y * ty
                                            if dot > 0: 
                                                proj_x, proj_y = ghost_x + dot * tx, ghost_y + dot * ty
                                                if math.hypot(p2x - proj_x, p2y - proj_y) < pocket_radius + 10:
                                                    scratch_risk = True; break
                                        
                                        if scratch_risk: shot_quality -= 5.0 

                                        if shot_quality > best_shot_quality:
                                            best_shot_quality = shot_quality
                                            best_aim_target = (ghost_x, ghost_y)
                                            is_banking = False
                                            
                                # 2. EVALUATE BANK SHOTS TO POCKET
                                for px, py in pockets:
                                    for c_val, mirror_func, axis in banks:
                                        mx, my = mirror_func(px, py)
                                        dx_m, dy_m = mx - b.position.x, my - b.position.y
                                        try:
                                            if axis == 'Y': t = (c_val - b.position.y) / dy_m
                                            else: t = (c_val - b.position.x) / dx_m
                                        except ZeroDivisionError: continue
                                        if 0 < t < 1:
                                            bank_x = b.position.x + t * dx_m
                                            bank_y = b.position.y + t * dy_m
                                            
                                            if not (200 <= bank_x <= 1400) or not (240 <= bank_y <= 840): continue
                                            if not path_is_clear((b.position.x, b.position.y), (bank_x, bank_y), [b, cue_body]): continue
                                            if not path_is_clear((bank_x, bank_y), (px, py), [b, cue_body]): continue
                                            
                                            dir_px, dir_py = (bank_x - b.position.x), (bank_y - b.position.y)
                                            dist_p = math.hypot(dir_px, dir_py)
                                            dir_px, dir_py = dir_px/dist_p, dir_py/dist_p
                                            
                                            ghost_x = b.position.x - dir_px * (ball_radius * 2)
                                            ghost_y = b.position.y - dir_py * (ball_radius * 2)
                                            
                                            if not path_is_clear((cue_body.position.x, cue_body.position.y), (ghost_x, ghost_y), [b, cue_body]): continue
                                            
                                            dx_c, dy_c = ghost_x - cue_body.position.x, ghost_y - cue_body.position.y
                                            dist_c = math.hypot(dx_c, dy_c)
                                            if dist_c == 0: continue
                                            dir_cx, dir_cy = dx_c / dist_c, dy_c / dist_c
                                            
                                            alignment = (dir_cx * dir_px) + (dir_cy * dir_py)
                                            if alignment > 0.1:
                                                shot_quality = alignment - 1.5 - (dist_p * 0.0002) 
                                                if shot_quality > best_shot_quality:
                                                    best_shot_quality = shot_quality
                                                    best_aim_target = (ghost_x, ghost_y)
                                                    is_banking = True

                        # 3. SET THE TARGET AND MOVE TO AIMING PHASE
                        if best_aim_target is None:
                            # Fallback 1: Safe direct contact (don't foul)
                            for i, (b, s) in enumerate(balls):
                                if ball_props[i][2] in target_nums:
                                    if path_is_clear((cue_body.position.x, cue_body.position.y), (b.position.x, b.position.y), [b, cue_body]):
                                        best_aim_target = (b.position.x, b.position.y)
                                        break
                                        
                        if best_aim_target is None:
                            # Fallback 2: Snookered Kick Shot (bounce off rail just to hit legally)
                            for i, (b, s) in enumerate(balls):
                                if ball_props[i][2] in target_nums:
                                    for c_val, mirror_func, axis in banks:
                                        mx, my = mirror_func(b.position.x, b.position.y)
                                        dx_m, dy_m = mx - cue_body.position.x, my - cue_body.position.y
                                        try:
                                            if axis == 'Y': t = (c_val - cue_body.position.y) / dy_m
                                            else: t = (c_val - cue_body.position.x) / dx_m
                                        except ZeroDivisionError: continue
                                        if 0 < t < 1:
                                            bank_x = cue_body.position.x + t * dx_m
                                            bank_y = cue_body.position.y + t * dy_m
                                            if not (200 <= bank_x <= 1400) or not (240 <= bank_y <= 840): continue
                                            if path_is_clear((cue_body.position.x, cue_body.position.y), (bank_x, bank_y), [b, cue_body]):
                                                if path_is_clear((bank_x, bank_y), (b.position.x, b.position.y), [b, cue_body]):
                                                    best_aim_target = (bank_x, bank_y)
                                                    is_banking = True
                                                    break
                                    if best_aim_target: break

                        if best_aim_target:
                            cue_body.ai_target_angle = math.atan2(best_aim_target[1] - cue_body.position.y, best_aim_target[0] - cue_body.position.x)
                            cue_body.ai_target_power = 6000 if is_break_shot else (3800 if is_banking else 3000)
                        else:
                            # Absolute last resort: Blindly hit towards a legal ball
                            for i, (b, s) in enumerate(balls):
                                if ball_props[i][2] in target_nums:
                                    cue_body.ai_target_angle = math.atan2(b.position.y - cue_body.position.y, b.position.x - cue_body.position.x)
                                    break
                            cue_body.ai_target_power = 2000

                        cue_body.ai_state = "AIMING"
                        is_charging = False
                        current_power = 0

                elif cue_body.ai_state == "AIMING":
                    diff = (cue_body.ai_target_angle - aim_angle) % (2 * math.pi)
                    if diff > math.pi: diff -= 2 * math.pi
                        
                    if abs(diff) < 0.03:
                        aim_angle = cue_body.ai_target_angle
                        cue_body.ai_state = "CHARGING"
                        is_charging = True
                    else:
                        aim_angle += diff * 0.08 

                elif cue_body.ai_state == "CHARGING":
                    is_charging = True
                    if current_power < cue_body.ai_target_power:
                        current_power += 80 
                    else:
                        current_power = cue_body.ai_target_power
                        cue_body.ai_state = "SHOOTING"
                        
                elif cue_body.ai_state == "SHOOTING":
                    force_vec = (current_power * math.cos(aim_angle), current_power * math.sin(aim_angle))
                    cue_body.apply_impulse_at_world_point(force_vec, cue_body.position)
                    
                    is_charging, current_power = False, 0
                    shot_taken, ball_in_hand = True, False
                    del cue_body.ai_state
            
            # --- USER INPUT LOGIC ---
            if not is_ai_turn:
                if is_dragging_spin:
                    dx = mouse_x - large_spin_center[0]
                    dy = mouse_y - large_spin_center[1]
                    dist = math.hypot(dx, dy)
                    if dist > large_spin_radius:
                        dx = dx / dist * large_spin_radius
                        dy = dy / dist * large_spin_radius
                    spin_x = dx / large_spin_radius
                    spin_y = dy / large_spin_radius

                if game_over_msg == "" and cue_body in [b[0] for b in balls] and cue_body.velocity.length < 2 and not shot_taken and not is_dragging_cue and not spin_popup_active:
                    if not is_charging: aim_angle = math.atan2(mouse_y - cue_body.position.y, mouse_x - cue_body.position.x)
                else: is_charging = False 

                if is_charging:
                    current_power = min(math.hypot(mouse_x - charge_start_pos[0], mouse_y - charge_start_pos[1]) * 30, 6000) 

            # Kept exactly inside inner rail Y bounds 240-840
            if is_dragging_cue and not spin_popup_active:
                if is_break_shot and not cheat_hand_of_god:
                    cx = max(220, min(mouse_x, 500)) 
                else:
                    cx = max(220, min(mouse_x, 1380))
                    
                cy = max(260, min(mouse_y, 820)) 
                valid_pos = True
                for b, _ in balls:
                    if b != cue_body and math.hypot(cx - b.position.x, cy - b.position.y) < ball_radius * 2.2:
                        valid_pos = False; break
                if valid_pos: cue_body.position, cue_body.velocity, cue_body.angular_velocity = (cx, cy), (0, 0), 0

            for _ in range(10):
                space.step(1 / 600.0)

                # --- AIMBOT MAGIC STEERING ---
                if cheat_aimbot and aimbot_target_body and shot_taken:
                    speed = aimbot_target_body.velocity.length
                    # Steering naturally ceases if it transfers momentum to another ball
                    if speed > 15: 
                        adx = aimbot_target_pos[0] - aimbot_target_body.position.x
                        ady = aimbot_target_pos[1] - aimbot_target_body.position.y
                        adist = math.hypot(adx, ady)
                        if adist > 0:
                            aimbot_target_body.velocity = (adx/adist * speed, ady/adist * speed)
                # -----------------------------
                
                if abs(cue_spin_vec[0]) > 0.1 or abs(cue_spin_vec[1]) > 0.1:
                    cue_body.apply_force_at_world_point((cue_spin_vec[0], cue_spin_vec[1]), cue_body.position)
                    cue_spin_vec[0] *= 0.993 
                    cue_spin_vec[1] *= 0.993
                
                for i, (body, shape) in enumerate(balls):
                    v_sq = body.velocity.x**2 + body.velocity.y**2
                    
                    if v_sq > 25 and abs(body.angular_velocity) > 0.1:
                        v_len = math.sqrt(v_sq)
                        dir_x = -body.velocity.y / v_len
                        dir_y = body.velocity.x / v_len
                        swerve_force = body.angular_velocity * v_len * 0.04
                        body.apply_force_at_world_point((dir_x * swerve_force, dir_y * swerve_force), body.position)
                    
                    if v_sq > 0.1:
                        for px, py in pockets:
                            dx_p = px - body.position.x
                            dy_p = py - body.position.y
                            dist_sq = dx_p**2 + dy_p**2
                            if dist_sq < 2116: 
                                dist = math.sqrt(dist_sq)
                                pull_x = dx_p / dist
                                pull_y = dy_p / dist
                                body.apply_force_at_world_point((pull_x * 12000, pull_y * 12000), body.position)

                    if shot_taken and first_hit_ball_this_turn is None and ball_props[i][2] != 0:
                        dx_b = cue_body.position.x - body.position.x
                        dy_b = cue_body.position.y - body.position.y
                        if dx_b**2 + dy_b**2 <= 1681: 
                            first_hit_ball_this_turn = ball_props[i]

            all_stopped = True
            for i, (body, shape) in enumerate(balls):
                if body.velocity.x**2 + body.velocity.y**2 < 4: 
                    body.velocity, body.angular_velocity = (0, 0), 0
                else: all_stopped = False
            cue_is_stopped = cue_body.velocity.x**2 + cue_body.velocity.y**2 < 4

            if shot_taken and all_stopped:
                aimbot_target_body, aimbot_target_pos = None, None
                foul_committed, foul_reason, turn_continues = False, "", False
                cue_spin_vec = [0.0, 0.0] 
                curr_type = p1_type if turn == 1 else p2_type
                curr_score = len([b for b in global_pocketed_balls if (b < 8 if (p1_type if turn == 1 else p2_type) == "Solids" else b > 8)])
                pocketed_nums = [b[2] for b in pocketed_this_turn_balls]

                first_hit_valid = False
                if first_hit_ball_this_turn:
                    _, hit_is_stripe, hit_num = first_hit_ball_this_turn
                    if curr_type is None and hit_num != 8: first_hit_valid = True
                    elif curr_type == "Stripes" and hit_is_stripe and hit_num != 8: first_hit_valid = True
                    elif curr_type == "Solids" and not hit_is_stripe and hit_num != 8: first_hit_valid = True
                    elif curr_score == 7 and hit_num == 8: first_hit_valid = True

                if scratch_this_turn: 
                    foul_committed, foul_reason = True, "FOUL: Scratch!"
                    cue_body.position, cue_body.velocity, cue_body.angular_velocity = (400, 540), (0, 0), 0
                elif first_hit_ball_this_turn is None: foul_committed, foul_reason = True, "FOUL: Hit nothing!"
                elif not first_hit_valid:
                    if curr_type is None and first_hit_ball_this_turn[2] == 8: foul_committed, foul_reason = True, "FOUL: Cannot hit 8-ball first!"
                    elif curr_score < 7 and first_hit_ball_this_turn[2] == 8: foul_committed, foul_reason = True, "FOUL: Hit 8-ball early!"
                    else: foul_committed, foul_reason = True, "FOUL: Hit wrong ball first!"

                if not foul_committed:
                    if curr_type is None: 
                        claimed_type = next(("Stripes" if b[1] else "Solids" for b in pocketed_this_turn_balls if b[2] != 8), None)
                        if claimed_type:
                            if turn == 1: p1_type, p2_type = claimed_type, ("Solids" if claimed_type == "Stripes" else "Stripes")
                            else: p2_type, p1_type = claimed_type, ("Solids" if claimed_type == "Stripes" else "Stripes")
                            turn_continues = True
                    else: 
                        if any(("Stripes" if b[1] else "Solids") == curr_type and b[2] != 8 for b in pocketed_this_turn_balls): turn_continues = True

                needs_rerack = False
                if 8 in pocketed_nums:
                    if is_break_shot: 
                        needs_rerack = True
                    else: 
                        if foul_committed or curr_score < 7:
                            game_over_msg = f"{p2_name if turn == 1 else p1_name} WINS!"
                        else:
                            game_over_msg = f"{p1_name if turn == 1 else p2_name} WINS!"

                if needs_rerack:
                    setup_balls()
                    alert_msg = "8-Ball pocketed on break! Table reracked."
                    alert_timer = 240
                else:
                    if foul_committed: alert_msg, alert_timer, turn, ball_in_hand = foul_reason, 180, (2 if turn == 1 else 1), True
                    elif not turn_continues: turn = 2 if turn == 1 else 1
                        
                    shot_taken, scratch_this_turn, first_hit_ball_this_turn = False, False, None
                    pocketed_this_turn_balls.clear()
                    is_break_shot = False

            if alert_timer > 0: alert_timer -= 1

            balls_to_remove = []
            for i, (body, shape) in enumerate(balls):
                out_of_bounds = not (-100 < body.position.x < VIRTUAL_W + 100 and -100 < body.position.y < VIRTUAL_H + 100)
                pocketed = any((body.position.x - px)**2 + (body.position.y - py)**2 < 2116 for px, py in pockets)
                    
                if pocketed or out_of_bounds:
                    color, is_stripe, num = ball_props[i]
                    if num == 0: 
                        if not scratch_this_turn:
                            animating_balls.append({'x': body.position.x, 'y': body.position.y, 'props': ball_props[i], 'angle': body.angle, 'radius': ball_radius})
                        body.position, body.velocity, body.angular_velocity = (-2000, -2000), (0, 0), 0
                        cue_spin_vec = [0.0, 0.0] 
                        scratch_this_turn = True
                    else:
                        balls_to_remove.append(i)
                        pocketed_this_turn_balls.append(ball_props[i])
                        global_pocketed_balls.append(num)
                        animating_balls.append({'x': body.position.x, 'y': body.position.y, 'props': ball_props[i], 'angle': body.angle, 'radius': ball_radius})

            for i in sorted(balls_to_remove, reverse=True):
                space.remove(balls[i][0], balls[i][1]) 
                balls.pop(i); ball_props.pop(i)             

        draw_dynamic_elements(game_surface)

        if game_state == "PLAYING" and game_over_msg == "" and cue_body in [b[0] for b in balls] and cue_is_stopped and not shot_taken and not is_dragging_cue:
            
            dx = math.cos(aim_angle)
            dy = math.sin(aim_angle)
            ray_len = 2000
            end_pt = (cue_body.position.x + dx * ray_len, cue_body.position.y + dy * ray_len)
            
            closest_t = ray_len
            target_ball_hit = None
            
            for b, s in balls:
                if b == cue_body: continue
                vx = cue_body.position.x - b.position.x
                vy = cue_body.position.y - b.position.y
                b_coef = (vx * dx + vy * dy)
                c_coef = (vx * vx + vy * vy) - (4 * ball_radius * ball_radius) 
                discriminant = b_coef * b_coef - c_coef
                if discriminant >= 0:
                    t1 = -b_coef - math.sqrt(discriminant)
                    if 0 < t1 < closest_t:
                        closest_t = t1
                        target_ball_hit = b
            
            for b, s in balls: space.remove(s)
            wall_query = space.segment_query_first(cue_body.position, end_pt, ball_radius, pymunk.ShapeFilter())
            for b, s in balls: space.add(s)
            
            hit_wall = False
            hit_pocket = False
            wall_normal = None
            
            if wall_query:
                wall_t = wall_query.alpha * ray_len
                if wall_t < closest_t:
                    closest_t = wall_t
                    target_ball_hit = None
                    hit_wall = True
                    wall_normal = wall_query.normal
                    if wall_query.shape in pocket_shapes:
                        hit_pocket = True
                        
            impact_x = cue_body.position.x + dx * closest_t
            impact_y = cue_body.position.y + dy * closest_t
            
            pygame.draw.line(game_surface, WHITE, cue_body.position, (impact_x, impact_y), 2)
            
            if target_ball_hit:
                is_illegal_target = False
                for i, (b, s) in enumerate(balls):
                    if b == target_ball_hit:
                        _, target_is_stripe, target_num = ball_props[i]
                        curr_type = p1_type if turn == 1 else p2_type
                        curr_score = len([pb for pb in global_pocketed_balls if (pb < 8 if curr_type == "Solids" else pb > 8)])
                        if curr_type is None:
                            if target_num == 8: is_illegal_target = True
                        else:
                            b_type = "Stripes" if target_is_stripe else "Solids"
                            if curr_score < 7:
                                if target_num == 8 or b_type != curr_type: is_illegal_target = True
                            else:
                                if target_num != 8: is_illegal_target = True
                        break

                if is_illegal_target:
                    pygame.draw.line(game_surface, (255, 50, 50), (impact_x - 12, impact_y - 12), (impact_x + 12, impact_y + 12), 6)
                    pygame.draw.line(game_surface, (255, 50, 50), (impact_x + 12, impact_y - 12), (impact_x - 12, impact_y + 12), 6)
                else:
                        pygame.draw.circle(game_surface, WHITE, (int(impact_x), int(impact_y)), ball_radius, 2)
                        nx = target_ball_hit.position.x - impact_x
                        ny = target_ball_hit.position.y - impact_y
                        dist = math.hypot(nx, ny)
                        if dist > 0: nx /= dist; ny /= dist
                        
                        ray_len = 1500 if cheat_ray_of_hope else 150
                        
                        pygame.draw.line(game_surface, (255, 50, 50), target_ball_hit.position, (target_ball_hit.position.x + nx * ray_len, target_ball_hit.position.y + ny * ray_len), 3)
                        
                        tx, ty = -ny, nx
                        if (tx * dx + ty * dy) < 0: tx, ty = -tx, -ty
                        pygame.draw.line(game_surface, WHITE, (impact_x, impact_y), (impact_x + tx * ray_len, impact_y + ty * ray_len), 3)
                    
            elif hit_wall:
                if hit_pocket:
                    pygame.draw.line(game_surface, (255, 50, 50), (impact_x - 12, impact_y - 12), (impact_x + 12, impact_y + 12), 6)
                    pygame.draw.line(game_surface, (255, 50, 50), (impact_x + 12, impact_y - 12), (impact_x - 12, impact_y + 12), 6)
                else:
                        pygame.draw.circle(game_surface, WHITE, (int(impact_x), int(impact_y)), ball_radius, 2)
                        if wall_normal:
                            dot_product = dx * wall_normal.x + dy * wall_normal.y
                            rx = dx - 2 * dot_product * wall_normal.x
                            ry = dy - 2 * dot_product * wall_normal.y
                            
                            ray_len = 1500 if cheat_ray_of_hope else 150
                            pygame.draw.line(game_surface, WHITE, (impact_x, impact_y), (impact_x + rx * ray_len, impact_y + ry * ray_len), 3)
            
            draw_cue_stick(game_surface, cue_body.position, aim_angle, current_power)
            
            if is_charging:
                pygame.draw.rect(game_surface, BLACK, (600, 140, 400, 20)) 
                pygame.draw.rect(game_surface, (255, 0, 0), (600, 140, min(current_power / 15, 400), 20))

        # --- DRAW HEADER UI (MINICLIP STYLE) ---
        
        # 1. Left: Pause Button
        pygame.draw.rect(game_surface, BTN_BLUE, pause_btn, border_radius=15)
        pygame.draw.rect(game_surface, WHITE, (pause_btn.centerx - 12, pause_btn.centery - 14, 8, 28), border_radius=2)
        pygame.draw.rect(game_surface, WHITE, (pause_btn.centerx + 4, pause_btn.centery - 14, 8, 28), border_radius=2)

        # 2. Left-Center: P1 Avatar and Name
        p1_color = (255, 255, 0) if turn == 1 else WHITE
        draw_avatar(game_surface, VIRTUAL_W//2 - 180, 15, turn == 1, is_bot=False)
        p1_name_surf = ui_font.render(p1_name, True, p1_color)
        game_surface.blit(p1_name_surf, p1_name_surf.get_rect(topright=(VIRTUAL_W//2 - 200, 25)))

        # 3. Right-Center: P2 Avatar and Name
        p2_color = (255, 255, 0) if turn == 2 else WHITE
        draw_avatar(game_surface, VIRTUAL_W//2 + 100, 15, turn == 2, is_bot=(game_mode == "PvAI"))
        p2_name_surf = ui_font.render(p2_name, True, p2_color)
        game_surface.blit(p2_name_surf, p2_name_surf.get_rect(topleft=(VIRTUAL_W//2 + 200, 25)))

        # 4. Render Pocketed Balls underneath Names
        for p_type, align_right, offset in [(p1_type, True, VIRTUAL_W//2 - 215), (p2_type, False, VIRTUAL_W//2 + 215)]:
            if p_type:
                target_nums = [1,2,3,4,5,6,7] if p_type == "Solids" else [9,10,11,12,13,14,15]
                remaining = [n for n in target_nums if n not in global_pocketed_balls]
                for idx, num in enumerate(remaining):
                    ball_x = offset - (idx * 32) if align_right else offset + (idx * 32)
                    draw_tiny_ball(game_surface, ball_x, 75, BALL_COLORS[(num-1) % 7], p_type == "Stripes")
                if not remaining and 8 not in global_pocketed_balls: 
                    draw_tiny_ball(game_surface, offset, 75, BLACK, False, True)
            else: 
                txt = font.render("(Open Table)", True, GRAY)
                if align_right:
                    game_surface.blit(txt, txt.get_rect(topright=(VIRTUAL_W//2 - 200, 65)))
                else:
                    game_surface.blit(txt, txt.get_rect(topleft=(VIRTUAL_W//2 + 200, 65)))

        # 5. Center: Game Mode Display
        mode_box = pygame.Rect(VIRTUAL_W//2 - 75, 25, 150, 60)
        pygame.draw.rect(game_surface, (20, 20, 20), mode_box, border_radius=12)
        pygame.draw.rect(game_surface, (255, 215, 0), mode_box, 3, border_radius=12)
        
        display_mode = "PvP" if game_mode == "PVP" else "vs AI"
        mode_text = button_font.render(display_mode, True, WHITE)
        
        # Offset Y by +3 pixels to account for the font's internal padding
        text_rect = mode_text.get_rect(center=(mode_box.centerx, mode_box.centery + 3))
        game_surface.blit(mode_text, text_rect)

        # 6. Right: Spin UI
        pygame.draw.circle(game_surface, WHITE, spin_ui_center, spin_ui_radius)
        pygame.draw.circle(game_surface, GRAY, spin_ui_center, spin_ui_radius, 4) 
        pygame.draw.circle(game_surface, (255, 0, 0), (int(spin_ui_center[0] + (spin_x * spin_ui_radius)), int(spin_ui_center[1] + (spin_y * spin_ui_radius))), 6)
        game_surface.blit(font.render("SPIN", True, WHITE), font.render("SPIN", True, WHITE).get_rect(center=(spin_ui_center[0], spin_ui_center[1] + 45)))

        # Ball In Hand overlay
        if ball_in_hand and not is_charging and game_over_msg == "" and not spin_popup_active:
            bih = ui_font.render("BALL IN HAND", True, (255, 255, 0))
            game_surface.blit(bih, bih.get_rect(center=(VIRTUAL_W//2, 115))) # Shifted down to not block the mode box

        if alert_timer > 0:
            pygame.draw.rect(game_surface, (255, 100, 0), (500, 480, 600, 80), border_radius=20)
            game_surface.blit(ui_font.render(alert_msg, True, WHITE), ui_font.render(alert_msg, True, WHITE).get_rect(center=(VIRTUAL_W//2, 520)))

        # --- EXCLUSIVE OVERLAYS ---
        if game_over_msg:
            overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA).convert_alpha()
            overlay.fill((0, 0, 0, 210)) 
            game_surface.blit(overlay, (0, 0))
            
            win_title_shadow = title_font.render(game_over_msg, True, BLACK)
            game_surface.blit(win_title_shadow, win_title_shadow.get_rect(center=(VIRTUAL_W//2 + 4, VIRTUAL_H//2 - 96)))
            
            win_title = title_font.render(game_over_msg, True, (255, 215, 0))
            game_surface.blit(win_title, win_title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 100)))
            
            pygame.draw.rect(game_surface, BTN_GREEN, win_restart_btn, border_radius=20)
            game_surface.blit(button_font.render("PLAY AGAIN", True, WHITE), button_font.render("PLAY AGAIN", True, WHITE).get_rect(center=win_restart_btn.center))
            
            pygame.draw.rect(game_surface, BTN_RED, win_menu_btn, border_radius=20)
            game_surface.blit(button_font.render("MAIN MENU", True, WHITE), button_font.render("MAIN MENU", True, WHITE).get_rect(center=win_menu_btn.center))

        elif spin_popup_active:
            overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA).convert_alpha()
            overlay.fill((0, 0, 0, 210)) 
            game_surface.blit(overlay, (0, 0))
            
            title = title_font.render("ADJUST SPIN", True, WHITE)
            game_surface.blit(title, title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 240)))
            
            pygame.draw.circle(game_surface, WHITE, large_spin_center, large_spin_radius)
            pygame.draw.circle(game_surface, GRAY, large_spin_center, large_spin_radius, 6)
            
            pygame.draw.line(game_surface, (200, 200, 200), (large_spin_center[0] - large_spin_radius, large_spin_center[1]), (large_spin_center[0] + large_spin_radius, large_spin_center[1]), 2)
            pygame.draw.line(game_surface, (200, 200, 200), (large_spin_center[0], large_spin_center[1] - large_spin_radius), (large_spin_center[0], large_spin_center[1] + large_spin_radius), 2)
            
            dot_x = int(large_spin_center[0] + spin_x * large_spin_radius)
            dot_y = int(large_spin_center[1] + spin_y * large_spin_radius)
            pygame.draw.circle(game_surface, (255, 0, 0), (dot_x, dot_y), 16)
            
            pygame.draw.rect(game_surface, BTN_BLUE, close_spin_btn, border_radius=20)
            game_surface.blit(button_font.render("DONE", True, WHITE), button_font.render("DONE", True, WHITE).get_rect(center=close_spin_btn.center))

        elif game_state == "PAUSED":
            overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA).convert_alpha()
            overlay.fill((0, 0, 0, 180)) 
            game_surface.blit(overlay, (0, 0))
            
            paused_surf = title_font.render("PAUSED", True, WHITE)
            game_surface.blit(paused_surf, paused_surf.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 260)))
            
            pygame.draw.rect(game_surface, BTN_BLUE, resume_btn, border_radius=20)
            game_surface.blit(button_font.render("RESUME", True, WHITE), button_font.render("RESUME", True, WHITE).get_rect(center=resume_btn.center))
            pygame.draw.rect(game_surface, BTN_GREEN, restart_btn, border_radius=20)
            game_surface.blit(button_font.render("RESTART MATCH", True, WHITE), button_font.render("RESTART MATCH", True, WHITE).get_rect(center=restart_btn.center))
            pygame.draw.rect(game_surface, BTN_RED, quit_menu_btn, border_radius=20)
            game_surface.blit(button_font.render("QUIT TO MENU", True, WHITE), button_font.render("QUIT TO MENU", True, WHITE).get_rect(center=quit_menu_btn.center))

    # --- APPLY CURSOR ---
    if is_dragging_cue:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
    elif hovering_interactive:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # --- Draw the Fade Overlay ---
    if ui_alpha > 0:
        fade_overlay.set_alpha(ui_alpha)
        game_surface.blit(fade_overlay, (0, 0))

    screen.fill((0, 0, 0)) 
    screen.blit(pygame.transform.scale(game_surface, (scaled_w, scaled_h)), (offset_x, offset_y))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()