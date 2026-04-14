import pygame
import random
import math
import config
import physics

# INITIAL CONFIG
pygame.init()  # Start all Pygame modules (video, sound, events...)
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))  # Create game window
pygame.display.set_caption("EcoThrow: Ultimate Ocean Defender")  # Title
clock = pygame.time.Clock()  # Tool to control game speed (FPS)

# Creation of fonts (Small, Medium, Large)
font_s = pygame.font.SysFont('Avenir Next', 22, bold=True)
font_m = pygame.font.SysFont('Avenir Next', 32, bold=True)
font_l = pygame.font.SysFont('Avenir Next', 60, bold=True)


# List of bins with their characteristics for collisions
bins = [
    {'type': 'Plastic', 'color': config.YELLOW, 'x': 450, 'y': 450, 'width': 70, 'height': 100},
    {'type': 'Paper', 'color': config.BLUE, 'x': 575, 'y': 450, 'width': 70, 'height': 100},
    {'type': 'Glass', 'color': config.GREEN, 'x': 700, 'y': 450, 'width': 70, 'height': 100}
]

# Definition of levels with difficulty...
levels = [
    {'name': 'Beach', 'sky_top': config.BEACH_SKY_TOP, 'sky_bottom': config.BEACH_SKY_BOTTOM, 'ground': config.BEACH_GROUND, 'wind': 0.0, 'gravity': 0.5, 'target_score': 2,
     'obstacle': False, 'decor_type': 'clouds'},
    {'name': 'Forest', 'sky_top': config.FOREST_SKY_TOP, 'sky_bottom': config.FOREST_SKY_BOTTOM, 'ground': config.FOREST_GROUND, 'wind': -0.1, 'gravity': 0.5, 'target_score': 3,
     'obstacle': False, 'decor_type': 'clouds'},
    {'name': 'Ocean', 'sky_top': config.OCEAN_SKY_TOP, 'sky_bottom': config.OCEAN_SKY_BOTTOM, 'ground': config.OCEAN_GROUND, 'wind': 0.25, 'gravity': 0.6,
     'target_score': 4, 'obstacle': 'shark', 'decor_type': 'bubbles'},
    {'name': 'Mountain', 'sky_top': config.MOUNTAIN_SKY_TOP, 'sky_bottom': config.MOUNTAIN_SKY_BOTTOM, 'ground': config.MOUNTAIN_GROUND, 'wind': 0.5, 'gravity': 0.7,
     'target_score': 5, 'obstacle': 'eagle', 'decor_type': 'snow'},
    {'name': 'Antarctica', 'sky_top': config.ANTARCTICA_SKY_TOP, 'sky_bottom': config.ANTARCTICA_SKY_BOTTOM, 'ground': config.ANTARCTICA_GROUND, 'wind': 0.8, 'gravity': 0.6,
     'target_score': 6, 'obstacle': 'penguin', 'decor_type': 'snow'},
    {'name': 'Efrei', 'sky_top': config.EFREI_SKY_TOP, 'sky_bottom': config.EFREI_SKY_BOTTOM, 'ground': config.EFREI_GROUND, 'wind': 0.2, 'gravity': 0.5,
     'target_score': 7, 'obstacle': False, 'decor_type': 'clouds'}
]

unlocked_levels_max = 0

try:
    img_efrei = pygame.transform.scale(pygame.image.load('efrei_photo.jpg'), (config.WIDTH, config.HEIGHT))
except:
    img_efrei = pygame.Surface((config.WIDTH, config.HEIGHT))
    img_efrei.fill(config.WHITE)

try:
    pygame.mixer.init()
    snd_score = pygame.mixer.Sound("score.wav")
    snd_throw = pygame.mixer.Sound("throw.wav")
    snd_error = pygame.mixer.Sound("error.wav")
except:
    snd_score = snd_throw = snd_error = None

def draw_gradient(surface, top, bottom):
    """Draws a vertical gradient over the entire surface"""
    for y in range(config.HEIGHT):
        factor = y / config.HEIGHT
        r = int(top[0] * (1 - factor) + bottom[0] * factor)
        g = int(top[1] * (1 - factor) + bottom[1] * factor)
        b = int(top[2] * (1 - factor) + bottom[2] * factor)
        pygame.draw.line(surface, (r, g, b), (0, y), (config.WIDTH, y))

particles = []
decor_bg = []

def init_decor(decor_type):
    decor_bg.clear()
    for _ in range(15):
        if decor_type == 'clouds':
            decor_bg.append({'x': random.randint(0, config.WIDTH), 'y': random.randint(50, 300), 'speed': random.uniform(0.1, 0.4), 'size': random.randint(40, 90)})
        elif decor_type == 'bubbles':
            decor_bg.append({'x': random.randint(0, config.WIDTH), 'y': random.randint(0, config.HEIGHT), 'speed': random.uniform(-1.5, -0.5), 'size': random.randint(5, 12)})
        elif decor_type == 'snow':
            decor_bg.append({'x': random.randint(0, config.WIDTH), 'y': random.randint(0, config.HEIGHT), 'speed_x': random.uniform(-1, 0.5), 'speed_y': random.uniform(1.5, 3.5), 'size': random.randint(2, 5)})

def create_particles(x, y, color, mode='trail'):
    if mode == 'trail':
        particles.append({'x': x, 'y': y, 'vx': random.uniform(-0.5, 0.5), 'vy': random.uniform(-0.5, 0.5), 'life': 20, 'color': color, 'size': 4})
    elif mode == 'explosion':
        for _ in range(25):
            particles.append({'x': x, 'y': y, 'vx': random.uniform(-5, 5), 'vy': random.uniform(-10, 2), 'life': random.randint(30, 60), 'color': random.choice([color, config.WHITE, config.ORANGE, config.YELLOW]), 'size': random.randint(3, 8)})
    elif mode == 'mega_explosion':
        # giga victory fireworks !! 😎
        for _ in range(120):
            rand_color = random.choice([config.GREEN, config.BLUE, config.YELLOW, config.WHITE, config.ORANGE, (255, 100, 200)])
            particles.append({'x': x, 'y': y, 'vx': random.uniform(-15, 15), 'vy': random.uniform(-15, 15), 'life': random.randint(40, 80), 'color': rand_color, 'size': random.randint(5, 15)})

def draw_shadow_text(surface, text, font, color, x, y, shadow_color=(0,0,0), offset=2):
    t_shadow = font.render(text, True, shadow_color)
    surface.blit(t_shadow, (x + offset, y + offset))
    t_clear = font.render(text, True, color)
    surface.blit(t_clear, (x, y))

def draw_waste(surface, w_type, x, y, angle=0):
    # small drawing function to model our waste with style ! (Alpha surface to be able to superimpose)
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    if w_type == 'Plastic':
        # our best water bottle: body + thin neck + blue label + orange cap on top
        pygame.draw.rect(surf, config.YELLOW, (6, 12, 18, 18), border_radius=4)
        pygame.draw.rect(surf, config.YELLOW, (11, 6, 8, 6))
        pygame.draw.rect(surf, config.ORANGE, (10, 3, 10, 4), border_radius=1) # the little cap lol
        pygame.draw.rect(surf, config.BLUE, (6, 16, 18, 6))
    elif w_type == 'Paper':
        # crumpled paper ball (I trick heavily by stacking random little circles)
        pygame.draw.circle(surf, config.BLUE, (15, 15), 11)
        pygame.draw.circle(surf, (200, 220, 255), (12, 12), 7)
        pygame.draw.circle(surf, (150, 180, 220), (18, 17), 5)
        # fake scribbled pen marks
        pygame.draw.line(surf, config.BLACK, (10, 10), (18, 20), 2)
        pygame.draw.line(surf, config.BLACK, (12, 20), (16, 12), 2)
    elif w_type == 'Glass':
        # sick little green glass bottle soda style
        pygame.draw.rect(surf, config.GREEN, (5, 13, 20, 17), border_radius=3)
        pygame.draw.rect(surf, config.GREEN, (11, 2, 8, 11))
        # a little ellipse stroke calmly to make a shine effect
        pygame.draw.ellipse(surf, (150, 255, 150), (7, 15, 4, 10))
        # the blank label right in the center
        pygame.draw.rect(surf, (200, 200, 200), (5, 18, 20, 8))
        
    # # We rotate the surface here! This makes the waste actually spin while flying to look super premium!
    rotated_surf = pygame.transform.rotate(surf, angle)
    new_rect = rotated_surf.get_rect(center=(int(x), int(y)))
    surface.blit(rotated_surf, new_rect.topleft)

# We initialize the base decor
init_decor(levels[0]['decor_type'])

# Characteristics of the dynamic obstacle
dynamic_obstacle = {'x': 400, 'y': 250, 'width': 90, 'height': 35, 'speed': 4}

# Initialization of game variables: score, lives...
game_state = 'MENU'
score = 0
lives = config.INITIAL_LIVES
level_index = 0
throw_angle = 45
throw_force = 15
alert_message = ""  # display message
alert_timer = 0  # Display duration

# NEW VFX VARIABLES
screen_shake = 0
slow_mo_timer = 0
floating_texts = []
flight_path = []
ui_anim_timer = 0

# random waste at the beginning
def create_new_waste():
    t = random.choice(['Plastic', 'Paper', 'Glass'])
    c = config.YELLOW if t == 'Plastic' else config.BLUE if t == 'Paper' else config.GREEN
    # # Giving it an angle and rot_speed so nothing looks static, it's way more organic this way!
    return {'x': 80, 'y': 500, 'vx': 0, 'vy': 0, 'radius': 12, 'type': t, 'color': c, 'in_flight': False, 'angle': 0, 'rot_speed': random.uniform(-15, 15)}

def start_level(idx):
    global game_state, score, lives, level_index, waste, particles, alert_timer
    level_index = idx
    score = 0
    lives = config.INITIAL_LIVES
    
    if levels[level_index]['name'] == 'Efrei':
        game_state = 'EFREI_INTRO'
        alert_timer = 180 # 3 seconds intro showing the photo!
    else:
        game_state = 'GAME'
        
    waste = create_new_waste()
    init_decor(levels[level_index]['decor_type'])
    particles.clear()
    flight_path.clear()
    floating_texts.clear()
    global ui_anim_timer
    ui_anim_timer = 0

waste = create_new_waste()

running = True
while running:

   # event management
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # quit
            running = False

        if event.type == pygame.KEYDOWN:  # If a key is pressed
            if game_state == 'MENU':
                if event.key == pygame.K_1 and unlocked_levels_max >= 0: start_level(0)
                elif event.key == pygame.K_2 and unlocked_levels_max >= 1: start_level(1)
                elif event.key == pygame.K_3 and unlocked_levels_max >= 2: start_level(2)
                elif event.key == pygame.K_4 and unlocked_levels_max >= 3: start_level(3)
                elif event.key == pygame.K_5 and unlocked_levels_max >= 4: start_level(4)
                elif event.key == pygame.K_6 and unlocked_levels_max >= 5: start_level(5)

            elif game_state == 'GAME':
                if event.key == pygame.K_SPACE and not waste['in_flight']:
                    # Calculates X and Y speed based on force and angle
                    waste['vx'], waste['vy'] = physics.calculate_initial_velocity(throw_force, throw_angle)
                    waste['in_flight'] = True
                    if snd_throw: snd_throw.play()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    game_state = 'MENU' # Quit ongoing level

            elif game_state in ['VICTORY', 'GAMEOVER', 'TRANSITION']:
                if event.key == pygame.K_r or event.key == pygame.K_RETURN:  # R key to return to menu
                    game_state = 'MENU'

    # LOGIC UPDATE: Movement calculations, collisions
    if game_state == 'GAME':
        level = levels[level_index]

        # Bins moving in harder levels!
        if level_index in [3, 4, 5]:
            bin_speed = 1 if level_index == 3 else 3 if level_index == 4 else 6
            for b in bins:
                if 'dir' not in b: b['dir'] = random.choice([-1, 1])
                b['x'] += bin_speed * b['dir']
                if b['x'] < 300: b['dir'] = 1
                elif b['x'] + b['width'] > 800: b['dir'] = -1

        # Obstacle moving
        if level['obstacle']:
            dynamic_obstacle['x'] += dynamic_obstacle['speed']
            if dynamic_obstacle['x'] > 720 or dynamic_obstacle['x'] < 300:  # Bounces on invisible edges
                dynamic_obstacle['speed'] *= -1

        # Waste movement if it is thrown
        if waste['in_flight']:
            waste['x'], waste['y'], waste['vx'], waste['vy'] = physics.update_position(
                waste['x'], waste['y'], waste['vx'], waste['vy'], level['gravity'], level['wind']
            )
            # # Adding a sick spinning effect based on its rotational speed
            waste['angle'] += waste['rot_speed']

            # Flight path recording
            if ui_anim_timer % 2 == 0:
                flight_path.append({'x': waste['x'], 'y': waste['y'], 'life': 20})

            # Particle trail
            create_particles(waste['x'], waste['y'], config.WHITE, 'trail')

            # Collision with the obstacle
            if level['obstacle'] and physics.check_obstacle_collision(waste['x'], waste['y'], dynamic_obstacle):
                waste['vx'] *= -0.8  # Bounce backward
                waste['vy'] = random.uniform(-12, -7)  # Random upward projection
                if level['obstacle'] == 'DE':
                    floating_texts.append({'text': "0/20!", 'x': waste['x'], 'y': waste['y'], 'color': config.RED, 'timer': 60, 'alpha': 255})
                else:
                    floating_texts.append({'text': f"-1 LIFE", 'x': waste['x'], 'y': waste['y'], 'color': config.RED, 'timer': 60, 'alpha': 255})
                screen_shake = 15 # Bam! Screen shake when you hit a hazard
                slow_mo_timer = 20 # Slowmo on hazard hit for drama
                if snd_error: snd_error.play()

            # if the waste goes off screen
            if waste['y'] > 600 or waste['x'] > 800 or waste['x'] < 0:
                lives -= 1
                alert_message = "MISSED!"
                alert_timer = 60
                waste = create_new_waste()
                if snd_error: snd_error.play()
                if lives <= 0: game_state = 'GAMEOVER'

            # Verification of collisions with bins
            for b_idx in bins:
                if physics.check_collision(waste['x'], waste['y'], waste['radius'], b_idx):
                    if b_idx['type'] == waste['type']:  # Right bin !
                        score += 1
                        if level['name'] == 'Efrei':
                            floating_texts.append({'text': "+1 LXP", 'x': b_idx['x'], 'y': b_idx['y']-10, 'color': config.GREEN, 'timer': 60, 'alpha': 255})
                        else:
                            floating_texts.append({'text': f"+1 SCORE", 'x': b_idx['x'], 'y': b_idx['y']-10, 'color': config.GREEN, 'timer': 60, 'alpha': 255})
                        create_particles(b_idx['x'] + b_idx['width']//2, b_idx['y'], b_idx['color'], 'explosion')
                        slow_mo_timer = 15 # Drama slowmo when scoring!
                        if snd_score: snd_score.play()
                    else:  # Wrong bin !
                        lives -= 1
                        floating_texts.append({'text': "-1 LIFE", 'x': b_idx['x'], 'y': b_idx['y']-10, 'color': config.RED, 'timer': 60, 'alpha': 255})
                        screen_shake = 15
                        if snd_error: snd_error.play()

                    waste = create_new_waste()

                    if lives <= 0:
                        game_state = 'GAMEOVER'
                    elif score >= level['target_score']:  # Level finished ?
                        if level_index < len(levels) - 1:
                            unlocked_levels_max = max(unlocked_levels_max, level_index + 1)
                            # we start the animation phase before the next level
                            game_state = 'TRANSITION'
                            alert_timer = 120 # anim of about 2 sec to enjoy the explosion
                            # lit epic success explosion in the middle of the screen !!
                            create_particles(config.WIDTH//2, config.HEIGHT//2, config.WHITE, 'mega_explosion')
                        else:
                            game_state = 'VICTORY'
                    break
        else:
            # Aiming controls (when the waste is not yet thrown)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and throw_angle < 90: throw_angle += 1
            if keys[pygame.K_DOWN] and throw_angle > 0: throw_angle -= 1
            if keys[pygame.K_RIGHT] and throw_force < 25: throw_force += 0.3
            if keys[pygame.K_LEFT] and throw_force > 5: throw_force -= 0.3

    # Global logic ticks
    ui_anim_timer += 1
    if screen_shake > 0: screen_shake -= 1
    if slow_mo_timer > 0: slow_mo_timer -= 1
    
    # Update floating texts
    for ft in floating_texts[:]:
        ft['y'] -= 1.5 # Float upwards
        ft['alpha'] -= 4 # Fade out
        ft['timer'] -= 1
        if ft['timer'] <= 0 or ft['alpha'] <= 0:
            floating_texts.remove(ft)
            
    # Update flight paths
    for fp in flight_path[:]:
        fp['life'] -= 1
        if fp['life'] <= 0: flight_path.remove(fp)

    # lil management to pass the anim time without the guy playing
    if game_state == 'TRANSITION':
        if alert_timer > 0:
            alert_timer -= 1

    # Apply screen shake offset dynamically just before display flip
    
    # DISPLAY (Drawing on the screen)
    if game_state == 'MENU':
        # # Giving the menu a sick gradient background so it isn't just pure black!
        draw_gradient(screen, config.BEACH_SKY_TOP, config.BEACH_SKY_BOTTOM)
        
        # # Cool pulsing effect for the title to make it feel alive!
        pulse = math.sin(pygame.time.get_ticks() / 300) * 10
        t_title = font_l.render("ECO THROW", True, config.GREEN)
        
        # # Giant drop shadow for the title to make it pop and look premium
        screen.blit(font_l.render("ECO THROW", True, (0, 50, 0)), (config.WIDTH // 2 - t_title.get_width() // 2 + 4, 84 + pulse))
        screen.blit(t_title, (config.WIDTH // 2 - t_title.get_width() // 2, 80 + pulse))
        
        for i, lvl in enumerate(levels):
            if i <= unlocked_levels_max:
                txt = f"Press [{i+1}] - {lvl['name']} (Score req: {lvl['target_score']})"
                color = config.WHITE
            else:
                txt = f"[{i+1}] - {lvl['name']} (LOCKED)"
                color = (100, 100, 100)
            draw_shadow_text(screen, txt, font_m, color, config.WIDTH // 2 - 250, 200 + i * 50)
            
        # # Little floating waste items on the menu screen to show what the game is about
        draw_waste(screen, 'Plastic', 100, 420 + math.cos(pygame.time.get_ticks()/200)*10, pygame.time.get_ticks()/10)
        draw_waste(screen, 'Glass', 700, 420 + math.sin(pygame.time.get_ticks()/200)*10, -pygame.time.get_ticks()/15)

    # we continue to recreate the image every ms to make the explosion move even in pause
    elif game_state in ['GAME', 'TRANSITION']:
        # Animation and display of background particles (clouds/bubbles)
        for d in decor_bg:
            if level['decor_type'] == 'clouds':
                d['x'] += d['speed']
                if d['x'] > config.WIDTH + 100: d['x'] = -100
            elif level['decor_type'] == 'bubbles':
                d['y'] += d['speed']
                if d['y'] < -20: d['y'] = config.HEIGHT + 20
            elif level['decor_type'] == 'snow':
                d['x'] += d['speed_x']
                d['y'] += d['speed_y']
                if d['y'] > config.HEIGHT:
                    d['y'] = -10
                    d['x'] = random.randint(0, config.WIDTH)

        # Update Particles
        for p in particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                particles.remove(p)

        # Drawing the environment (Sky and Ground) with Gradient
        draw_gradient(screen, level['sky_top'], level['sky_bottom'])
        
        # clean visual design depending on my level
        
        if level['name'] == 'Beach':
            # # Adding a majestic sun with animated rays and a beautiful parasol setup !!
            pygame.draw.circle(screen, (255, 215, 0), (700, 120), 50)
            # Animated sun rays pulsing out smoothly
            ray_pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * 20
            pygame.draw.circle(screen, (255, 140, 0, 100), (700, 120), int(60 + ray_pulse), 5)
            # Distant beautiful purple mountains
            pygame.draw.polygon(screen, (200, 180, 220), [(100, 480), (300, 350), (600, 480)])
            # Animated waves that literally move like real water overlapping !
            wave_offset = (pygame.time.get_ticks() / 30) % 100
            for w in range(-100, 900, 100):
                pygame.draw.ellipse(screen, (0, 150, 220), (w - wave_offset, 460, 150, 50))
                pygame.draw.ellipse(screen, (0, 119, 190), (w - wave_offset + 50, 470, 150, 50))
            # My chill parasol on the sand to fit the summer vibe
            pygame.draw.rect(screen, (150, 100, 50), (120, 380, 8, 140)) # Pole
            pygame.draw.polygon(screen, (255, 50, 50), [(60, 380), (124, 330), (188, 380)]) # Red umbrella part
            pygame.draw.polygon(screen, (255, 255, 255), [(90, 380), (124, 330), (160, 380)]) # White stripes

        elif level['name'] == 'Forest':
            # # Pushed the forest to the max with depth layers and actual foliage shapes
            # Background distant soft trees (depth layer 1)
            for x_tree in [30, 200, 400, 600, 750]:
                pygame.draw.polygon(screen, (40, 80, 40), [(x_tree - 60, 520), (x_tree + 60, 520), (x_tree, 350)])
            # Foreground detailed trees (depth layer 2)
            for x_tree in [100, 300, 500, 700]:
                pygame.draw.rect(screen, (80, 40, 20), (x_tree - 10, 420, 20, 100)) # Trunk
                # Overlapping circles for a bushy leafy organic look !
                pygame.draw.circle(screen, (34, 139, 34), (x_tree, 400), 45)
                pygame.draw.circle(screen, (34, 139, 34), (x_tree - 25, 430), 40)
                pygame.draw.circle(screen, (34, 139, 34), (x_tree + 25, 430), 40)
                pygame.draw.circle(screen, (50, 180, 50), (x_tree, 380), 30) # Highlights
            # Some tall grass popping up at the bottom dynamically
            for x_grass in range(0, 800, 30):
                pygame.draw.polygon(screen, (20, 100, 20), [(x_grass, 520), (x_grass+10, 520), (x_grass+5, 490)])

        elif level['name'] == 'Ocean':
            # # Maxing out the ocean with animated kelp forests and a sunken silhouette
            # Distant sunken submarine silhouette for the mysterious lore
            pygame.draw.ellipse(screen, (10, 20, 30), (500, 450, 200, 60))
            pygame.draw.rect(screen, (10, 20, 30), (560, 420, 40, 30))
            # Waving seaweeds using trigonometry
            for x_kelp in [50, 150, 250, 650, 750]:
                for seg in range(5):
                    # the seaweed bends dynamically with the time! math is crazy!
                    sway = math.sin(pygame.time.get_ticks() / 300 + x_kelp) * 15
                    pygame.draw.ellipse(screen, (0, 150, 80), (x_kelp + sway, 520 - (seg*30), 12, 35))

        elif level['name'] == 'Mountain':
            # # Added extreme parallax feeling with huge backdrop mountains and floating clouds
            # Background dark mountains
            pygame.draw.polygon(screen, (80, 80, 100), [(0, 520), (250, 200), (500, 520)])
            pygame.draw.polygon(screen, (90, 90, 110), [(300, 520), (600, 150), (900, 520)])
            # Foreground detailed mountains
            pygame.draw.polygon(screen, (130, 130, 150), [(100, 520), (450, 280), (800, 520)])
            pygame.draw.polygon(screen, (255, 255, 255), [(450, 280), (510, 320), (460, 330), (420, 300), (390, 320)]) # High detail snowcap
            pygame.draw.polygon(screen, (140, 140, 160), [(-100, 520), (150, 350), (400, 520)])
            pygame.draw.polygon(screen, (255, 255, 255), [(150, 350), (190, 380), (160, 390), (130, 370), (110, 380)])
            # Some robust mountain pines clinging to the cliffs
            for pine in [(120, 420), (180, 480), (600, 450), (700, 480)]:
                pygame.draw.polygon(screen, (20, 60, 30), [(pine[0]-15, pine[1]+30), (pine[0]+15, pine[1]+30), (pine[0], pine[1])])

        elif level['name'] == 'Antarctica':
            # # Icy wonderland pushed to the limit with a glowing igloo and floating icebergs !
            # Distant iceberg floating slowly on the freezing water layer (if we consider it water)
            ice_float = math.sin(pygame.time.get_ticks() / 1000) * 5
            pygame.draw.polygon(screen, (180, 230, 255), [(100, 480+ice_float), (200, 380+ice_float), (350, 480+ice_float)])
            # Detailed Igloo
            pygame.draw.circle(screen, (230, 240, 255), (600, 520), 90) # Dome
            pygame.draw.rect(screen, level['ground'], (510, 520, 180, 90)) # cut bottom half
            # Glowing warm light coming from inside the igloo! So cozy.
            pulse_light = abs(math.sin(pygame.time.get_ticks() / 200)) * 10
            # To draw translucent circles we need a surface because Pygame draw circle alpha is limited on direct screen
            light_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(light_surf, (255, 200, 50, 60), (60, 60), int(40 + pulse_light))
            screen.blit(light_surf, (530, 460))
            # Igloo door
            pygame.draw.circle(screen, (20, 30, 50), (590, 520), 30)
            pygame.draw.rect(screen, level['ground'], (560, 520, 60, 30))
            # Ice blocks brick pattern overlay on the dome!
            for r in range(40, 90, 20):
                pygame.draw.arc(screen, (200, 220, 240), (600-r, 520-r, r*2, r*2), 0, 3.14, 3)
            # A deep blue crack in the foreground ice to show the danger
            pygame.draw.polygon(screen, (50, 150, 250), [(50, 550), (80, 580), (150, 600), (90, 600), (40, 570)])

        elif level['name'] == 'Efrei':
            # # Red brick building on the right
            pygame.draw.rect(screen, (160, 60, 60), (450, 150, 400, 400)) # Bricks
            pygame.draw.rect(screen, (220, 220, 220), (450, 150, 400, 400), 5) # Outline
            for by in range(160, 550, 30):
                pygame.draw.line(screen, (130, 40, 40), (450, by), (800, by), 2)
            # Brick windows
            for wx, wy in [(500, 200), (650, 200), (500, 350), (650, 350)]:
                pygame.draw.rect(screen, (100, 150, 200), (wx, wy, 60, 80))
                pygame.draw.rect(screen, (50, 50, 50), (wx, wy, 60, 80), 3)

            # # Modern Glass building on the left
            pygame.draw.rect(screen, (200, 220, 240), (-50, 200, 350, 350))
            # Grid windows
            for gx in range(-50, 300, 50):
                pygame.draw.line(screen, (100, 120, 150), (gx, 200), (gx, 550), 3)
            for gy in range(200, 550, 50):
                pygame.draw.line(screen, (100, 120, 150), (-50, gy), (300, gy), 3)
            
            # THE LOGO ON THE GLASS !!
            draw_shadow_text(screen, "#ONLY EFREI PARIS", font_l, (0, 150, 255), 30, 350)
            
            # Cool tree supports in the middle
            for tx in [300, 380]:
                pygame.draw.rect(screen, (139, 100, 80), (tx, 450, 12, 70))
                pygame.draw.polygon(screen, (40, 120, 40), [(tx - 30, 450), (tx + 42, 450), (tx + 6, 380)])


        # we display the lil decorative fixed bg clouds
        for d in decor_bg:
            if level['decor_type'] == 'clouds':
                # stretched circles = govt cloud... lol
                pygame.draw.ellipse(screen, (255, 255, 255), (int(d['x']), int(d['y']), int(d['size']*2), int(d['size'])))
            elif level['decor_type'] == 'bubbles':
                # little empty ellipse = little bubble under water
                pygame.draw.circle(screen, (255, 255, 255), (int(d['x']), int(d['y'])), d['size'], 1)
            elif level['decor_type'] == 'snow':
                # white circles for snow
                pygame.draw.circle(screen, (255, 255, 255), (int(d['x']), int(d['y'])), d['size'])

        # solid bottom block (earth etc..)
        pygame.draw.rect(screen, level['ground'], (0, 520, 800, 80))
        # I force the limit to visually detach... it looks good
        pygame.draw.line(screen, (0,0,0), (0, 520), (800, 520), 4)

        # anim loop for the particles that fly during the throws
        for p in particles:
            p['vy'] += 0.5 # GRAVITY ON PARTICLES!
            p['x'] += p['vx']
            p['y'] += p['vy']
            # we trick on the radius by testing its age (life / 30 * init size)
            t = max(1, int(p['size'] * (p['life'] / 30)))
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), t)
            
        # Draw flight path trail
        for fp in flight_path:
            fp_alpha = int(255 * (fp['life'] / 20))
            fp_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(fp_surf, (255, 255, 255, fp_alpha), (5, 5), max(1, int(4 * (fp['life']/20))))
            screen.blit(fp_surf, (int(fp['x'] - 5), int(fp['y'] - 5)))

        # Drawing the animated obstacle (if present)
        if level['obstacle'] == 'shark':
            # Shark moving up and down slightly
            bobbing = math.sin(pygame.time.get_ticks() / 200) * 5
            # Body color
            shark_color = (100, 110, 130)
            
            # Shadow on the ground
            pygame.draw.ellipse(screen, (0, 0, 0, 50), (dynamic_obstacle['x'] + 10, dynamic_obstacle['y'] + 50, dynamic_obstacle['width'], dynamic_obstacle['height'] // 2))
            
            # Draw tail fin (flips direction based on speed)
            dir = 1 if dynamic_obstacle['speed'] > 0 else -1
            tail_x = dynamic_obstacle['x'] if dir == 1 else dynamic_obstacle['x'] + dynamic_obstacle['width']
            tail_y = dynamic_obstacle['y'] + dynamic_obstacle['height']//2 + bobbing
            pygame.draw.polygon(screen, shark_color, [(tail_x, tail_y), (tail_x - dir*20, tail_y - 15), (tail_x - dir*20, tail_y + 15)])
            
            # Body
            pygame.draw.ellipse(screen, shark_color, (dynamic_obstacle['x'], dynamic_obstacle['y'] + bobbing, dynamic_obstacle['width'], dynamic_obstacle['height']))
            
            # Dorsal fin
            pygame.draw.polygon(screen, shark_color, [(dynamic_obstacle['x'] + 30, dynamic_obstacle['y'] + bobbing + 10), (dynamic_obstacle['x'] + 50, dynamic_obstacle['y'] + bobbing + 10), (dynamic_obstacle['x'] + 40, dynamic_obstacle['y'] + bobbing - 15)])
            
            # Eye
            eye_x = dynamic_obstacle['x'] + 65 if dir == 1 else dynamic_obstacle['x'] + 25
            pygame.draw.circle(screen, config.BLACK, (int(eye_x), int(dynamic_obstacle['y'] + bobbing + 12)), 3)
            
            draw_shadow_text(screen, "SHARK!", font_s, config.RED, dynamic_obstacle['x'] + 10, dynamic_obstacle['y'] + bobbing - 25)

        elif level['obstacle'] == 'eagle':
            # Eagle hovering and flapping
            flap = math.sin(pygame.time.get_ticks() / 150) * 15
            bobbing = math.sin(pygame.time.get_ticks() / 200) * 8
            eagle_color = (139, 69, 19) # Brown
            head_color = (255, 255, 255)
            
            # Shadow on the ground
            pygame.draw.ellipse(screen, (0, 0, 0, 50), (dynamic_obstacle['x'] + 10, dynamic_obstacle['y'] + 50, dynamic_obstacle['width'], dynamic_obstacle['height'] // 2))
            
            dir = 1 if dynamic_obstacle['speed'] > 0 else -1
            
            # Wings
            wing_x = dynamic_obstacle['x'] + dynamic_obstacle['width'] // 2
            wing_y = dynamic_obstacle['y'] + 10 + bobbing
            pygame.draw.polygon(screen, eagle_color, [(wing_x - 10, wing_y + 10), (wing_x + 10, wing_y + 10), (wing_x - dir * 15, wing_y - flap - 20)])
            
            # Body
            pygame.draw.ellipse(screen, eagle_color, (dynamic_obstacle['x'], dynamic_obstacle['y'] + bobbing, dynamic_obstacle['width'] - 20, dynamic_obstacle['height']))
            
            # Head (white like a bald eagle)
            head_x = dynamic_obstacle['x'] + dynamic_obstacle['width'] - 30 if dir == 1 else dynamic_obstacle['x'] - 5
            pygame.draw.ellipse(screen, head_color, (head_x, dynamic_obstacle['y'] + bobbing, 30, 25))
            
            # Beak
            beak_x = head_x + 25 if dir == 1 else head_x
            pygame.draw.polygon(screen, config.YELLOW, [(head_x + 15, dynamic_obstacle['y'] + bobbing + 10), (beak_x + 15 * dir, dynamic_obstacle['y'] + bobbing + 15), (head_x + 15, dynamic_obstacle['y'] + bobbing + 20)])
            
            # Eye
            eye_x = head_x + 18 if dir == 1 else head_x + 12
            pygame.draw.circle(screen, config.BLACK, (int(eye_x), int(dynamic_obstacle['y'] + bobbing + 10)), 3)
            
            draw_shadow_text(screen, "EAGLE!", font_s, config.RED, dynamic_obstacle['x'] + 10, dynamic_obstacle['y'] + bobbing - 25)

        elif level['obstacle'] == 'penguin':
            # Penguin sliding on its belly
            penguin_color = (15, 15, 20)
            belly_color = (255, 255, 255)
            
            # Shadow
            pygame.draw.ellipse(screen, (0, 0, 0, 50), (dynamic_obstacle['x'] + 5, dynamic_obstacle['y'] + 45, dynamic_obstacle['width'] - 10, dynamic_obstacle['height'] // 2))
            
            dir = 1 if dynamic_obstacle['speed'] > 0 else -1
            bobbing = math.sin(pygame.time.get_ticks() / 150) * 3
            
            # Body sliding
            pygame.draw.ellipse(screen, penguin_color, (dynamic_obstacle['x'], dynamic_obstacle['y'] + 10 + bobbing, dynamic_obstacle['width'], dynamic_obstacle['height']))
            pygame.draw.ellipse(screen, belly_color, (dynamic_obstacle['x'] + 10, dynamic_obstacle['y'] + 15 + bobbing, dynamic_obstacle['width'] - 20, dynamic_obstacle['height'] - 10))
            
            # Flipper flapping a bit
            flap = math.sin(pygame.time.get_ticks() / 100) * 8
            flip_x = dynamic_obstacle['x'] + dynamic_obstacle['width']//2
            flip_y = dynamic_obstacle['y'] + 20 + bobbing
            pygame.draw.polygon(screen, penguin_color, [(flip_x-10, flip_y), (flip_x+10, flip_y), (flip_x - dir*20, flip_y - flap - 5)])

            # Head
            head_x = dynamic_obstacle['x'] + dynamic_obstacle['width'] - 20 if dir == 1 else dynamic_obstacle['x'] - 5
            pygame.draw.ellipse(screen, penguin_color, (head_x, dynamic_obstacle['y'] + 5 + bobbing, 25, 25))
            
            # Beak
            beak_x = head_x + 25 if dir == 1 else head_x
            pygame.draw.polygon(screen, config.ORANGE, [(head_x + 15, dynamic_obstacle['y'] + 15 + bobbing), (beak_x + 10 * dir, dynamic_obstacle['y'] + 18 + bobbing), (head_x + 15, dynamic_obstacle['y'] + 21 + bobbing)])
            
            # Eye
            eye_x = head_x + 18 if dir == 1 else head_x + 12
            pygame.draw.circle(screen, config.WHITE, (int(eye_x), int(dynamic_obstacle['y'] + 12 + bobbing)), 4)
            pygame.draw.circle(screen, config.BLACK, (int(eye_x + dir), int(dynamic_obstacle['y'] + 12 + bobbing)), 2)

            draw_shadow_text(screen, "PENGUIN!", font_s, config.BLUE, dynamic_obstacle['x'] + 10, dynamic_obstacle['y'] + bobbing - 25)

        elif level['obstacle'] == 'DE':
            # Drawing a floating sheet of paper (Exam copy)
            bobbing = math.sin(pygame.time.get_ticks() / 150) * 8
            # Rotating the paper back and forth
            angle = math.sin(pygame.time.get_ticks() / 200) * 15
            paper_w, paper_h = 60, 80
            p_surf = pygame.Surface((paper_w, paper_h), pygame.SRCALPHA)
            pygame.draw.rect(p_surf, (250, 250, 240), (0, 0, paper_w, paper_h)) # Paper
            pygame.draw.rect(p_surf, (220, 50, 50), (0, 0, paper_w, paper_h), 3) # Red border
            
            # Text lines on paper
            for l_y in range(25, paper_h - 10, 10):
                pygame.draw.line(p_surf, (150, 150, 150), (10, l_y), (paper_w - 10, l_y), 2)
                
            # DE Title
            t_de = font_s.render("DE", True, (200, 50, 50))
            p_surf.blit(t_de, (5, 5))
            
            # Grade text
            t_grade = font_s.render("0/20", True, (220, 20, 20))
            p_surf.blit(t_grade, (5, paper_h - 25))
            
            rotated_p = pygame.transform.rotate(p_surf, angle)
            new_rect = rotated_p.get_rect(center=(int(dynamic_obstacle['x'] + dynamic_obstacle['width']//2), int(dynamic_obstacle['y'] + bobbing + 20)))
            screen.blit(rotated_p, new_rect.topleft)

        # ---- Drawing our superb urban bins -----
        # a big single layer to use transp/SRCALPHA chill (for shadows !)
        layer_bins = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        for b_idx in bins:
            # # Adding a soft colored glow under each bin to make them stand out beautifully!
            pygame.draw.ellipse(layer_bins, (*b_idx['color'][:3], 80), (b_idx['x'] - 20, b_idx['y'] + b_idx['height'] - 10, b_idx['width'] + 40, 20))
            
            # 1. Big shadow behind for the incrrr volume effect
            pygame.draw.rect(layer_bins, (0, 0, 0, 100), (b_idx['x'] + 10, b_idx['y'] + 10, b_idx['width'], b_idx['height']), border_radius=8)
            # 2. The massive bin in block with its real colors
            pygame.draw.rect(layer_bins, b_idx['color'], (b_idx['x'], b_idx['y'], b_idx['width'], b_idx['height']), border_radius=8)
            # 3. Blackened lines for the bin's stripes (it really makes it look like a park bin like that)
            for x_ray in [20, 35, 50]:
                pygame.draw.line(layer_bins, (0, 0, 0, 60), (b_idx['x'] + x_ray, b_idx['y'] + 25), (b_idx['x'] + x_ray, b_idx['y'] + b_idx['height'] - 15), 4)
            # 4. The big gray lid closely stuck to the top of the bottle, sticking out
            pygame.draw.rect(layer_bins, (70, 70, 70), (b_idx['x'] - 5, b_idx['y'] - 10, b_idx['width'] + 10, 20), border_radius=6)
            pygame.draw.rect(layer_bins, (200, 200, 200), (b_idx['x'] - 5, b_idx['y'] - 10, b_idx['width'] + 10, 5), border_radius=6) # small extra sun glare effect
            # 5. Protective border in stylized black
            pygame.draw.rect(layer_bins, config.BLACK, (b_idx['x'], b_idx['y'], b_idx['width'], b_idx['height']), 3, border_radius=8)
            pygame.draw.rect(layer_bins, config.BLACK, (b_idx['x'] - 5, b_idx['y'] - 10, b_idx['width'] + 10, 20), 2, border_radius=6)
            
        # blit of our master piece on the canvas
        screen.blit(layer_bins, (0,0))
        
        # And a nice textual addition for each bin so we know what to throw in ^^
        for b_idx in bins:
            txt_surface = font_s.render(b_idx['type'], True, config.WHITE)
            txt_w = txt_surface.get_width()
            draw_shadow_text(screen, b_idx['type'], font_s, config.WHITE, b_idx['x'] + b_idx['width'] // 2 - txt_w // 2, b_idx['y'] + 45)

        # Drawing the aiming trajectory (before the throw I won't tell u why)
        if not waste['in_flight']:
            sim_x, sim_y = waste['x'], waste['y']
            sim_vx, sim_vy = physics.calculate_initial_velocity(throw_force, throw_angle)
            # Im dumping 150 frames of physics calculation to predict its trajec !!!
            for i in range(150): 
                sim_x, sim_y, sim_vx, sim_vy = physics.update_position(sim_x, sim_y, sim_vx, sim_vy, level['gravity'], level['wind'])
                if i % 4 == 0:
                    pygame.draw.circle(screen, (255, 255, 255, 180), (int(sim_x), int(sim_y)), 3)
                # tiny safety if the ball hits the edge to avoid crashing it far lmaooo
                if sim_y > 600 or sim_x > 800 or sim_x < 0:
                    break

        # Dynamic power gauge (CIRCULAR sleek UI!)
        if not waste['in_flight']:
            gauge_color = config.GREEN if throw_force <= 10 else config.ORANGE if throw_force <= 20 else config.RED
            arc_rect = (int(waste['x'] - 40), int(waste['y'] - 40), 80, 80)
            # Full backing circle
            pygame.draw.arc(screen, (50, 50, 50, 150), arc_rect, 0, 6.28, 8)
            # Power filled arc
            fill_angle = max(0.1, (throw_force / 25) * 6.28)
            pygame.draw.arc(screen, gauge_color, arc_rect, 1.57 - fill_angle/2, 1.57 + fill_angle/2, 8)
            draw_shadow_text(screen, "POWER", font_s, gauge_color, int(waste['x'] - 25), int(waste['y'] + 45))

        # Full custom drawing of our HD waste instead of old balls
        draw_waste(screen, waste['type'], waste['x'], waste['y'], waste['angle'])

        # UI Glassmorphism (Information Panel)
        # Easing bouncing effect!
        ui_y_offset = (math.exp(-ui_anim_timer/10) * math.cos(ui_anim_timer/3)) * -100
        panel_y = 10 + ui_y_offset
        
        panel = pygame.Surface((260, 140), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 140), (0, 0, 260, 140), border_radius=15)
        pygame.draw.rect(panel, (255, 255, 255, 50), (0, 0, 260, 140), 2, border_radius=15)
        screen.blit(panel, (10, panel_y))
        
        draw_shadow_text(screen, f"Location: {level['name']}", font_s, config.WHITE, 20, panel_y + 10)
        draw_shadow_text(screen, f"Score: {score}/{level['target_score']} | Lives: {lives}", font_s, config.WHITE, 20, panel_y + 40)
        
        wind_color = (150, 200, 255) if level['wind'] != 0 else (200, 200, 200)
        draw_shadow_text(screen, f"Wind: {'<-- ' if level['wind'] < 0 else '--> ' if level['wind'] > 0 else 'None '}{abs(level['wind']):.2f}", font_s, wind_color, 20, panel_y + 70)
        draw_shadow_text(screen, f"OBJECT: {waste['type']}", font_m, waste['color'], 20, panel_y + 95)

        # Render Floating Texts (Damage / Scores)
        for ft in floating_texts:
            t_surf = font_m.render(ft['text'], True, ft['color'])
            alpha_surf = pygame.Surface(t_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, max(0, min(255, int(ft['alpha'])))))
            t_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            t_shadow = font_m.render(ft['text'], True, (0,0,0))
            t_shadow.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            screen.blit(t_shadow, (ft['x'] + 2, ft['y'] + 2))
            screen.blit(t_surf, (ft['x'], ft['y']))

        # Display of temporary Pop-Up messages
        if alert_timer > 0 and alert_message != "" and game_state == 'GAME':
            color = config.GREEN if "WELL" in alert_message or "LEVEL" in alert_message else config.RED
            t_surface = font_l.render(alert_message, True, color)
            txt_w = t_surface.get_width()
            
            # Box behind the popup
            bg_rect = pygame.Surface((txt_w + 40, 80), pygame.SRCALPHA)
            pygame.draw.rect(bg_rect, (0, 0, 0, 180), (0, 0, txt_w + 40, 80), border_radius=20)
            screen.blit(bg_rect, (config.WIDTH // 2 - txt_w // 2 - 20, 260))
            
            draw_shadow_text(screen, alert_message, font_l, color, config.WIDTH // 2 - txt_w // 2, 270)
            alert_timer -= 1

        # animated final display when the next level pops !
        if game_state == 'TRANSITION':
            # nice fade to darken the background = beautiful contrast !!
            veil = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(veil, (0, 0, 0, 150), (0,0,config.WIDTH,config.HEIGHT))
            screen.blit(veil, (0,0))
            
            txt = "LEVEL CLEARED!"
            t_surface = font_l.render(txt, True, config.YELLOW)
            x_txt = config.WIDTH // 2 - t_surface.get_width() // 2
            # gently raises the text thanks to my timer hehe 
            y_txt = 250 - (120 - alert_timer)
            draw_shadow_text(screen, txt, font_l, config.YELLOW, x_txt, y_txt, offset=4)
            draw_shadow_text(screen, "Press 'R' or 'ENTER' to return to menu", font_m, config.WHITE, config.WIDTH // 2 - 280, 350)

    elif game_state == 'EFREI_INTRO':
        alert_timer -= 1
        screen.blit(img_efrei, (0,0))
        # Draw a little text over the image
        t_efrei = font_l.render("ENTERING EFREI CAMPUS...", True, config.YELLOW)
        draw_shadow_text(screen, "ENTERING EFREI CAMPUS...", font_l, config.YELLOW, config.WIDTH // 2 - t_efrei.get_width() // 2, 500, (0,0,0), 4)
        if alert_timer <= 0:
            game_state = 'GAME'

    # End screens: Victory and Defeat
    elif game_state == 'GAMEOVER':
        # # Dark transparent overlay instead of solid color to keep the dead level visible behind in shame
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (40, 0, 0, 200), (0,0,config.WIDTH,config.HEIGHT))
        screen.blit(overlay, (0,0))
        
        t_msg = font_l.render("GAME OVER", True, config.RED)
        draw_shadow_text(screen, "GAME OVER", font_l, config.RED, config.WIDTH // 2 - t_msg.get_width() // 2, 200, (0,0,0), 4)
        draw_shadow_text(screen, "Press 'R' to return to Menu...", font_m, (200, 200, 200), config.WIDTH // 2 - 200, 350)

    elif game_state == 'VICTORY':
        # # Nice green overlay for the win screen!
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 40, 0, 200), (0,0,config.WIDTH,config.HEIGHT))
        screen.blit(overlay, (0,0))
        
        # # Rotating sunbeams in the background just for the flex. Pygame makes this so easy with polygons
        center = (config.WIDTH//2, config.HEIGHT//2)
        for i in range(12):
            angle_beam = pygame.time.get_ticks()/100 + (i * 30)
            end_x = center[0] + math.cos(math.radians(angle_beam)) * 1000
            end_y = center[1] + math.sin(math.radians(angle_beam)) * 1000
            pygame.draw.polygon(screen, (20, 80, 20, 100), [(center[0], center[1]), (end_x, end_y), (center[0] + math.cos(math.radians(angle_beam + 10))*1000, center[1] + math.sin(math.radians(angle_beam + 10))*1000)])
            
        t_msg = font_l.render("PLANET SAVED!", True, config.GREEN)
        draw_shadow_text(screen, "PLANET SAVED!", font_l, config.GREEN, config.WIDTH // 2 - t_msg.get_width() // 2, 200, (0,0,0), 4)
        draw_shadow_text(screen, "Press 'R' to return to Menu, HERO!", font_m, config.WHITE, config.WIDTH // 2 - 250, 350)


    # Screen shake application!
    if screen_shake > 0:
        shake_x = random.randint(-screen_shake, screen_shake)
        shake_y = random.randint(-screen_shake, screen_shake)
        surf_copy = screen.copy()
        screen.fill((0,0,0)) # clear screen before redrawing offset
        screen.blit(surf_copy, (shake_x, shake_y))

    pygame.display.flip()  # Update the whole screen with what we've drawn
    
    # Slowmo applied directly by cutting framerate
    target_fps = 15 if slow_mo_timer > 0 else config.FPS
    clock.tick(target_fps)  # Wait the necessary time to stay at target FPS

pygame.quit()