# eco_shooter.py
import pygame
from os.path import join, exists
from random import randint, uniform, choice

# ---------- Cấu hình chung ----------
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FPS = 60

# Màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 150, 0)
MENU_BLUE = (0, 100, 150)
BG_COLOR = (58, 46, 63)
CYAN = (0, 255, 255)
YELLOW = (240, 220, 40)

ASSETS_DIR = "images"
HIGH_SCORE_FILE = "highscore.txt"

# ---------- Helper: load image/sound with fallback ----------
def load_image(path, size=None):
    try:
        surf = pygame.image.load(path).convert_alpha()
        if size:
            surf = pygame.transform.smoothscale(surf, size)
        return surf
    except Exception:
        # fallback: create simple placeholder
        w, h = size if size else (40, 40)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (150, 150, 150), surf.get_rect(), border_radius=8)
        pygame.draw.line(surf, (100,100,100), (0,0),(w,h),2)
        return surf

def load_sound(path):
    try:
        snd = pygame.mixer.Sound(path)
        return snd
    except Exception:
        # return object with play() method that does nothing
        class Dummy:
            def play(self, *a, **k): pass
            def set_volume(self, *a, **k): pass
        return Dummy()

# ---------- Sprites ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, groups, surf=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)

        # Surface: nếu có file thì dùng, không thì vẽ shape
        if surf:
            self.image = surf
        else:
            surf = pygame.Surface((64, 48), pygame.SRCALPHA)
            pygame.draw.polygon(surf, GREEN, [(32,0),(0,48),(64,48)])
            self.image = surf

        self.original_image = self.image
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 100))
        self.direction = pygame.Vector2()
        self.speed = 360  # px / s
        self.lives = 5
        self.shield = False
        self.shield_time = 0
        self.shield_duration = 5000  # ms

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 10  # ms

        # mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def shield_timer(self):
        if self.shield:
            current_time = pygame.time.get_ticks()
            if current_time - self.shield_time >= self.shield_duration:
                self.shield = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = pygame.Vector2(dx, dy)
        if self.direction.length() != 0:
            self.direction = self.direction.normalize()
        pos = pygame.Vector2(self.rect.center)
        pos += self.direction * self.speed * dt

        # giới hạn trong màn hình
        pos.x = max(self.rect.width // 2, min(WINDOW_WIDTH - self.rect.width // 2, pos.x))
        pos.y = max(self.rect.height // 2, min(WINDOW_HEIGHT - self.rect.height // 2, pos.y))

        self.rect.center = (round(pos.x), round(pos.y))
        self.laser_timer()
        self.shield_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)

        if surf:
            self.image = surf
        else:
            size = randint(1,3)
            surf = pygame.Surface((size,size), pygame.SRCALPHA)
            pygame.draw.circle(surf, WHITE, (size//2,size//2), size//2)
            self.image = surf
        self.rect = self.image.get_rect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        self.speed = randint(10, 60)

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = 0
            self.rect.centerx = randint(0, WINDOW_WIDTH)

class Laser(pygame.sprite.Sprite):
    """ Player's laser (goes up) """
    def __init__(self, surf, pos, groups):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 700

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()

class BossBullet(pygame.sprite.Sprite):
    """ Boss's projectile (goes down) """
    def __init__(self, size, pos, groups):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 60, 60), surf.get_rect(), border_radius=3)
        self.image = surf
        self.rect = self.image.get_rect(midtop=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 360

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Pollution(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups, difficulty):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)

        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(0, 1)
        self.speed = randint(180, 300) + difficulty * 30
        self.rotation = 0
        self.rotation_speed = randint(-120, 120)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # di chuyển xuống
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT + 100:
            self.kill()
            return
        # quay animation
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        try:
            self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            pass

class GreenItem(pygame.sprite.Sprite):
    def __init__(self, pos, groups, difficulty):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)

        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, GREEN, (size // 2, size // 2), size // 2)
        pygame.draw.circle(surf, (0,120,0), (size // 2, size // 2), size // 2, 3)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.speed = randint(130, 230) + difficulty * 10
        self.mask = pygame.mask.from_surface(self.image)
        subtypes = ['reusable_bag', 'water_bottle', 'plant', 'solar_panel', 'recycling_bin']
        self.subtype = choice(subtypes)

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT + 50:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups, sound=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)

        self.frames = frames or []
        self.frame_index = 0.0
        if self.frames:
            self.image = self.frames[0]
        else:
            # fallback small circle
            surf = pygame.Surface((40,40), pygame.SRCALPHA)
            pygame.draw.circle(surf, YELLOW, (20,20), 20)
            self.image = surf
        self.rect = self.image.get_rect(center=pos)
        try:
            if sound:
                sound.play()
        except Exception:
            pass

    def update(self, dt):
        if not self.frames:
            # no frames, auto kill quickly
            self.frame_index += 10 * dt
            if self.frame_index > 1:
                self.kill()
            return
        self.frame_index += 24 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

# ---------- Boss cuối ----------
class Boss(pygame.sprite.Sprite):
    def __init__(self, groups, frames=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        # tạo surface nếu không có ảnh boss
        if frames and len(frames):
            self.original_image = frames[0]
            self.frames = frames
            self.image = frames[0]
            self.anim_index = 0.0
        else:
            self.original_image = pygame.Surface((260,120), pygame.SRCALPHA)
            pygame.draw.ellipse(self.original_image, (180,30,30), self.original_image.get_rect())
            self.image = self.original_image
            self.frames = None
            self.anim_index = 0.0

        self.rect = self.image.get_rect(midtop=(WINDOW_WIDTH//2, -150))
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 40
        self.max_health = 40
        self.speed = 120
        self.direction = pygame.Vector2(1,0)
        self.entered = False
        self.shoot_timer = pygame.time.get_ticks()
        self.shoot_interval = 1200  # ms
        self.spawn_pollution_timer = pygame.time.get_ticks()
        self.spawn_pollution_interval = 2000

    def update(self, dt):
        # vào màn hình rồi di chuyển ngang
        if not self.entered:
            self.rect.y += 80 * dt
            if self.rect.top >= 40:
                self.entered = True
        else:
            self.rect.x += self.direction.x * self.speed * dt
            if self.rect.left <= 40:
                self.rect.left = 40
                self.direction.x *= -1
            if self.rect.right >= WINDOW_WIDTH - 40:
                self.rect.right = WINDOW_WIDTH - 40
                self.direction.x *= -1

            # animation nếu có frames
            if self.frames:
                self.anim_index += 6 * dt
                self.image = self.frames[int(self.anim_index) % len(self.frames)]
                self.rect = self.image.get_rect(center=self.rect.center)

        # update mask
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            pass

    def shoot(self, spawn_fn):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = now
            # bắn 3 projectiles xuống
            centers = [self.rect.midbottom,
                       (self.rect.centerx - 40, self.rect.bottom - 10),
                       (self.rect.centerx + 40, self.rect.bottom - 10)]
            for c in centers:
                spawn_fn(c)

    def spawn_pollution(self, spawn_fn, difficulty):
        now = pygame.time.get_ticks()
        if now - self.spawn_pollution_timer >= max(600, self.spawn_pollution_interval - difficulty*50):
            self.spawn_pollution_timer = now
            x = randint(self.rect.left+20, self.rect.right-20)
            spawn_fn((x, self.rect.bottom + 10), difficulty)

# ---------- Utils: high score ----------
def load_highscore():
    try:
        if exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
    except Exception:
        pass
    return 0

def save_highscore(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(int(score)))
    except Exception:
        pass

# ---------- Game setup ----------
pygame.init()
pygame.mixer.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Eco Shooter - Finished Version")
clock = pygame.time.Clock()

# Load assets (try/catch)
# Images
player_img = None
meteor_img = None
star_img = None
laser_img = None
explosion_frames = []
boss_frames = None

try:
    player_img = load_image(join(ASSETS_DIR, "player.png"), (64,48))
    meteor_img = load_image(join(ASSETS_DIR, "meteor.png"), (64,64))
    star_img = load_image(join(ASSETS_DIR, "star.png"), (3,3))
    laser_img = load_image(join(ASSETS_DIR, "laser.png"), (8,28))
    # explosion frames
    for i in range(21):
        p = join(ASSETS_DIR, "explosion", f"{i}.png")
        if exists(p):
            explosion_frames.append(load_image(p))
    # boss frames optional - try folder boss/*
    boss_frames = []
    for i in range(8):
        p = join(ASSETS_DIR, "boss", f"{i}.png")
        if exists(p):
            boss_frames.append(load_image(p, (260,120)))
    if not boss_frames:
        boss_frames = None
except Exception:
    pass

# Sounds
laser_sound = load_sound("laser.wav")
explosion_sound = load_sound("explosion.wav")
game_music = load_sound("game_music.wav")
game_music.set_volume(0.25)
try:
    game_music.play(loops=-1)
except Exception:
    pass

# Fonts (Unicode support for ❤)
try:
    big_font = pygame.font.Font(join(ASSETS_DIR, "Oxanium-Bold.ttf"), 72)
    font = pygame.font.Font(join(ASSETS_DIR, "Oxanium-Bold.ttf"), 40)
    font_lives = pygame.font.Font(join(ASSETS_DIR, "DejaVuSans.ttf"), 24)
    small_font = pygame.font.Font(join(ASSETS_DIR, "Oxanium-Bold.ttf"), 18)
except Exception:
    big_font = pygame.font.SysFont("Arial", 72)
    font = pygame.font.SysFont("Arial", 40)
    # choose a Unicode-capable fallback
    font_lives = pygame.font.SysFont("Segoe UI Symbol", 24) or pygame.font.SysFont("Arial Unicode MS", 24)
    small_font = pygame.font.SysFont("Arial", 18)

# Sprites groups
all_sprites = pygame.sprite.Group()
pollution_sprites = pygame.sprite.Group()
green_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
explosion_sprites = pygame.sprite.Group()
boss_sprites = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()   # <-- group for boss projectiles

# Create initial background stars
for _ in range(30):
    Star(all_sprites, star_img)

# Game state variables
score = 0
high_score = load_highscore()
difficulty = 0
pollution_timer = pygame.time.get_ticks()
green_timer = pygame.time.get_ticks()
difficulty_time = pygame.time.get_ticks()
state = 'MAIN_MENU'  # MAIN_MENU, INSTRUCTIONS, PLAYING, GAME_OVER, WIN
player = None
mouse_pressed = False
mouse_pos = (0,0)
paused = False
boss_spawned = False
win_timer = 0

# Instructions text (completed)
instructions_text = [
    "CONTROLS:",
    " • Use Arrow keys or WASD to move",
    " • Press Space to shoot",
    " • Press P to pause, ESC to return to menu",
    "",
    "OBJECTIVE:",
    " • Shoot pollution items (+10 points)",
    " • Collect green items (+20 points)",
    " • Avoid pollution (lose 1 life, -15 points)",
    " • 'Plant' gives a temporary shield",
    " • 'Solar panel' reduces shooting cooldown",
    "",
    "BOSS:",
    " • A Boss will appear when you reach a high score",
    " • Shoot the Boss multiple times to defeat it",
    " • Beware! The Boss will attack back",
    ""
]

# Utility: draw button
def draw_button(surface, text, rect, bg_color, text_color=WHITE):
    pygame.draw.rect(surface, bg_color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return rect

# Display score & lives
def display_score():
    global score
    text_surf = font.render(str(score), True, WHITE)
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, 50))
    bg_rect = text_rect.inflate(40, 20)
    pygame.draw.rect(display_surface, (0,0,0), bg_rect)
    pygame.draw.rect(display_surface, WHITE, bg_rect, 2)
    display_surface.blit(text_surf, text_rect)

def display_lives():
    if not player:
        return
    lives_text = 'Lives: ' + '❤' * player.lives
    # Render with font_lives that supports heart; if not, fallback to ASCII
    try:
        text_surf = font_lives.render(lives_text, True, WHITE)
    except Exception:
        text_surf = font_lives.render(f'Lives: {player.lives}', True, WHITE)
    text_rect = text_surf.get_rect(topleft=(20,20))
    display_surface.blit(text_surf, text_rect)

# Reset game
def reset_game():
    global score, difficulty, pollution_timer, green_timer, difficulty_time, player, boss_spawned, boss_sprites
    score = 0
    difficulty = 0
    pollution_timer = pygame.time.get_ticks()
    green_timer = pygame.time.get_ticks()
    difficulty_time = pygame.time.get_ticks()
    boss_spawned = False

    # kill entities
    for s in pollution_sprites: s.kill()
    for s in green_sprites: s.kill()
    for s in laser_sprites: s.kill()
    for s in explosion_sprites: s.kill()
    for s in boss_sprites: s.kill()
    for s in boss_bullets: s.kill()

    # reset player
    if player:
        player.kill()
    # create new player
    return Player(all_sprites, player_img)

# Spawn functions
def spawn_pollution_at(pos, difficulty_local):
    Pollution(meteor_img, pos, (all_sprites, pollution_sprites), difficulty_local)

def spawn_pollution_random(difficulty_local):
    x = randint(40, WINDOW_WIDTH - 40)
    pos = (x, -40)
    Pollution(meteor_img, pos, (all_sprites, pollution_sprites), difficulty_local)

def spawn_green_at(pos, difficulty_local):
    GreenItem(pos, (all_sprites, green_sprites), difficulty_local)

def spawn_laser_from(player_rect_midtop):
    Laser(laser_img, player_rect_midtop, (all_sprites, laser_sprites))
    try:
        laser_sound.play()
    except Exception:
        pass

def spawn_boss_bullet_at(midtop_pos):
    # bullet size based on boss width; keep small
    BossBullet((12, 20), midtop_pos, (all_sprites, boss_bullets))

# Collisions
def collisions():
    global score, state, high_score, boss_spawned
    current_time = pygame.time.get_ticks()

    # Player - Pollution
    if player and not player.shield:
        collided = pygame.sprite.spritecollide(player, pollution_sprites, False, pygame.sprite.collide_mask)
        for pol in collided:
            player.lives -= 1
            score = max(0, score - 15)
            AnimatedExplosion(explosion_frames, pol.rect.center, (all_sprites, explosion_sprites), explosion_sound)
            pol.kill()
            if player.lives <= 0:
                high_score = max(high_score, score)
                save_highscore(high_score)
                state = 'GAME_OVER'
                return

    # Player - Green
    if player:
        collided_green = pygame.sprite.spritecollide(player, green_sprites, True, pygame.sprite.collide_mask)
        for g in collided_green:
            score += 20
            if g.subtype == 'plant':
                player.shield = True
                player.shield_time = current_time
            elif g.subtype == 'solar_panel':
                player.cooldown_duration = max(150, player.cooldown_duration - 80)
            elif g.subtype == 'recycling_bin':
                score += 10  # extra reward

    # Boss bullets hit player
    if player and not player.shield:
        hit_by_bullet = pygame.sprite.spritecollide(player, boss_bullets, True, pygame.sprite.collide_mask)
        if hit_by_bullet:
            player.lives -= 1
            AnimatedExplosion(explosion_frames, player.rect.center, (all_sprites, explosion_sprites), explosion_sound)
            if player.lives <= 0:
                high_score = max(high_score, score)
                save_highscore(high_score)
                state = 'GAME_OVER'
                return

    # Laser - Pollution & Laser - Boss
    for laser in list(laser_sprites):
        # Boss collision
        if boss_spawned:
            hit_boss = pygame.sprite.spritecollide(laser, boss_sprites, False, pygame.sprite.collide_mask)
            if hit_boss:
                for b in hit_boss:
                    # damage boss
                    b.health -= 5
                    AnimatedExplosion(explosion_frames, laser.rect.center, (all_sprites, explosion_sprites), explosion_sound)
                    if laser and laser.alive():
                        laser.kill()
                    # Check boss death
                    if b.health <= 0:
                        score += 500
                        AnimatedExplosion(explosion_frames, b.rect.center, (all_sprites, explosion_sprites), explosion_sound)
                        b.kill()
                        # Win condition
                        # set state properly (no setattr on globals())
                        high_score = max(high_score, score)
                        save_highscore(high_score)
                        # mark boss as not spawned and go to WIN
                        boss_spawned = False
                        state = 'WIN'
                        return
                    break
                continue

        collided = pygame.sprite.spritecollide(laser, pollution_sprites, False, pygame.sprite.collide_mask)
        if collided:
            for pol in collided:
                score += 10
                AnimatedExplosion(explosion_frames, pol.rect.center, (all_sprites, explosion_sprites), explosion_sound)
                pol.kill()
                if laser and laser.alive():
                    laser.kill()
                break

def win_game():  # kept for compatibility with old calls (not used now)
    global state, high_score
    high_score = max(high_score, score)
    save_highscore(high_score)
    state = 'WIN'

# ---------- Main loop ----------
running = True
player = None

while running:
    dt = clock.tick(FPS) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == 'PLAYING' and event.key == pygame.K_SPACE and player and player.can_shoot and not paused:
                spawn_laser_from(player.rect.midtop)
                player.can_shoot = False
                player.laser_shoot_time = pygame.time.get_ticks()
            if event.key == pygame.K_ESCAPE:
                if state == 'PLAYING':
                    state = 'MAIN_MENU'
                elif state in ('MAIN_MENU','INSTRUCTIONS','GAME_OVER','WIN'):
                    state = 'MAIN_MENU'
            if event.key == pygame.K_p and state == 'PLAYING':
                paused = not paused
            if state == 'GAME_OVER' and event.key == pygame.K_r:
                player = reset_game()
                state = 'PLAYING'
            if state == 'MAIN_MENU' and event.key == pygame.K_RETURN:
                player = reset_game()
                state = 'PLAYING'

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pressed = True

    # Mouse clicks handling for menus
    if state != 'PLAYING' and mouse_pressed:
        if state == 'MAIN_MENU':
            play_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 250, 240, 58)
            inst_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 318, 240, 58)
            exit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 386, 240, 58)
            if play_rect.collidepoint(mouse_pos):
                player = reset_game()
                state = 'PLAYING'
            elif inst_rect.collidepoint(mouse_pos):
                state = 'INSTRUCTIONS'
            elif exit_rect.collidepoint(mouse_pos):
                running = False
        elif state == 'INSTRUCTIONS':
            back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, 560, 100, 50)
            if back_rect.collidepoint(mouse_pos):
                state = 'MAIN_MENU'
        elif state == 'GAME_OVER':
            play_again_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 350, 240, 58)
            menu_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 418, 240, 58)
            exit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 486, 240, 58)
            if play_again_rect.collidepoint(mouse_pos):
                player = reset_game()
                state = 'PLAYING'
            elif menu_rect.collidepoint(mouse_pos):
                state = 'MAIN_MENU'
            elif exit_rect.collidepoint(mouse_pos):
                running = False
        elif state == 'WIN':
            menu_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 420, 240, 58)
            if menu_rect.collidepoint(mouse_pos):
                state = 'MAIN_MENU'
        mouse_pressed = False

    # Update game logic
    if state == 'PLAYING' and not paused:
        current_time = pygame.time.get_ticks()

        # Spawn pollution (faster with difficulty)
        spawn_interval = max(160, 900 - difficulty * 45)
        if current_time - pollution_timer > spawn_interval:
            pollution_timer = current_time
            spawn_pollution_random(difficulty)

        # Spawn green items
        spawn_interval_green = max(900, 3000 - difficulty * 100)
        if current_time - green_timer > spawn_interval_green:
            green_timer = current_time
            spawn_chance = max(0.18, 0.7 - difficulty * 0.05)
            if uniform(0, 1) < spawn_chance:
                x = randint(40, WINDOW_WIDTH - 40)
                spawn_green_at((x, -40), difficulty)

        # Increase difficulty every 10s
        if current_time - difficulty_time > 10000:
            difficulty_time = current_time
            difficulty += 1

        # Spawn boss if score threshold reached
        if not boss_spawned and score >= 200 and difficulty >= 2:
            Boss((all_sprites, boss_sprites), boss_frames)
            boss_spawned = True

        # If boss exists, let it shoot/spawn
        for b in boss_sprites:
            b.shoot(lambda c: spawn_boss_bullet_at(c))
            b.spawn_pollution(lambda pos, diff: spawn_pollution_at(pos, diff), difficulty)

        # Update all sprites (includes boss_bullets because they are in all_sprites)
        all_sprites.update(dt)
        boss_bullets.update(dt)

        # collisions
        collisions()

    # Drawing
    display_surface.fill(BG_COLOR)

    if state == 'PLAYING':
        all_sprites.draw(display_surface)
        boss_bullets.draw(display_surface)

        # Draw boss health bars if present
        for b in boss_sprites:
            # health bar background
            bar_w = 300
            bar_h = 18
            bar_x = WINDOW_WIDTH//2 - bar_w//2
            bar_y = 10
            pygame.draw.rect(display_surface, (60,60,60), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
            # current health
            health_ratio = max(0, b.health / b.max_health)
            pygame.draw.rect(display_surface, RED, (bar_x + 4, bar_y + 4, int((bar_w-8) * health_ratio), bar_h - 8), border_radius=6)
            text = small_font.render("BOSS", True, WHITE)
            display_surface.blit(text, (bar_x - 60, bar_y - 2))

        display_score()
        display_lives()
        if player and player.shield:
            pygame.draw.circle(display_surface, CYAN, player.rect.center, int(player.rect.width * 0.7), 3)

        # paused overlay
        if paused:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,120))
            display_surface.blit(overlay, (0,0))
            p_surf = big_font.render("PAUSED", True, WHITE)
            p_rect = p_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            display_surface.blit(p_surf, p_rect)

    elif state == 'MAIN_MENU':
        title_surf = big_font.render('ECO SHOOTER', True, GREEN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 150))
        display_surface.blit(title_surf, title_rect)

        sub_surf = font.render('Play Green - Save The Earth', True, WHITE)
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 220))
        display_surface.blit(sub_surf, sub_rect)

        play_rect = draw_button(display_surface, 'PLAY GAME', pygame.Rect(WINDOW_WIDTH // 2 - 120, 250, 240, 58), DARK_GREEN)
        inst_rect = draw_button(display_surface, 'INSTRUCTIONS', pygame.Rect(WINDOW_WIDTH // 2 - 130, 318, 260, 58), MENU_BLUE)
        exit_rect = draw_button(display_surface, 'EXIT GAME', pygame.Rect(WINDOW_WIDTH // 2 - 120, 386, 240, 58), RED)

        hs_surf = small_font.render(f'High Score: {high_score}', True, WHITE)
        hs_rect = hs_surf.get_rect(center=(WINDOW_WIDTH // 2, 480))
        display_surface.blit(hs_surf, hs_rect)

        hint = small_font.render("Press ENTER to Quick Play", True, WHITE)
        display_surface.blit(hint, (WINDOW_WIDTH//2 - hint.get_width()//2, 520))

    elif state == 'INSTRUCTIONS':
        title_surf = big_font.render('HOW TO PLAY', True, GREEN)
        display_surface.blit(title_surf, (WINDOW_WIDTH//2 - title_surf.get_width()//2, 40))

        y = 140
        for line in instructions_text:
            line_surf = small_font.render(line, True, WHITE)
            display_surface.blit(line_surf, (100, y))
            y += 34

        back_rect = draw_button(display_surface, 'BACK', pygame.Rect(WINDOW_WIDTH//2 - 50, 560, 100, 50), MENU_BLUE)

    elif state == 'GAME_OVER':
        title_surf = big_font.render('GAME OVER', True, RED)
        display_surface.blit(title_surf, (WINDOW_WIDTH//2 - title_surf.get_width()//2, 120))

        score_surf = font.render(f'Score: {score}', True, WHITE)
        display_surface.blit(score_surf, (WINDOW_WIDTH//2 - score_surf.get_width()//2, 220))

        hs_surf = small_font.render(f'High Score: {high_score}', True, WHITE)
        display_surface.blit(hs_surf, (WINDOW_WIDTH//2 - hs_surf.get_width()//2, 270))

        draw_button(display_surface, 'PLAY AGAIN (R)', pygame.Rect(WINDOW_WIDTH // 2 - 120, 350, 240, 58), DARK_GREEN)
        draw_button(display_surface, 'MAIN MENU', pygame.Rect(WINDOW_WIDTH // 2 - 120, 418, 240, 58), MENU_BLUE)
        draw_button(display_surface, 'EXIT', pygame.Rect(WINDOW_WIDTH // 2 - 120, 486, 240, 58), RED)

    elif state == 'WIN':
        title_surf = big_font.render('YOU WIN!', True, GREEN)
        display_surface.blit(title_surf, (WINDOW_WIDTH//2 - title_surf.get_width()//2, 140))

        score_surf = font.render(f'Score: {score}', True, WHITE)
        display_surface.blit(score_surf, (WINDOW_WIDTH//2 - score_surf.get_width()//2, 260))

        draw_button(display_surface, 'BACK TO MENU', pygame.Rect(WINDOW_WIDTH // 2 - 120, 420, 240, 58), MENU_BLUE)

    # Flip display
    pygame.display.update()

# Clean up
pygame.quit()
