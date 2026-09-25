import pygame
import pymunk
import math

# --- Setup Pygame ---
pygame.init()
# Canvas expanded to 1600x1000 to create a dedicated UI header!
VIRTUAL_W, VIRTUAL_H = 1600, 1000 
current_width, current_height = VIRTUAL_W // 2, VIRTUAL_H // 2  

RENDER_FLAGS = pygame.RESIZABLE | pygame.DOUBLEBUF
screen = pygame.display.set_mode((current_width, current_height), RENDER_FLAGS, vsync=1)

game_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
pygame.display.set_caption("8 Ball Pool 3D")
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
game_state = "MENU" 
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
spin_ui_center = (60, 45)
spin_ui_radius = 28
spin_popup_active = False     
is_dragging_spin = False      
large_spin_center = (VIRTUAL_W // 2, VIRTUAL_H // 2)
large_spin_radius = 180

pause_btn = pygame.Rect(VIRTUAL_W - 190, 25, 160, 45)
close_spin_btn = pygame.Rect(VIRTUAL_W // 2 - 100, VIRTUAL_H // 2 + 220, 200, 60)
play_main_btn = pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 - 40, 400, 100)
quit_main_btn = pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 + 100, 400, 100)
resume_btn = pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 - 120, 400, 80)
restart_btn = pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 - 20, 400, 80)
quit_menu_btn = pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 + 80, 400, 80)

win_restart_btn = pygame.Rect(VIRTUAL_W//2 - 340, VIRTUAL_H//2 + 20, 320, 80)
win_menu_btn = pygame.Rect(VIRTUAL_W//2 + 20, VIRTUAL_H//2 + 20, 320, 80)

# --- PERFECT SYMMETRICAL 2:1 TABLE GEOMETRY (Shifted Down 80px) ---
# Play Area: Exactly 1200 x 600. Center is now (800, 540).
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
table_bg = pygame.Surface((VIRTUAL_W, VIRTUAL_H))

def build_static_table_cache():
    table_bg.fill(HEADER_BG)
    pygame.draw.rect(table_bg, (30, 15, 10), (70, 110, 1460, 860), border_radius=30) 
    pygame.draw.rect(table_bg, WOOD_BROWN, (80, 120, 1440, 840), border_radius=24)   
    pygame.draw.rect(table_bg, (110, 60, 30), (80, 120, 1440, 840), 6, border_radius=24) 
    pygame.draw.rect(table_bg, FELT_GREEN, (150, 190, 1300, 700), border_radius=15) 
    pygame.draw.rect(table_bg, (110, 60, 30), (150, 190, 1300, 700), 6, border_radius=15)

    silver = (200, 210, 220)
    for dx in [350, 500, 650, 950, 1100, 1250]:
        pygame.draw.circle(table_bg, silver, (dx, 180), 6) 
        pygame.draw.circle(table_bg, silver, (dx, 900), 6) 
    for dy in [390, 540, 690]:
        pygame.draw.circle(table_bg, silver, (140, dy), 6)  
        pygame.draw.circle(table_bg, silver, (1460, dy), 6)

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

# --- Game State Variables ---
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

# --- GRAPHICS CACHING ---
shadow_surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(shadow_surf, (0, 0, 0, 120), (ball_radius, ball_radius), ball_radius)

highlight_surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(highlight_surf, (255, 255, 255, 70), (ball_radius - 6, ball_radius - 6), int(ball_radius * 0.5))
pygame.draw.circle(highlight_surf, (255, 255, 255, 180), (ball_radius - 8, ball_radius - 8), int(ball_radius * 0.2))

ball_cache = {}
rotated_ball_cache = {} 

def get_or_create_ball_surf(color, is_stripe, num):
    if num not in ball_cache:
        surf = pygame.Surface((ball_radius*2, ball_radius*2), pygame.SRCALPHA)
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
    
    turn, p1_type, p2_type = 1, None, None
    game_over_msg, alert_msg, alert_timer = "", "", 0
    ball_in_hand, is_dragging_cue, is_charging = True, False, False
    shot_taken, scratch_this_turn, first_hit_ball_this_turn = False, False, None
    spin_x, spin_y = 0.0, 0.0
    cue_spin_vec = [0.0, 0.0]
    spin_popup_active, is_dragging_spin = False, False
    is_break_shot = True
    pocketed_this_turn_balls.clear()
    global_pocketed_balls.clear()
    animating_balls.clear()

    for body, shape in balls: space.remove(body, shape)
    balls.clear()
    ball_props.clear()

    # Re-centered exactly on the true Y=540 horizontal line
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
        elif event.type == pygame.VIDEORESIZE:
            current_width, current_height = event.w, event.h
            screen = pygame.display.set_mode((current_width, current_height), RENDER_FLAGS, vsync=1)
            
        elif event.type == pygame.KEYDOWN:
            if game_state == "NAMES":
                if event.key == pygame.K_RETURN:
                    if active_input == 1 and p1_name.strip() != "": active_input = 2
                    elif active_input == 2 and p2_name.strip() != "": setup_balls(); game_state = "PLAYING"
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == 1: p1_name = p1_name[:-1]
                    else: p2_name = p2_name[:-1]
                else:
                    if event.unicode.isprintable():
                        if active_input == 1 and len(p1_name) < 12: p1_name += event.unicode
                        elif active_input == 2 and len(p2_name) < 12: p2_name += event.unicode
            elif event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING" and game_over_msg == "":
                    if spin_popup_active: spin_popup_active = False
                    else: game_state = "PAUSED"
                elif game_state == "PAUSED": game_state = "PLAYING"
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "MENU":
                if play_main_btn.collidepoint(mouse_x, mouse_y):
                    p1_name, p2_name, active_input = "", "", 1 
                    game_state = "NAMES"
                elif quit_main_btn.collidepoint(mouse_x, mouse_y): running = False

            elif game_state == "NAMES":
                if pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 - 120, 600, 80).collidepoint(mouse_x, mouse_y): active_input = 1
                elif pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 + 40, 600, 80).collidepoint(mouse_x, mouse_y): active_input = 2
                elif pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 + 200, 400, 100).collidepoint(mouse_x, mouse_y):
                    if p1_name.strip() == "": p1_name = "Player 1"
                    if p2_name.strip() == "": p2_name = "Player 2"
                    setup_balls(); game_state = "PLAYING"

            elif game_state == "PAUSED":
                if resume_btn.collidepoint(mouse_x, mouse_y): game_state = "PLAYING"
                elif restart_btn.collidepoint(mouse_x, mouse_y): setup_balls(); game_state = "PLAYING"
                elif quit_menu_btn.collidepoint(mouse_x, mouse_y): game_state = "MENU"

            elif game_state == "PLAYING":
                if game_over_msg != "":
                    if win_restart_btn.collidepoint(mouse_x, mouse_y):
                        setup_balls()
                        game_state = "PLAYING"
                    elif win_menu_btn.collidepoint(mouse_x, mouse_y):
                        game_state = "MENU"
                elif spin_popup_active:
                    if close_spin_btn.collidepoint(mouse_x, mouse_y):
                        spin_popup_active = False
                    elif math.hypot(mouse_x - large_spin_center[0], mouse_y - large_spin_center[1]) <= large_spin_radius:
                        is_dragging_spin = True
                        spin_x = (mouse_x - large_spin_center[0]) / large_spin_radius
                        spin_y = (mouse_y - large_spin_center[1]) / large_spin_radius
                    else:
                        spin_popup_active = False
                else:
                    if pause_btn.collidepoint(mouse_x, mouse_y): game_state = "PAUSED"
                    elif math.hypot(mouse_x - spin_ui_center[0], mouse_y - spin_ui_center[1]) <= spin_ui_radius:
                        spin_popup_active = True 
                    elif game_over_msg == "" and cue_body in [b[0] for b in balls] and cue_body.velocity.length < 2 and not shot_taken:
                        if ball_in_hand and math.hypot(mouse_x - cue_body.position.x, mouse_y - cue_body.position.y) <= ball_radius * 3:
                            is_dragging_cue = True
                        else:
                            is_charging = True
                            charge_start_pos = (mouse_x, mouse_y)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if game_state == "PLAYING":
                if is_dragging_spin:
                    is_dragging_spin = False
                elif is_dragging_cue: is_dragging_cue = False 
                elif is_charging:
                    if current_power > 100: 
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

    if game_state in ["MENU", "NAMES"]:
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
            
        elif game_state == "NAMES":
            title = ui_font.render("ENTER PLAYER NAMES", True, WHITE)
            game_surface.blit(title, title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 240)))

            p1_box = pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 - 120, 600, 80)
            pygame.draw.rect(game_surface, WHITE if active_input == 1 else GRAY, p1_box, border_radius=10)
            game_surface.blit(ui_font.render("P1 Name:", True, WHITE), (p1_box.x - 200, p1_box.y + 20))
            game_surface.blit(ui_font.render(p1_name + ("_" if active_input == 1 else ""), True, BLACK), (p1_box.x + 20, p1_box.y + 20))

            p2_box = pygame.Rect(VIRTUAL_W//2 - 300, VIRTUAL_H//2 + 40, 600, 80)
            pygame.draw.rect(game_surface, WHITE if active_input == 2 else GRAY, p2_box, border_radius=10)
            game_surface.blit(ui_font.render("P2 Name:", True, WHITE), (p2_box.x - 200, p2_box.y + 20))
            game_surface.blit(ui_font.render(p2_name + ("_" if active_input == 2 else ""), True, BLACK), (p2_box.x + 20, p2_box.y + 20))

            start_btn = pygame.Rect(VIRTUAL_W//2 - 200, VIRTUAL_H//2 + 200, 400, 100)
            pygame.draw.rect(game_surface, BTN_GREEN, start_btn, border_radius=20)
            game_surface.blit(button_font.render("START MATCH", True, WHITE), button_font.render("START MATCH", True, WHITE).get_rect(center=start_btn.center))

    elif game_state in ["PLAYING", "PAUSED"]:
        if game_state == "PLAYING":
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
                if is_break_shot:
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
                    pygame.draw.line(game_surface, (255, 50, 50), target_ball_hit.position, (target_ball_hit.position.x + nx * 150, target_ball_hit.position.y + ny * 150), 3)
                    
                    tx, ty = -ny, nx
                    if (tx * dx + ty * dy) < 0: tx, ty = -tx, -ty
                    pygame.draw.line(game_surface, WHITE, (impact_x, impact_y), (impact_x + tx * 150, impact_y + ty * 150), 3)
                    
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
                        pygame.draw.line(game_surface, WHITE, (impact_x, impact_y), (impact_x + rx * 150, impact_y + ry * 150), 3)
            
            draw_cue_stick(game_surface, cue_body.position, aim_angle, current_power)
            
            if is_charging:
                pygame.draw.rect(game_surface, BLACK, (600, 140, 400, 20)) 
                pygame.draw.rect(game_surface, (255, 0, 0), (600, 140, min(current_power / 15, 400), 20))

        pygame.draw.rect(game_surface, BTN_BLUE, pause_btn, border_radius=10)
        game_surface.blit(button_font.render("PAUSE", True, WHITE), button_font.render("PAUSE", True, WHITE).get_rect(center=pause_btn.center))

        if ball_in_hand and not is_charging and game_over_msg == "" and not spin_popup_active:
            bih = ui_font.render("BALL IN HAND", True, (255, 255, 0))
            game_surface.blit(bih, bih.get_rect(center=(VIRTUAL_W//2, 45)))

        p1_color, p2_color = ((255, 255, 0) if turn == 1 else WHITE), ((255, 255, 0) if turn == 2 else WHITE)
        game_surface.blit(ui_font.render(p1_name, True, p1_color), ui_font.render(p1_name, True, p1_color).get_rect(midleft=(260, 35)))
        game_surface.blit(ui_font.render(p2_name, True, p2_color), ui_font.render(p2_name, True, p2_color).get_rect(midleft=(960, 35)))

        for p_type, offset in [(p1_type, 274), (p2_type, 974)]:
            if p_type:
                target_nums = [1,2,3,4,5,6,7] if p_type == "Solids" else [9,10,11,12,13,14,15]
                remaining = [n for n in target_nums if n not in global_pocketed_balls]
                for idx, num in enumerate(remaining):
                    draw_tiny_ball(game_surface, offset + (idx * 32), 65, BALL_COLORS[(num-1) % 7], p_type == "Stripes")
                if not remaining and 8 not in global_pocketed_balls: draw_tiny_ball(game_surface, offset, 65, BLACK, False, True)
            else: game_surface.blit(font.render("(Open Table)", True, GRAY), (offset - 14, 55))

        pygame.draw.circle(game_surface, WHITE, spin_ui_center, spin_ui_radius)
        pygame.draw.circle(game_surface, GRAY, spin_ui_center, spin_ui_radius, 4) 
        pygame.draw.circle(game_surface, (255, 0, 0), (int(spin_ui_center[0] + (spin_x * spin_ui_radius)), int(spin_ui_center[1] + (spin_y * spin_ui_radius))), 6)
        game_surface.blit(font.render("SPIN", True, WHITE), font.render("SPIN", True, WHITE).get_rect(center=(60, 95)))

        if alert_timer > 0:
            pygame.draw.rect(game_surface, (255, 100, 0), (500, 480, 600, 80), border_radius=20)
            game_surface.blit(ui_font.render(alert_msg, True, WHITE), ui_font.render(alert_msg, True, WHITE).get_rect(center=(VIRTUAL_W//2, 520)))

        # --- EXCLUSIVE OVERLAYS ---
        if game_over_msg:
            overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
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
            overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
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
            overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
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

    screen.fill((0, 0, 0)) 
    screen.blit(pygame.transform.scale(game_surface, (scaled_w, scaled_h)), (offset_x, offset_y))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()