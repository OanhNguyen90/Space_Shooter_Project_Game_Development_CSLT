# eco_shooter_annotated.py
# Phiên bản mã có chú thích từng dòng (ngắn gọn):
# Mỗi dòng code có chú thích giải thích 'cú pháp' và 'công dụng' trong toàn thể.

import pygame  # import module 'pygame' để dùng API game/âm thanh/đầu vào/đồ họa
from os.path import join, exists, abspath  # import các hàm thao tác đường dẫn (join, kiểm tra tồn tại, lấy đường dẫn tuyệt đối)
from os import getcwd  # import hàm lấy thư mục làm việc hiện tại
from random import randint, choice  # import các hàm sinh số ngẫu nhiên nguyên và chọn ngẫu nhiên
import sys  # import module hệ thống (thường dùng để thoát chương trình...)
import math  # import module toán học (sin, pi, sqrt...)
import json  # import để lưu/đọc trạng thái game sang file json

# ---------- cấu hình cửa sổ & FPS ----------
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720  # khai báo hằng kích thước cửa sổ (tuple unpacking)
FPS = 60  # khung hình trên giây (số nguyên)

# ---------- màu sắc (RGB tuples) ----------
WHITE = (255, 255, 255)  # tuple RGB màu trắng
BLACK = (0, 0, 0)  # tuple RGB màu đen
GREEN = (0, 200, 0)  # xanh đậm
LIME = (0, 255, 0)  # xanh sáng
RED = (255, 0, 0)  # đỏ
BLUE = (0, 120, 255)  # xanh dương
MENU_BLUE = (0, 100, 150)  # xanh menu
BG_COLOR = (34, 28, 38)  # màu nền tối
CYAN = (0, 200, 220)  # xanh dương sáng
YELLOW = (240, 220, 40)  # vàng

# ---------- assets paths & files ----------
ASSETS_DIR = "images"  # thư mục chứa assets (chuỗi)
AUDIO_SUBDIR = "audio"  # thư mục con chứa audio
HIGH_SCORE_FILE = "highscore.txt"  # file lưu điểm cao nhất
SAVE_FILE = "savegame.json"  # file lưu trạng thái game khi pause

# ---------- save message ----------
SAVE_MESSAGE_DURATION = 2500  # ms hiển thị thông báo "Game Saved"

# ---------- educational info ----------
educational_info = {  # từ điển chứa thông tin giáo dục (key->string)
    'reusable_bag': "Using reusable bags reduces plastic waste. Vietnam discards 3.2 million tons of plastic yearly!",
    'water_bottle': "Reusable water bottles prevent thousands of single-use plastics from polluting oceans and landfills.",
    'plant': "Planting trees absorbs CO2 and improves air quality. One tree can sequester 48 lbs of CO2 per year!",
    'solar_panel': "Solar panels provide clean, renewable energy, reducing air pollution from fossil fuels.",
    'recycling_bin': "Recycling saves resources: Recycling 1 ton of paper saves 17 trees and 7,000 gallons of water!"
}

questions = [  # danh sách câu hỏi quiz dạng dict
    {
        "question": "How much household solid waste is generated daily in Vietnam?",
        "options": ["A. 20,000 tons", "B. 67,877 tons", "C. 100,000 tons"],
        "correct": "B"
    },
    {
        "question": "How much plastic waste does Vietnam produce annually?",
        "options": ["A. 1 million tons", "B. 3.2 million tons", "C. 5 million tons"],
        "correct": "B"
    },
    {
        "question": "What percentage of waste on Vietnamese beaches is plastic?",
        "options": ["A. 50%", "B. 95.4%", "C. 80%"],
        "correct": "B"
    },
    {
        "question": "Does air pollution (PM2.5) in Ho Chi Minh City often exceed WHO standards?",
        "options": ["A. Never", "B. Yes, often", "C. Rarely"],
        "correct": "B"
    }
]

# ---------- pre-init audio safe ----------
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)  # gọi pre_init để cấu hình mixer trước khi init pygame (tần số, định dạng,...)
except Exception:
    pass  # nếu xảy ra lỗi thì bỏ qua (phòng lỗi khi chạy trong môi trường thiếu audio)

# ---------- helper: tìm file assets ----------
def find_asset_candidates(filename):  # định nghĩa hàm trả về list đường dẫn khả thi cho 1 filename
    if not filename:
        return []  # nếu không có tên file thì trả về list rỗng
    candidates = [
        filename,  # thử chính xác string người truyền
        join(ASSETS_DIR, AUDIO_SUBDIR, filename),  # thử images/audio/filename
        join(AUDIO_SUBDIR, filename),  # thử audio/filename
        join(ASSETS_DIR, filename),  # thử images/filename
        join('.venv', 'audio', filename),  # thử đường dẫn .venv/audio/filename (fallback dev)
        join(getcwd(), filename)  # thử đường dẫn tuyệt đối từ current working dir
    ]
    return [abspath(p) for p in candidates]  # trả về danh sách các đường dẫn tuyệt đối

class DummySound:  # lớp mô phỏng Sound khi audio không tồn tại
    def play(self, *a, **k): pass  # phương thức play không làm gì
    def set_volume(self, *a, **k): pass  # phương thức set_volume không làm gì

def load_sound(name):  # hàm load âm thanh, trả về pygame.mixer.Sound hoặc DummySound
    if not name:
        return DummySound()  # nếu tên rỗng thì trả DummySound
    for p in find_asset_candidates(name):  # duyệt các đường dẫn khả thi
        try:
            if exists(p):  # nếu file tồn tại
                try:
                    s = pygame.mixer.Sound(p)  # thử tạo Sound từ đường dẫn
                    print(f"[audio] Loaded sound: {p}")  # log
                    return s  # trả sound
                except Exception as e:
                    print(f"[audio] Failed to load sound {p}: {e}")  # báo lỗi nếu không load được
        except Exception:
            continue
    print(f"[audio] Warning: sound '{name}' not found; using dummy sound.")
    return DummySound()  # nếu không tìm thấy file, trả DummySound

def load_music(name):  # hàm load nhạc nền (sử dụng pygame.mixer.music)
    if not name:
        return False
    for p in find_asset_candidates(name):
        try:
            if exists(p):
                try:
                    pygame.mixer.music.load(p)  # load file vào music channel
                    print(f"[audio] Loaded music: {p}")
                    return True
                except Exception as e:
                    print(f"[audio] Failed to load music {p}: {e}")
        except Exception:
            continue
    print(f"[audio] Warning: music '{name}' not found.")
    return False

# ---------- helper load image ----------
def load_image(path, size=None):  # load image với fallback tạo placeholder surface
    if not path:
        w, h = size if size else (40, 40)  # nếu không có path thì dùng kích thước mặc định
        surf = pygame.Surface((w, h), pygame.SRCALPHA)  # tạo surface trong suốt
        pygame.draw.rect(surf, (120,120,120), surf.get_rect(), border_radius=8)  # vẽ khung placeholder
        pygame.draw.line(surf, (80,80,80), (2,2), (w-3,h-3), 2)  # vẽ đường chéo để hiện placeholder
        return surf
    try:
        p = abspath(path)  # lấy đường dẫn tuyệt đối
        if exists(p):
            surf = pygame.image.load(p).convert_alpha()  # load và convert alpha
            if size:
                surf = pygame.transform.smoothscale(surf, size)  # scale nếu cần
            return surf
        # try alt variants
        low = path.lower()
        if exists(low):
            surf = pygame.image.load(abspath(low)).convert_alpha()
            if size:
                surf = pygame.transform.smoothscale(surf, size)
            return surf
        up = path.upper()
        if exists(up):
            surf = pygame.image.load(abspath(up)).convert_alpha()
            if size:
                surf = pygame.transform.smoothscale(surf, size)
            return surf
    except Exception as e:
        print(f"[image] failed load {path}: {e}")
    w, h = size if size else (40, 40)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)  # tạo placeholder khi không load được
    pygame.draw.rect(surf, (120,120,120), surf.get_rect(), border_radius=8)
    pygame.draw.line(surf, (80,80,80), (2,2), (w-3,h-3), 2)
    return surf

# ---------- Sprite classes ----------
class Player(pygame.sprite.Sprite):  # lớp người chơi kế thừa Sprite của pygame
    def __init__(self, groups, surf=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)  # gọi constructor Sprite, thêm vào nhóm (unpack)
        else:
            super().__init__(groups)  # hoặc truyền trực tiếp 1 group
        if surf:
            self.image = surf  # nếu có surface truyền vào thì dùng
        else:
            surf = pygame.Surface((64,48), pygame.SRCALPHA)  # tạo surface mặc định cho player
            pygame.draw.polygon(surf, LIME, [(32,0),(0,48),(64,48)])  # vẽ hình tam giác làm phi thuyền
            self.image = surf
        self.original_image = self.image  # lưu bản gốc để xử lý xoay/scale nếu cần
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT-100))  # rect để xử lý va chạm/hiển thị
        self.direction = pygame.Vector2()  # vector hướng di chuyển
        self.speed = 360  # tốc độ điểm/giây
        self.lives = 5  # số mạng
        self.max_lives_display = 10  # tối đa hiển thị
        self.shield = False  # cờ shield
        self.shield_time = 0  # thời điểm bật shield
        self.shield_duration = 5000  # ms thời lượng shield
        self.can_shoot = True  # cờ cho phép bắn
        self.laser_shoot_time = 0  # thời điểm bắn cuối
        self.cooldown_duration = 150  # ms cooldown giữa các lần bắn
        try:
            self.mask = pygame.mask.from_surface(self.image)  # mask cho va chạm chính xác
        except Exception:
            self.mask = None  # fallback None nếu không tạo được mask

    def laser_timer(self):
        if not self.can_shoot and pygame.time.get_ticks() - self.laser_shoot_time >= self.cooldown_duration:
            self.can_shoot = True  # bật lại khả năng bắn sau cooldown

    def shield_timer(self):
        if self.shield and pygame.time.get_ticks() - self.shield_time >= self.shield_duration:
            self.shield = False  # tắt shield khi hết thời gian

    def update(self, dt):  # hàm update được gọi mỗi frame (dt = delta seconds)
        keys = pygame.key.get_pressed()  # lấy trạng thái phím
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])  # tính hướng ngang
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])  # tính hướng dọc
        self.direction = pygame.Vector2(dx, dy)  # set vector hướng
        if self.direction.length() != 0:
            self.direction = self.direction.normalize()  # chuẩn hóa vector để tốc độ đều
        pos = pygame.Vector2(self.rect.center)  # lấy vị trí hiện tại
        pos += self.direction * self.speed * dt  # tính vị trí mới theo speed và dt
        pos.x = max(self.rect.width//2, min(WINDOW_WIDTH - self.rect.width//2, pos.x))  # giới hạn theo biên ngang
        pos.y = max(self.rect.height//2, min(WINDOW_HEIGHT - self.rect.height//2, pos.y))  # giới hạn theo biên dọc
        self.rect.center = (round(pos.x), round(pos.y))  # gán vị trí (làm tròn)
        self.laser_timer()  # cập nhật timer bắn
        self.shield_timer()  # cập nhật timer shield

class Star(pygame.sprite.Sprite):  # hiệu ứng sao nền
    def __init__(self, all_groups, surf=None):
        if isinstance(all_groups, (list, tuple)):
            super().__init__(*all_groups)
        else:
            super().__init__(all_groups)
        if surf:
            self.image = surf
        else:
            size = randint(1,3)
            surf = pygame.Surface((size,size), pygame.SRCALPHA)
            pygame.draw.circle(surf, WHITE, (size//2,size//2), size//2)
            self.image = surf
        self.rect = self.image.get_rect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))  # vị trí ngẫu nhiên
        self.speed = randint(10,60)  # tốc độ rơi
    def update(self, dt):
        self.rect.y += self.speed * dt  # di chuyển xuống
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = 0  # reset về trên cùng
            self.rect.centerx = randint(0, WINDOW_WIDTH)

class Laser(pygame.sprite.Sprite):  # đạn của player
    def __init__(self, surf, pos, groups):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.image = surf  # surface đạn
        self.rect = self.image.get_rect(midbottom=pos)  # đặt điểm midbottom theo pos truyền vào
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
        self.speed = 750  # tốc độ đạn
    def update(self, dt):
        self.rect.y -= self.speed * dt  # di chuyển lên
        if self.rect.bottom < 0:
            self.kill()  # hủy sprite khi ra khỏi màn hình

class BossBullet(pygame.sprite.Sprite):  # đạn của boss, hỗ trợ 2 kiểu khởi tạo (size_or_pos)
    def __init__(self, size_or_pos, pos=None, groups=None):
        if isinstance(groups, (list, tuple)) or isinstance(groups, pygame.sprite.Group):
            size = size_or_pos
            spawn_pos = pos
            grps = groups
        else:
            spawn_pos = size_or_pos
            grps = pos
            size = None
        if isinstance(grps, (list, tuple)):
            super().__init__(*grps)
        else:
            super().__init__(grps)
        global boss_bullet_img
        try:
            if 'boss_bullet_img' in globals() and boss_bullet_img:
                self.image = boss_bullet_img.copy()
                self.rect = self.image.get_rect(midtop=spawn_pos)
            else:
                size_use = size if size else (18,28)
                surf = pygame.Surface(size_use, pygame.SRCALPHA)
                pygame.draw.rect(surf, (200,60,60), surf.get_rect(), border_radius=4)
                self.image = surf
                self.rect = self.image.get_rect(midtop=spawn_pos)
            try:
                self.mask = pygame.mask.from_surface(self.image)
            except Exception:
                self.mask = None
        except Exception:
            surf = pygame.Surface((18,28), pygame.SRCALPHA)
            pygame.draw.rect(surf, (200,60,60), surf.get_rect(), border_radius=4)
            self.image = surf
            self.rect = self.image.get_rect(midtop=spawn_pos)
            try:
                self.mask = pygame.mask.from_surface(self.image)
            except Exception:
                self.mask = None
        self.speed = 360  # tốc độ rơi của đạn boss
    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Pollution(pygame.sprite.Sprite):  # vật thể ô nhiễm (kẻ thù)
    def __init__(self, surf, pos, groups, difficulty):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.original_surf = surf  # giữ bản gốc để xoay
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(0,1)  # di chuyển xuống
        self.speed = randint(120,260) + difficulty*20  # tốc độ tăng theo difficulty
        self.rotation = 0
        self.rotation_speed = randint(-120,120)  # tốc độ xoay
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
        self.pollution_type = choice(['plastic_waste','air_pollution','solid_waste'])  # chọn loại ô nhiễm
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt  # di chuyển
        if self.rect.top > WINDOW_HEIGHT + 120:
            self.kill()  # hủy khi ra khỏi vùng
            return
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360  # cập nhật góc xoay
        try:
            self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)  # xoay ảnh
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            pass

class GreenItem(pygame.sprite.Sprite):  # vật phẩm xanh, cho thưởng và thông tin
    def __init__(self, pos, groups, difficulty):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.subtype = choice(['reusable_bag','water_bottle','plant','solar_panel','recycling_bin'])  # loại vật phẩm
        img = None
        try:
            subtype_to_idx = {
                'reusable_bag': 0,
                'water_bottle': 1,
                'plant': 2,
                'solar_panel': 3,
                'recycling_bin': 0
            }
            idx = subtype_to_idx.get(self.subtype, 0)
            if 'green_item_images' in globals() and green_item_images and idx < len(green_item_images):
                img = green_item_images[idx].copy()  # lấy ảnh tương ứng nếu có
        except Exception:
            img = None
        if img:
            self.image = img
            self.rect = self.image.get_rect(center=pos)
        else:
            size = 40
            surf = pygame.Surface((size,size), pygame.SRCALPHA)
            pygame.draw.circle(surf, GREEN, (size//2,size//2), size//2)
            pygame.draw.circle(surf, (0,120,0), (size//2,size//2), size//2, 3)
            self.image = surf
            self.rect = self.image.get_rect(center=pos)
        self.speed = randint(80,180) + difficulty*8
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT + 50:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):  # hiệu ứng nổ có khung ảnh
    def __init__(self, frames, pos, groups, sound=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.frames = frames or []  # danh sách frames
        self.frame_index = 0.0
        if self.frames:
            self.image = self.frames[0]
        else:
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
            self.frame_index += 10 * dt
            if self.frame_index > 1:
                self.kill()
            return
        self.frame_index += 24 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class Boss(pygame.sprite.Sprite):  # lớp Boss chính với animation, di chuyển bong bóng (bob)
    def __init__(self, groups, frames=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        if frames and len(frames):
            self.frames = frames
            self.image = frames[0]
            self.anim_index = 0.0
        else:
            self.frames = None
            self.image = pygame.Surface((260,120), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (180,30,30), self.image.get_rect())
            self.anim_index = 0.0
        self.rect = self.image.get_rect(midtop=(WINDOW_WIDTH//2, -150))  # bắt đầu ở trên màn hình (entrance)
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
        self.health = 60
        self.max_health = 60
        self.speed = 140
        self.direction = pygame.Vector2(1,0)
        self.entered = False  # cờ đã vào vị trí chưa
        self.shoot_timer = pygame.time.get_ticks()
        self.shoot_interval = 1200
        self.spawn_pollution_timer = pygame.time.get_ticks()
        self.spawn_pollution_interval = 2000
        self.bob_phase = 0.0
        self.bob_amplitude = 28.0
        self.bob_speed = 2.5
        self.base_y = None
        # faces still kept internally for sprite rendering, but UI icons are removed per request
        try:
            f0 = None
            f1 = None
            face0_path = join(ASSETS_DIR, "boss", "0.png")
            face1_path = join(ASSETS_DIR, "boss", "1.png")
            if exists(face0_path):
                f0 = load_image(face0_path, (48,48))
            if exists(face1_path):
                f1 = load_image(face1_path, (48,48))
            if not f0:
                f0 = pygame.Surface((48,48), pygame.SRCALPHA)
                pygame.draw.circle(f0, (200,230,180), (24,24), 22)
                pygame.draw.circle(f0, (0,0,0), (16,18), 3)
                pygame.draw.circle(f0, (0,0,0), (32,18), 3)
                pygame.draw.arc(f0, (0,120,0), (8,10,32,28), math.pi/8, math.pi - math.pi/8, 3)
            if not f1:
                f1 = pygame.Surface((48,48), pygame.SRCALPHA)
                pygame.draw.circle(f1, (240,180,180), (24,24), 22)
                pygame.draw.polygon(f1, (0,0,0), [(12,14),(20,18),(12,22)])
                pygame.draw.polygon(f1, (0,0,0), [(36,14),(28,18),(36,22)])
                pygame.draw.line(f1, (160,0,0), (12,34), (36,34), 4)
        except Exception:
            f0 = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.circle(f0, (200,230,180), (24,24), 22)
            f1 = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.circle(f1, (240,180,180), (24,24), 22)
        self.faces = (f0, f1)
        self.hard_mode = False

    def update(self, dt):
        if not self.entered:
            self.rect.y += 90 * dt  # di chuyển xuống trong giai đoạn xuất hiện
            if self.rect.top >= 40:
                self.entered = True
                self.base_y = self.rect.y
        else:
            self.rect.x += self.direction.x * self.speed * dt  # di chuyển ngang
            if self.rect.left <= 40:
                self.rect.left = 40
                self.direction.x *= -1  # đổi hướng khi chạm biên
            if self.rect.right >= WINDOW_WIDTH - 40:
                self.rect.right = WINDOW_WIDTH - 40
                self.direction.x *= -1
            self.bob_phase += self.bob_speed * dt
            if self.base_y is None:
                self.base_y = self.rect.y
            bob_y = self.base_y + math.sin(self.bob_phase) * self.bob_amplitude  # tính bob (lên xuống)
            self.rect.y = int(bob_y)
        if self.frames:
            self.anim_index += 6 * dt
            self.image = self.frames[int(self.anim_index) % len(self.frames)]
            self.rect = self.image.get_rect(center=self.rect.center)
            try:
                self.mask = pygame.mask.from_surface(self.image)
            except Exception:
                pass
        if not self.hard_mode and self.health <= (self.max_health // 2):
            self.hard_mode = True
            self.shoot_interval = max(400, self.shoot_interval // 2)  # tăng tần suất bắn
            self.spawn_pollution_interval = max(600, self.spawn_pollution_interval // 2)
            self.bob_speed = 4.0
            self.bob_amplitude = 40.0

    def shoot(self, spawn_fn):  # spawn_fn là hàm callback để tạo đạn
        now = pygame.time.get_ticks()
        if now - self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = now
            if not self.hard_mode:
                centers = [self.rect.midbottom, (self.rect.centerx - 48, self.rect.bottom - 10), (self.rect.centerx + 48, self.rect.bottom - 10)]
            else:
                centers = [
                    (self.rect.centerx - 80, self.rect.bottom - 6),
                    (self.rect.centerx - 40, self.rect.bottom - 6),
                    (self.rect.centerx, self.rect.bottom - 6),
                    (self.rect.centerx + 40, self.rect.bottom - 6),
                    (self.rect.centerx + 80, self.rect.bottom - 6)
                ]
            for c in centers:
                spawn_fn(c)  # gọi callback tạo đạn tại mỗi center

    def spawn_pollution(self, spawn_fn, difficulty):
        now = pygame.time.get_ticks()
        interval = max(600, self.spawn_pollution_interval - difficulty*40)
        if now - self.spawn_pollution_timer >= interval:
            self.spawn_pollution_timer = now
            x = randint(self.rect.left+20, self.rect.right-20)
            spawn_fn((x, self.rect.bottom + 10), difficulty)  # spawn pollution ở dưới boss

# ---------- highscore helpers ----------
def load_highscore():
    try:
        if exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as f:  # mở file đọc
                return int(f.read().strip())  # trả về int
    except Exception:
        pass
    return 0  # fallback 0

def save_highscore(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:  # mở file ghi (ghi đè)
            f.write(str(int(score)))  # ghi điểm (chuyển thành int rồi str)
    except Exception:
        pass

# ---------- save game helper ----------
def save_game_state():
    """
    Lưu trạng thái game chính ra file SAVE_FILE (JSON).
    Ghi: score, high_score, difficulty, level, player pos & lives & shield,
    boss_spawned & boss health & pos (nếu có), state, and timestamp.
    """
    try:
        data = {
            "score": int(score),
            "high_score": int(high_score),
            "difficulty": int(difficulty),
            "level": int(level),
            "state": state,
            "timestamp_ms": pygame.time.get_ticks()
        }
        # player info
        if player:
            try:
                data["player"] = {
                    "lives": int(player.lives),
                    "pos": (int(player.rect.centerx), int(player.rect.centery)),
                    "shield": bool(player.shield),
                    "shield_time": int(player.shield_time),
                    "shield_duration": int(player.shield_duration)
                }
            except Exception:
                data["player"] = None
        else:
            data["player"] = None

        # boss info
        try:
            data["boss_spawned"] = bool(boss_spawned)
            if boss and boss_spawned:
                data["boss"] = {
                    "health": int(getattr(boss, "health", 0)),
                    "max_health": int(getattr(boss, "max_health", 0)),
                    "pos": (int(boss.rect.centerx), int(boss.rect.centery))
                }
            else:
                data["boss"] = None
        except Exception:
            data["boss_spawned"] = False
            data["boss"] = None

        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[save] Game saved to {SAVE_FILE}")
        try:
            # feedback âm thanh nếu có
            if 'menu_click_sound' in globals() and menu_click_sound:
                menu_click_sound.play()
        except Exception:
            pass
        return True
    except Exception as e:
        print("[save] Failed to save game state:", e)
        return False

# ---------- init pygame & mixer ----------
pygame.init()  # khởi tạo pygame (display, font, v.v.)
try:
    pygame.mixer.init()  # khởi tạo mixer nếu có
    pygame.mixer.set_num_channels(32)  # set số kênh audio để phát đồng thời
except Exception as e:
    print("[audio] pygame.mixer.init() failed or unavailable:", e)

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # tạo cửa sổ hiển thị
pygame.display.set_caption("Eco Shooter - UI Update")  # tiêu đề cửa sổ
clock = pygame.time.Clock()  # đồng hồ để quản lý FPS

# ---------- load assets (images, frames, extra UI images) ----------
player_img = None  # placeholder biến ảnh
meteor_img = None
star_img = None
laser_img = None
explosion_frames = []
boss_frames = None
boss_bullet_img = None
green_item_images = []
background_img = None

# Extra UI images requested
captain_img = None
epilogue_img = None
gameover_bg_img = None
win_bg_img = None

try:
    # player
    p_path = join(ASSETS_DIR, "player.png")
    if exists(p_path):
        player_img = load_image(p_path, (64,48))  # load player image nếu có

    # meteor
    meteor_path = join(ASSETS_DIR, "meteor.png")
    if exists(meteor_path):
        meteor_img = load_image(meteor_path, (64,64))
    else:
        meteor_img = load_image(None, (64,64))  # fallback placeholder

    # star
    star_path = join(ASSETS_DIR, "star.png")
    if exists(star_path):
        star_img = load_image(star_path, (3,3))
    else:
        star_img = load_image(None, (3,3))

    # laser
    laser_path = join(ASSETS_DIR, "laser.png")
    if exists(laser_path):
        laser_img = load_image(laser_path, (8,28))
    else:
        laser_img = load_image(None, (8,28))

    # explosion frames (0..20)
    for i in range(21):
        p = join(ASSETS_DIR, "explosion", f"{i}.png")
        if exists(p):
            explosion_frames.append(load_image(p))

    # boss frames
    boss_frames_tmp = []
    for i in range(12):
        p = join(ASSETS_DIR, "boss", f"{i}.png")
        if exists(p):
            boss_frames_tmp.append(load_image(p, (260,120)))
    if boss_frames_tmp:
        boss_frames = boss_frames_tmp

    # boss_bullet image
    bb = join(ASSETS_DIR, "boss_bullet.png")
    if exists(bb):
        boss_bullet_img = load_image(bb, (18,28))

    # green_item images
    for i in range(6):
        p = join(ASSETS_DIR, f"green_item{i}.png")
        if exists(p):
            green_item_images.append(load_image(p, (40,40)))

    # background
    bg_candidates = [join(ASSETS_DIR, "background.PNG"), join(ASSETS_DIR, "background.png")]
    for bp in bg_candidates:
        if exists(bp):
            background_img = load_image(bp, (WINDOW_WIDTH, WINDOW_HEIGHT))
            break

    # ---------------------------
    # Extra UI assets requested by user (with fallback to container path)
    # ---------------------------
    cap_candidates = [join(ASSETS_DIR, "captain.png"), join(ASSETS_DIR, "captain.PNG")]
    for cp in cap_candidates:
        if exists(cp):
            captain_img = load_image(cp, (160, 200))
            break

    # fallback: dev-provided image in container (added)
    dev_cap_path = "/mnt/data/c43735b4-9797-411d-92c3-454ba2222b92.png"
    try:
        if not captain_img and exists(dev_cap_path):
            captain_img = load_image(dev_cap_path, (160, 2000))
            print(f"[assets] Loaded captain image from container: {dev_cap_path}")
    except Exception as e:
        print(f"[assets] Failed loading dev captain image: {e}")

    epi_candidates = [join(ASSETS_DIR, "epilogue.png"), join(ASSETS_DIR, "epilogue.PNG")]
    for ep in epi_candidates:
        if exists(ep):
            epilogue_img = load_image(ep, (160, 220))
            break

except Exception as e:
    print("[assets] error loading assets:", e)

# ---------- sounds ----------
laser_sound = load_sound("laser.wav")  # load hiệu ứng laser
explosion_sound = load_sound("explosion.wav")
pickup_sound = load_sound("pickup.wav")
menu_click_sound = load_sound("menu_click.wav")
quiz_correct_sound = load_sound("quiz_correct.wav")
quiz_wrong_sound = load_sound("quiz_wrong.wav")
boss_spawn_sound = load_sound("damage.ogg")
music_loaded = False
if load_music("game_music.wav") or load_music("game_music.ogg") or load_music(join(AUDIO_SUBDIR, "game_music.wav")):
    try:
        pygame.mixer.music.set_volume(0.25)  # đặt volume nhạc nền
        pygame.mixer.music.play(loops=-1)  # phát lặp vô tận
    except Exception:
        pass

# ---------- fonts ----------
CUSTOM_FONT_PATH = join(ASSETS_DIR, "Oxanium-Bold.ttf")  # đường dẫn font tuỳ chỉnh
CUSTOM_FONT_AVAILABLE = False
try:
    big_font = pygame.font.Font(CUSTOM_FONT_PATH, 72)  # cố thử load font tuỳ chỉnh
    font = pygame.font.Font(CUSTOM_FONT_PATH, 36)
    small_font = pygame.font.Font(CUSTOM_FONT_PATH, 18)
    CUSTOM_FONT_AVAILABLE = True
except Exception:
    big_font = pygame.font.SysFont("Arial", 72)  # fallback fonts hệ thống
    font = pygame.font.SysFont("Arial", 19)
    small_font = pygame.font.SysFont("Arial", 18)
    CUSTOM_FONT_AVAILABLE = False

try:
    font_lives = pygame.font.Font(join(ASSETS_DIR, "DejaVuSans.ttf"), 22)
except Exception:
    font_lives = pygame.font.SysFont("Segoe UI Symbol", 22)

# ---------- text wrapping + render helper ----------
def wrap_lines(text, font_obj, max_width):  # tách text thành nhiều dòng tuân theo max_width
    lines = []
    paragraphs = text.split('\n')
    for para in paragraphs:
        words = para.split(' ')
        if not words:
            lines.append('')
            continue
        line = ''
        for word in words:
            test_line = line + (' ' if line else '') + word
            fw, fh = font_obj.size(test_line)
            if fw <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                if font_obj.size(word)[0] > max_width:
                    part = ''
                    for ch in word:
                        test_part = part + ch
                        if font_obj.size(test_part)[0] <= max_width:
                            part = test_part
                        else:
                            if part:
                                lines.append(part)
                            part = ch
                    if part:
                        line = part
                    else:
                        line = ''
                else:
                    line = word
        if line:
            lines.append(line)
    return lines

def render_wrapped(surface, text, font_name_or_path, starting_size, color, rect, min_font_size=12):  # render text tự co để vừa rect
    size = starting_size
    while size >= min_font_size:
        try:
            if CUSTOM_FONT_AVAILABLE and exists(CUSTOM_FONT_PATH):
                f = pygame.font.Font(CUSTOM_FONT_PATH, size)
            else:
                f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", size)
        except Exception:
            f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", size)
        lines = wrap_lines(text, f, rect.width)
        total_height = len(lines) * f.get_linesize()
        if total_height <= rect.height:
            y = rect.top
            for line in lines:
                surf = f.render(line, True, color)
                surface.blit(surf, (rect.left, y))
                y += f.get_linesize()
            return f, size
        size -= 1
    try:
        if CUSTOM_FONT_AVAILABLE and exists(CUSTOM_FONT_PATH):
            f = pygame.font.Font(CUSTOM_FONT_PATH, min_font_size)
        else:
            f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", min_font_size)
    except Exception:
        f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", min_font_size)
    lines = wrap_lines(text, f, rect.width)
    y = rect.top
    for line in lines:
        surf = f.render(line, True, color)
        surface.blit(surf, (rect.left, y))
        y += f.get_linesize()
    return f, min_font_size

# ---------- groups & initial entities ----------
all_sprites = pygame.sprite.Group()  # nhóm chứa tất cả sprite
pollution_sprites = pygame.sprite.Group()  # nhóm kẻ thù
green_sprites = pygame.sprite.Group()  # nhóm vật phẩm xanh
laser_sprites = pygame.sprite.Group()  # nhóm đạn của player
explosion_sprites = pygame.sprite.Group()  # nhóm hiệu ứng nổ
boss_sprites = pygame.sprite.Group()  # nhóm boss
boss_bullets = pygame.sprite.Group()  # nhóm đạn boss

for _ in range(30):
    Star(all_sprites, star_img)  # tạo 30 sao nền

# ---------- game state ----------
score = 0
high_score = load_highscore()  # load highscore từ file
difficulty = 0
pollution_timer = pygame.time.get_ticks()
green_timer = pygame.time.get_ticks()
difficulty_time = pygame.time.get_ticks()
state = 'MAIN_MENU'  # trạng thái game (menu, playing...)
player = None
boss = None
mouse_pressed = False
mouse_pos = (0,0)
paused = False
boss_spawned = False
win_timer = 0
level = 0
current_quiz = None
quiz_message_timer = 0
quiz_message = ""
quiz_result_visible = False

# Flag để cho phép save 1 lần mỗi lần vào pause (auto-save on pause)
save_on_pause_allowed = True

# Save manual feedback
save_message = ""
save_message_timer = 0

# ---------- Visual Novel intro content ----------
vn_pages = [
    "Our mission is to save the planet: collect and recycle waste, encourage the use of fabric bags and reusable water bottles.",
    "On this journey, you will face sources of pollution: plastic waste, solid waste, and air pollution. Defeat them to reduce their impact.",
    "The final boss represents harmful consumption habits. Defeat the boss to help restore the environment and inspire the community.",
    "Remember: collect green items to gain educational information and power. Ready? Let’s set out and protect the planet!"
]
vn_page = 0

win_vn_pages = [
    "You have won! The boss – the symbol of polluting habits – has been defeated.",
    "The community is beginning to change: more people are using fabric bags, reusable bottles, and the coastline has less trash.",
    "Small actions create big differences. Thank you for protecting the planet!",
    "A happy ending: Everyone joins forces to preserve the environment. Press ENTER to return to the Menu."
]
win_vn_page = 0

# ---------- basic draw helpers ----------
def draw_text(surface, text, font_obj, color, pos):  # render text với font đã cho tại position
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(topleft=pos)
    surface.blit(txt, rect)
    return rect

def draw_centered(surface, text, font_obj, color, center):  # render text canh giữa
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(center=center)
    surface.blit(txt, rect)
    return rect

def draw_button(surface, rect, text, font_obj, mouse_pos, mouse_pressed, base_color, hover_color, click_sound=None):  # vẽ button cơ bản
    pygame.draw.rect(surface, base_color, rect, border_radius=12)
    hovered = rect.collidepoint(mouse_pos)
    if hovered:
        # slightly darker overlay to show hover
        pygame.draw.rect(surface, hover_color, rect, border_radius=12)
    txt = font_obj.render(text, True, WHITE)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)
    clicked = hovered and mouse_pressed
    if clicked and click_sound:
        try:
            click_sound.play()
        except Exception:
            pass
    return clicked

# ---------- spawn helpers ----------
def spawn_pollution_at(pos=None, difficulty=0):  # spawn đối tượng ô nhiễm
    surf = meteor_img if meteor_img else load_image(None, (64,64))
    if pos is None:
        x = randint(40, WINDOW_WIDTH - 40)
        y = -50
    else:
        x, y = pos
    Pollution(surf, (x, y), (all_sprites, pollution_sprites), difficulty)

def spawn_green_item():  # spawn vật phẩm xanh
    x = randint(40, WINDOW_WIDTH - 40)
    GreenItem((x, -20), (all_sprites, green_sprites), difficulty)

def spawn_boss_bullet_at(pos):  # spawn đạn boss, hỗ trợ ảnh nếu có
    if 'boss_bullet_img' in globals() and boss_bullet_img:
        BossBullet(pos, (all_sprites, boss_bullets))
    else:
        BossBullet((18,28), pos, (all_sprites, boss_bullets))

def player_shoot():  # hàm bắn của player
    global laser_sound
    if player and player.can_shoot:
        player.can_shoot = False
        player.laser_shoot_time = pygame.time.get_ticks()
        surf = laser_img if laser_img else load_image(None, (8,28))
        Laser(surf, player.rect.midtop, (all_sprites, laser_sprites))
        try:
            laser_sound.play()
        except Exception:
            pass

def spawn_boss(difficulty_level=0):  # khởi tạo boss
    global boss_spawned, boss
    boss_spawned = True
    boss = Boss((all_sprites, boss_sprites), frames=boss_frames)
    boss.health = 50 + difficulty_level * 15
    boss.max_health = boss.health
    try:
        boss_spawn_sound.play()
    except Exception:
        pass

def create_explosion(pos):
    AnimatedExplosion(explosion_frames, pos, (all_sprites, explosion_sprites), sound=explosion_sound)

def reset_game():  # đặt lại trạng thái game khi bắt đầu hoặc restart
    global score, difficulty, pollution_timer, green_timer, difficulty_time
    global state, player, boss_spawned, boss, win_timer, level, save_on_pause_allowed
    all_sprites.empty()
    pollution_sprites.empty()
    green_sprites.empty()
    laser_sprites.empty()
    explosion_sprites.empty()
    boss_sprites.empty()
    boss_bullets.empty()
    for _ in range(30):
        Star(all_sprites, star_img)
    player_surf = player_img if player_img else None
    player_obj = Player((all_sprites,), surf=player_surf)
    globals()['player'] = player_obj  # lưu player vào globals
    score = 0
    difficulty = 0
    level = 1
    pollution_timer = pygame.time.get_ticks()
    green_timer = pygame.time.get_ticks()
    difficulty_time = pygame.time.get_ticks()
    boss_spawned = False
    boss = None
    win_timer = 0
    # reset flag save when resetting game so next pause can auto-save once
    save_on_pause_allowed = True

reset_game()  # khởi tạo game lần đầu

# ---------- main loop ----------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # dt tính bằng giây (frame delta)
    now = pygame.time.get_ticks()  # thời gian hiện tại (ms)
    for event in pygame.event.get():  # xử lý event queue
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == 'MAIN_MENU':
                if event.key == pygame.K_RETURN:
                    state = 'VN_INTRO'
                    vn_page = 0
                elif event.key == pygame.K_i:
                    state = 'INSTRUCTIONS'
            elif state == 'INSTRUCTIONS':
                if event.key == pygame.K_ESCAPE:
                    state = 'MAIN_MENU'
            elif state == 'VN_INTRO':
                if event.key == pygame.K_RETURN:
                    vn_page += 1
                    if vn_page >= len(vn_pages):
                        reset_game()
                        state = 'PLAYING'
                elif event.key == pygame.K_ESCAPE:
                    state = 'MAIN_MENU'
            elif state == 'PLAYING':
                if event.key == pygame.K_SPACE:
                    player_shoot()
                if event.key == pygame.K_p:
                    # toggle pause immediately
                    paused = not paused
                    if paused:
                        # khi chuyển sang paused: auto-save 1 lần nếu được phép
                        if save_on_pause_allowed:
                            if save_game_state():
                                save_message = "Game auto-saved on pause."
                            else:
                                save_message = "Auto-save failed."
                            save_message_timer = now
                            save_on_pause_allowed = False
                    else:
                        # khi unpause: cho phép auto-save lại ở lần pause tiếp theo
                        save_on_pause_allowed = True
                if event.key == pygame.K_ESCAPE:
                    state = 'MAIN_MENU'
            elif state in ('GAME_OVER',):
                if event.key == pygame.K_RETURN:
                    state = 'MAIN_MENU'
            elif state == 'QUIZ':
                if event.key in (pygame.K_a, pygame.K_b, pygame.K_c):
                    ans = {pygame.K_a: "A", pygame.K_b: "B", pygame.K_c: "C"}[event.key]
                    if current_quiz:
                        if ans == current_quiz['correct']:
                            quiz_msg = "Correct!"
                            try:
                                quiz_correct_sound.play()
                            except Exception:
                                pass
                            score += 150
                        else:
                            quiz_msg = f"Wrong. The correct answer is {current_quiz['correct']}"
                            try:
                                quiz_wrong_sound.play()
                            except Exception:
                                pass
                        quiz_message = quiz_msg
                        quiz_message_timer = now
                        quiz_result_visible = True
                    state = 'PLAYING'
            elif state == 'WIN_VN':
                if event.key == pygame.K_RETURN:
                    win_vn_page += 1
                    if win_vn_page >= len(win_vn_pages):
                        state = 'MAIN_MENU'
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed = True
            mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = False
            mouse_pos = pygame.mouse.get_pos()

    if state == 'PLAYING' and not paused:
        if now - pollution_timer >= max(600, 1200 - difficulty * 50):
            pollution_timer = now
            spawn_pollution_at(difficulty=difficulty)
        if now - green_timer >= 3500:
            green_timer = now
            spawn_green_item()
        if now - difficulty_time >= 15000:
            difficulty_time = now
            difficulty += 1
            level += 1
        if not boss_spawned and score >= 2000 + difficulty * 1:
            spawn_boss(difficulty_level=difficulty)

    all_sprites.update(dt)  # cập nhật tất cả sprite

    if boss_spawned and boss_sprites:
        for b in boss_sprites:
            b.shoot(lambda pos: spawn_boss_bullet_at(pos))
            b.spawn_pollution(lambda pos, diff: spawn_pollution_at(pos=pos, difficulty=diff), difficulty)

    # collisions: pollution <-> laser
    hits = pygame.sprite.groupcollide(pollution_sprites, laser_sprites, True, True, pygame.sprite.collide_mask)
    for hit in hits:
        score += 50
        create_explosion(hit.rect.center)
        try:
            explosion_sound.play()
        except Exception:
            pass
        if randint(1,10) > 8:
            GreenItem(hit.rect.center, (all_sprites, green_sprites), difficulty)

    # boss hit by laser
    if boss_spawned:
        boss_hits = pygame.sprite.groupcollide(boss_sprites, laser_sprites, False, True, pygame.sprite.collide_mask)
        for b in boss_hits:
            b.health -= 1 + difficulty // 2
            create_explosion(b.rect.center)
            if b.health <= 0:
                create_explosion(b.rect.center)
                score += 2000
                b.kill()
                boss_spawned = False
                state = 'WIN_VN'
                win_vn_page = 0
                win_timer = now

    # player hit by boss bullets
    if player and not player.shield:
        hits = pygame.sprite.spritecollide(player, boss_bullets, True, pygame.sprite.collide_mask)
        if hits:
            player.lives -= 1
            create_explosion(player.rect.center)
            try:
                dmg = load_sound("damage.ogg")
                dmg.play()
            except Exception:
                pass
            if player.lives <= 0:
                state = 'GAME_OVER'
                if score > high_score:
                    save_highscore(score)
                    high_score = score

    # player hit by pollution
    if player and not player.shield:
        hits = pygame.sprite.spritecollide(player, pollution_sprites, True, pygame.sprite.collide_mask)
        if hits:
            player.lives -= 1
            create_explosion(player.rect.center)
            try:
                dmg = load_sound("damage.ogg")
                dmg.play()
            except Exception:
                pass
            if player.lives <= 0:
                state = 'GAME_OVER'
                if score > high_score:
                    save_highscore(score)
                    high_score = score

    # pickups
    if player:
        pickups = pygame.sprite.spritecollide(player, green_sprites, True, pygame.sprite.collide_mask)
        for p in pickups:
            st = getattr(p, 'subtype', None)
            try:
                pickup_sound.play()
            except Exception:
                pass
            if st == 'reusable_bag':
                score += 200
                quiz_message = educational_info.get('reusable_bag', "")
            elif st == 'water_bottle':
                score += 200
                quiz_message = educational_info.get('water_bottle', "")
            elif st == 'plant':
                player.lives = min(player.lives + 1, player.max_lives_display)
                quiz_message = educational_info.get('plant', "")
            elif st == 'solar_panel':
                player.shield = True
                player.shield_time = now
                quiz_message = educational_info.get('solar_panel', "")
            elif st == 'recycling_bin':
                score += 300
                quiz_message = educational_info.get('recycling_bin', "")
            quiz_message_timer = now
            quiz_result_visible = True
            if randint(0, 60) < 8:
                current_quiz = choice(questions)
                state = 'QUIZ'

    # ---------- render ----------
    # draw background if available
    if background_img:
        display_surface.blit(background_img, (0,0))
    else:
        display_surface.fill(BG_COLOR)

    if state == 'MAIN_MENU':
        draw_centered(display_surface, "ECO SHOOTER", big_font, CYAN, (WINDOW_WIDTH//2, 120))
        btn_w, btn_h = 360, 64
        start_rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, 240, btn_w, btn_h)
        instr_rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, 320, btn_w, btn_h)
        quit_rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, 400, btn_w, btn_h)

        if draw_button(display_surface, start_rect, "Start Game", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            state = 'VN_INTRO'
            vn_page = 0
            mouse_pressed = False
        if draw_button(display_surface, instr_rect, "Instructions", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            state = 'INSTRUCTIONS'; mouse_pressed = False
        if draw_button(display_surface, quit_rect, "Quit", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            running = False; mouse_pressed = False

        bar_w = btn_w
        bar_h = 48
        bx = WINDOW_WIDTH//2 - bar_w//2
        by = 520
        pygame.draw.rect(display_surface, (20,20,20,220), (bx, by, bar_w, bar_h), border_radius=8)
        draw_centered(display_surface, f"High Score: {high_score}", font, YELLOW, (WINDOW_WIDTH//2, by + bar_h//2))

    elif state == 'VN_INTRO':
        panel_w, panel_h = WINDOW_WIDTH - 160, 300
        panel_rect = pygame.Rect(80, WINDOW_HEIGHT//2 - panel_h//2, panel_w, panel_h)
        panel_s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_s.fill((12,12,12,230))
        pygame.draw.rect(panel_s, (80,80,80), panel_s.get_rect(), 2, border_radius=12)
        display_surface.blit(panel_s, panel_rect.topleft)

        # Character box (left) - now show captain image if available
        char_rect = pygame.Rect(panel_rect.left + 18, panel_rect.top + 24, 180, panel_h - 48)
        pygame.draw.rect(display_surface, (30,30,40), char_rect, border_radius=8)
        pygame.draw.rect(display_surface, (90,90,110), char_rect, 3, border_radius=8)
        draw_text(display_surface, "Captain", small_font, WHITE, (char_rect.left + 12, char_rect.top + 8))

        # draw captain image if provided; else placeholder box
        if captain_img:
            img_rect = captain_img.get_rect(center=(char_rect.left + char_rect.width//2, char_rect.top + char_rect.height//2))
            display_surface.blit(captain_img, img_rect)
        else:
            face_placeholder = pygame.Surface((char_rect.width - 24, char_rect.height - 56), pygame.SRCALPHA)
            pygame.draw.rect(face_placeholder, (120,120,120), face_placeholder.get_rect(), border_radius=8)
            display_surface.blit(face_placeholder, (char_rect.left + 12, char_rect.top + 36))

        # text area (right)
        text_area = pygame.Rect(char_rect.right + 20, panel_rect.top + 20, panel_rect.right - (char_rect.right + 40), panel_h - 80)
        font_name_to_use = "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial"
        page_text = vn_pages[vn_page] if vn_page < len(vn_pages) else ""
        render_wrapped(display_surface, page_text, font_name_to_use, 26, WHITE, text_area, min_font_size=14)
        draw_text(display_surface, f"Page {vn_page+1}/{len(vn_pages)} - Press ENTER or Next", small_font, (180,180,180), (text_area.left, text_area.bottom + 8))

        next_rect = pygame.Rect(panel_rect.right - 140, panel_rect.bottom - 60, 120, 44)
        if draw_button(display_surface, next_rect, "Next", small_font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            vn_page += 1
            mouse_pressed = False
            if vn_page >= len(vn_pages):
                reset_game()
                state = 'PLAYING'

        skip_rect = pygame.Rect(panel_rect.left + 12, panel_rect.bottom - 60, 120, 44)
        if draw_button(display_surface, skip_rect, "Skip", small_font, mouse_pos, mouse_pressed, (80,80,80), (110,110,110), click_sound=menu_click_sound):
            state = 'MAIN_MENU'
            mouse_pressed = False

    elif state == 'INSTRUCTIONS':
        draw_centered(display_surface, "Instructions", big_font, MENU_BLUE, (WINDOW_WIDTH//2, 80))
        tips = [
            "Move: Arrow keys or WASD",
            "Shoot: SPACE (cooldown)",
            "Pause: P",
            "Collect green items to learn and gain bonuses.",
            "Answer quiz questions (A/B/C) for extra points.",
            "Pro tip: If text looks too big for your screen, try reducing the window size or font assets."
        ]
        y = 160
        for t in tips:
            rect = pygame.Rect(120, y, 760, 56)
            font_name_to_use = "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial"
            render_wrapped(display_surface, t, font_name_to_use, 28, WHITE, rect, min_font_size=14)
            y += 56
        draw_text(display_surface, "Press ESC to return to menu", small_font, WHITE, (120, y + 20))

    elif state in ('PLAYING', 'QUIZ'):
        all_sprites.draw(display_surface)  # vẽ tất cả sprite

        panel_w, panel_h = 520, 100
        panel_rect = pygame.Rect(8, 8, panel_w, panel_h)
        s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        s.fill((20,20,20,200))
        pygame.draw.rect(s, (80,80,80), s.get_rect(), 2, border_radius=8)
        display_surface.blit(s, panel_rect.topleft)

        draw_text(display_surface, f"Score: {score}", font, WHITE, (16, 14))
        draw_text(display_surface, f"High: {high_score}", small_font, YELLOW, (16, 56))

        hearts = min(player.lives if player else 0, 10)
        lives_text = "❤ " * hearts
        draw_text(display_surface, f"Lives: {lives_text}", font_lives, RED, (220, 16))
        draw_text(display_surface, f"Level: {level}", small_font, WHITE, (220, 56))

        if player and player.shield:
            remaining = max(0, player.shield_duration - (now - player.shield_time))
            ratio = remaining / player.shield_duration
            bar_w = 200; bar_h = 10
            x = WINDOW_WIDTH - bar_w - 16; y = 20
            pygame.draw.rect(display_surface, (60,60,60), (x, y, bar_w, bar_h))
            pygame.draw.rect(display_surface, (0,180,255), (x, y, int(bar_w*ratio), bar_h))

        # ---------- Boss health bar (NO ICONS) ----------
        if boss_spawned and boss_sprites:
            for b in boss_sprites:
                bar_w = 420; bar_h = 18
                left_padding = 12
                right_padding = 12
                available_left = panel_rect.right + left_padding
                available_width = WINDOW_WIDTH - available_left - right_padding
                safe_bar_w = min(bar_w, max(120, available_width))
                center_x = WINDOW_WIDTH//2 - safe_bar_w//2
                safe_x = center_x if center_x >= available_left else available_left
                if safe_x + safe_bar_w > WINDOW_WIDTH - right_padding:
                    safe_bar_w = WINDOW_WIDTH - right_padding - safe_x
                safe_bar_w = max(120, safe_bar_w)
                x = int(safe_x)
                y = 8
                pygame.draw.rect(display_surface, (80,80,80), (x, y, safe_bar_w, bar_h))
                ratio = max(0, b.health) / max(1, b.max_health)
                pygame.draw.rect(display_surface, (200,40,40), (x, y, int(safe_bar_w*ratio), bar_h))
                label = small_font.render("BOSS", True, WHITE)
                label_rect = label.get_rect(center=(x + safe_bar_w//2, y + bar_h + 12))
                display_surface.blit(label, label_rect)

        if paused:
            # overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            display_surface.blit(overlay, (0,0))

            # Title: PAUSED (căn thẳng, to rõ)
            title_y = WINDOW_HEIGHT//2 - 160
            draw_centered(display_surface, "PAUSED", big_font, YELLOW, (WINDOW_WIDTH//2, title_y))

            # Button layout: aligned & straight (centered vertically under title)
            btn_w = 420  # fixed width to ensure straight alignment
            btn_h = 64
            gap = 20
            # compute top of first button so the whole block is centered under the title
            buttons_total_height = 3 * btn_h + 2 * gap
            start_y = title_y + 48  # small gap under title
            # centers the block horizontally
            cx = WINDOW_WIDTH//2 - btn_w//2

            # Individual rects (stacked)
            save_rect = pygame.Rect(cx, start_y, btn_w, btn_h)
            resume_rect = pygame.Rect(cx, start_y + btn_h + gap, btn_w, btn_h)
            menu_rect = pygame.Rect(cx, start_y + 2*(btn_h + gap), btn_w, btn_h)

            # Draw buttons with consistent style
            # Save button: manual save allowed any time while paused
            if draw_button(display_surface, save_rect, "Save Game", font, mouse_pos, mouse_pressed, (0,120,220), (0,90,180), click_sound=menu_click_sound):
                ok = save_game_state()
                if ok:
                    save_message = "Game saved (manual)."
                else:
                    save_message = "Save failed."
                save_message_timer = now
                mouse_pressed = False  # prevent repeated triggers

            # Resume button: unpause immediately
            if draw_button(display_surface, resume_rect, "Resume", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
                paused = False
                # when resuming, allow next auto-save on next pause
                save_on_pause_allowed = True
                mouse_pressed = False

            # Main Menu button: go back to main menu (unpause -> menu)
            if draw_button(display_surface, menu_rect, "Return to Menu", font, mouse_pos, mouse_pressed, (80,80,80), (110,110,110), click_sound=menu_click_sound):
                paused = False
                state = 'MAIN_MENU'
                mouse_pressed = False

            # small explanatory line under the buttons (optional)
            hint_y = start_y + 3*(btn_h + gap) + 12
            draw_centered(display_surface, "Tip: Press P to toggle Pause. Click Save to store progress.", small_font, (200,200,200), (WINDOW_WIDTH//2, hint_y))

        if state == 'QUIZ' and current_quiz:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,190))
            display_surface.blit(overlay, (0,0))
            draw_centered(display_surface, "QUIZ TIME!", big_font, CYAN, (WINDOW_WIDTH//2, 100))
            q_rect = pygame.Rect(120, 180, WINDOW_WIDTH - 240, 96)
            font_name_to_use = "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial"
            render_wrapped(display_surface, current_quiz['question'], font_name_to_use, 28, WHITE, q_rect, min_font_size=14)
            opt_y = q_rect.bottom + 12
            opt_rect = pygame.Rect(160, opt_y, WINDOW_WIDTH - 320, 48 * len(current_quiz['options']))
            options_text = '\n'.join(current_quiz['options'])
            render_wrapped(display_surface, options_text, font_name_to_use, 26, LIME, opt_rect, min_font_size=14)
            draw_text(display_surface, "Press A / B / C to answer", small_font, WHITE, (120, opt_rect.bottom + 12))

        if quiz_result_visible and now - quiz_message_timer < 4000:
            box_w, box_h = 720, 96
            box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box.fill((20,20,20,220))
            pygame.draw.rect(box, (80,80,80), box.get_rect(), 2, border_radius=10)
            display_surface.blit(box, (WINDOW_WIDTH//2 - box_w//2, WINDOW_HEIGHT - 140))
            msg_rect = pygame.Rect(WINDOW_WIDTH//2 - box_w//2 + 12, WINDOW_HEIGHT - 140 + 12, box_w - 24, box_h - 24)
            render_wrapped(display_surface, quiz_message, "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial", 18, WHITE, msg_rect, min_font_size=12)
        elif quiz_result_visible and now - quiz_message_timer >= 4000:
            quiz_result_visible = False
            quiz_message = ""

        # save manual feedback display (small box near top-right)
        if save_message and now - save_message_timer < SAVE_MESSAGE_DURATION:
            sm_w, sm_h = 320, 48
            sm_x = WINDOW_WIDTH - sm_w - 16
            sm_y = 16
            sm = pygame.Surface((sm_w, sm_h), pygame.SRCALPHA)
            sm.fill((20,20,20,220))
            pygame.draw.rect(sm, (80,80,80), sm.get_rect(), 2, border_radius=8)
            display_surface.blit(sm, (sm_x, sm_y))
            draw_centered(display_surface, save_message, small_font, YELLOW, (sm_x + sm_w//2, sm_y + sm_h//2))
        elif save_message and now - save_message_timer >= SAVE_MESSAGE_DURATION:
            save_message = ""
            save_message_timer = 0

    elif state == 'GAME_OVER':
        # draw game over background image if available; else dim & gradient rectangle
        if gameover_bg_img:
            display_surface.blit(gameover_bg_img, (0,0))
        else:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((30, 10, 10))
            display_surface.blit(overlay, (0,0))
        draw_centered(display_surface, "GAME OVER", big_font, RED, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        draw_centered(display_surface, f"Score: {score}", font, WHITE, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        draw_centered(display_surface, f"High Score: {high_score}", small_font, YELLOW, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
        draw_centered(display_surface, "Press ENTER to return to Menu", small_font, WHITE, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 140))

    elif state == 'WIN_VN':
        # Win epilogue: draw win background if exists
        if win_bg_img:
            display_surface.blit(win_bg_img, (0,0))
        else:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10,40,10,120))
            display_surface.blit(overlay, (0,0))

        panel_w, panel_h = WINDOW_WIDTH - 160, 300
        panel_rect = pygame.Rect(80, WINDOW_HEIGHT//2 - panel_h//2, panel_w, panel_h)
        panel_s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_s.fill((10,40,10,200))
        pygame.draw.rect(panel_s, (80,80,80), panel_s.get_rect(), 2, border_radius=12)
        display_surface.blit(panel_s, panel_rect.topleft)

        # character/celebration box: now attempt to draw epilogue image
        char_rect = pygame.Rect(panel_rect.left + 18, panel_rect.top + 24, 180, panel_h - 48)
        pygame.draw.rect(display_surface, (40,40,30), char_rect, border_radius=8)
        pygame.draw.rect(display_surface, (110,110,90), char_rect, 3, border_radius=8)
        draw_text(display_surface, "Epilogue", small_font, WHITE, (char_rect.left + 12, char_rect.top + 8))

        if epilogue_img:
            img_rect = epilogue_img.get_rect(center=(char_rect.left + char_rect.width//2, char_rect.top + char_rect.height//2))
            display_surface.blit(epilogue_img, img_rect)
        else:
            face_placeholder = pygame.Surface((char_rect.width - 24, char_rect.height - 56), pygame.SRCALPHA)
            pygame.draw.rect(face_placeholder, (160,220,160), face_placeholder.get_rect(), border_radius=8)
            display_surface.blit(face_placeholder, (char_rect.left + 12, char_rect.top + 36))

        text_area = pygame.Rect(char_rect.right + 20, panel_rect.top + 20, panel_rect.right - (char_rect.right + 40), panel_h - 80)
        page_text = win_vn_pages[win_vn_page] if win_vn_page < len(win_vn_pages) else ""
        render_wrapped(display_surface, page_text, "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial", 24, WHITE, text_area, min_font_size=14)
        draw_text(display_surface, f"Page {win_vn_page+1}/{len(win_vn_pages)} - Press ENTER to continue", small_font, (220,220,220), (text_area.left, text_area.bottom + 8))

    pygame.display.flip()  # cập nhật toàn bộ màn hình

# ---------- cleanup ----------
try:
    pygame.mixer.quit()
except Exception:
    pass
pygame.quit()  # thoát pygame. pause menu layout fixed (buttons straight & centered)
# eco_shooter_annotated.py
# Phiên bản mã có chú thích từng dòng (ngắn gọn):
# Mỗi dòng code có chú thích giải thích 'cú pháp' và 'công dụng' trong toàn thể.

import pygame  # import module 'pygame' để dùng API game/âm thanh/đầu vào/đồ họa
from os.path import join, exists, abspath  # import các hàm thao tác đường dẫn (join, kiểm tra tồn tại, lấy đường dẫn tuyệt đối)
from os import getcwd  # import hàm lấy thư mục làm việc hiện tại
from random import randint, choice  # import các hàm sinh số ngẫu nhiên nguyên và chọn ngẫu nhiên
import sys  # import module hệ thống (thường dùng để thoát chương trình...)
import math  # import module toán học (sin, pi, sqrt...)
import json  # import để lưu/đọc trạng thái game sang file json

# ---------- cấu hình cửa sổ & FPS ----------
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720  # khai báo hằng kích thước cửa sổ (tuple unpacking)
FPS = 60  # khung hình trên giây (số nguyên)

# ---------- màu sắc (RGB tuples) ----------
WHITE = (255, 255, 255)  # tuple RGB màu trắng
BLACK = (0, 0, 0)  # tuple RGB màu đen
GREEN = (0, 200, 0)  # xanh đậm
LIME = (0, 255, 0)  # xanh sáng
RED = (255, 0, 0)  # đỏ
BLUE = (0, 120, 255)  # xanh dương
MENU_BLUE = (0, 100, 150)  # xanh menu
BG_COLOR = (34, 28, 38)  # màu nền tối
CYAN = (0, 200, 220)  # xanh dương sáng
YELLOW = (240, 220, 40)  # vàng

# ---------- assets paths & files ----------
ASSETS_DIR = "images"  # thư mục chứa assets (chuỗi)
AUDIO_SUBDIR = "audio"  # thư mục con chứa audio
HIGH_SCORE_FILE = "highscore.txt"  # file lưu điểm cao nhất
SAVE_FILE = "savegame.json"  # file lưu trạng thái game khi pause

# ---------- save message ----------
SAVE_MESSAGE_DURATION = 2500  # ms hiển thị thông báo "Game Saved"

# ---------- educational info ----------
educational_info = {  # từ điển chứa thông tin giáo dục (key->string)
    'reusable_bag': "Using reusable bags reduces plastic waste. Vietnam discards 3.2 million tons of plastic yearly!",
    'water_bottle': "Reusable water bottles prevent thousands of single-use plastics from polluting oceans and landfills.",
    'plant': "Planting trees absorbs CO2 and improves air quality. One tree can sequester 48 lbs of CO2 per year!",
    'solar_panel': "Solar panels provide clean, renewable energy, reducing air pollution from fossil fuels.",
    'recycling_bin': "Recycling saves resources: Recycling 1 ton of paper saves 17 trees and 7,000 gallons of water!"
}

questions = [  # danh sách câu hỏi quiz dạng dict
    {
        "question": "How much household solid waste is generated daily in Vietnam?",
        "options": ["A. 20,000 tons", "B. 67,877 tons", "C. 100,000 tons"],
        "correct": "B"
    },
    {
        "question": "How much plastic waste does Vietnam produce annually?",
        "options": ["A. 1 million tons", "B. 3.2 million tons", "C. 5 million tons"],
        "correct": "B"
    },
    {
        "question": "What percentage of waste on Vietnamese beaches is plastic?",
        "options": ["A. 50%", "B. 95.4%", "C. 80%"],
        "correct": "B"
    },
    {
        "question": "Does air pollution (PM2.5) in Ho Chi Minh City often exceed WHO standards?",
        "options": ["A. Never", "B. Yes, often", "C. Rarely"],
        "correct": "B"
    }
]

# ---------- pre-init audio safe ----------
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)  # gọi pre_init để cấu hình mixer trước khi init pygame (tần số, định dạng,...)
except Exception:
    pass  # nếu xảy ra lỗi thì bỏ qua (phòng lỗi khi chạy trong môi trường thiếu audio)

# ---------- helper: tìm file assets ----------
def find_asset_candidates(filename):  # định nghĩa hàm trả về list đường dẫn khả thi cho 1 filename
    if not filename:
        return []  # nếu không có tên file thì trả về list rỗng
    candidates = [
        filename,  # thử chính xác string người truyền
        join(ASSETS_DIR, AUDIO_SUBDIR, filename),  # thử images/audio/filename
        join(AUDIO_SUBDIR, filename),  # thử audio/filename
        join(ASSETS_DIR, filename),  # thử images/filename
        join('.venv', 'audio', filename),  # thử đường dẫn .venv/audio/filename (fallback dev)
        join(getcwd(), filename)  # thử đường dẫn tuyệt đối từ current working dir
    ]
    return [abspath(p) for p in candidates]  # trả về danh sách các đường dẫn tuyệt đối

class DummySound:  # lớp mô phỏng Sound khi audio không tồn tại
    def play(self, *a, **k): pass  # phương thức play không làm gì
    def set_volume(self, *a, **k): pass  # phương thức set_volume không làm gì

def load_sound(name):  # hàm load âm thanh, trả về pygame.mixer.Sound hoặc DummySound
    if not name:
        return DummySound()  # nếu tên rỗng thì trả DummySound
    for p in find_asset_candidates(name):  # duyệt các đường dẫn khả thi
        try:
            if exists(p):  # nếu file tồn tại
                try:
                    s = pygame.mixer.Sound(p)  # thử tạo Sound từ đường dẫn
                    print(f"[audio] Loaded sound: {p}")  # log
                    return s  # trả sound
                except Exception as e:
                    print(f"[audio] Failed to load sound {p}: {e}")  # báo lỗi nếu không load được
        except Exception:
            continue
    print(f"[audio] Warning: sound '{name}' not found; using dummy sound.")
    return DummySound()  # nếu không tìm thấy file, trả DummySound

def load_music(name):  # hàm load nhạc nền (sử dụng pygame.mixer.music)
    if not name:
        return False
    for p in find_asset_candidates(name):
        try:
            if exists(p):
                try:
                    pygame.mixer.music.load(p)  # load file vào music channel
                    print(f"[audio] Loaded music: {p}")
                    return True
                except Exception as e:
                    print(f"[audio] Failed to load music {p}: {e}")
        except Exception:
            continue
    print(f"[audio] Warning: music '{name}' not found.")
    return False

# ---------- helper load image ----------
def load_image(path, size=None):  # load image với fallback tạo placeholder surface
    if not path:
        w, h = size if size else (40, 40)  # nếu không có path thì dùng kích thước mặc định
        surf = pygame.Surface((w, h), pygame.SRCALPHA)  # tạo surface trong suốt
        pygame.draw.rect(surf, (120,120,120), surf.get_rect(), border_radius=8)  # vẽ khung placeholder
        pygame.draw.line(surf, (80,80,80), (2,2), (w-3,h-3), 2)  # vẽ đường chéo để hiện placeholder
        return surf
    try:
        p = abspath(path)  # lấy đường dẫn tuyệt đối
        if exists(p):
            surf = pygame.image.load(p).convert_alpha()  # load và convert alpha
            if size:
                surf = pygame.transform.smoothscale(surf, size)  # scale nếu cần
            return surf
        # try alt variants
        low = path.lower()
        if exists(low):
            surf = pygame.image.load(abspath(low)).convert_alpha()
            if size:
                surf = pygame.transform.smoothscale(surf, size)
            return surf
        up = path.upper()
        if exists(up):
            surf = pygame.image.load(abspath(up)).convert_alpha()
            if size:
                surf = pygame.transform.smoothscale(surf, size)
            return surf
    except Exception as e:
        print(f"[image] failed load {path}: {e}")
    w, h = size if size else (40, 40)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)  # tạo placeholder khi không load được
    pygame.draw.rect(surf, (120,120,120), surf.get_rect(), border_radius=8)
    pygame.draw.line(surf, (80,80,80), (2,2), (w-3,h-3), 2)
    return surf

# ---------- Sprite classes ----------
class Player(pygame.sprite.Sprite):  # lớp người chơi kế thừa Sprite của pygame
    def __init__(self, groups, surf=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)  # gọi constructor Sprite, thêm vào nhóm (unpack)
        else:
            super().__init__(groups)  # hoặc truyền trực tiếp 1 group
        if surf:
            self.image = surf  # nếu có surface truyền vào thì dùng
        else:
            surf = pygame.Surface((64,48), pygame.SRCALPHA)  # tạo surface mặc định cho player
            pygame.draw.polygon(surf, LIME, [(32,0),(0,48),(64,48)])  # vẽ hình tam giác làm phi thuyền
            self.image = surf
        self.original_image = self.image  # lưu bản gốc để xử lý xoay/scale nếu cần
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT-100))  # rect để xử lý va chạm/hiển thị
        self.direction = pygame.Vector2()  # vector hướng di chuyển
        self.speed = 360  # tốc độ điểm/giây
        self.lives = 5  # số mạng
        self.max_lives_display = 10  # tối đa hiển thị
        self.shield = False  # cờ shield
        self.shield_time = 0  # thời điểm bật shield
        self.shield_duration = 5000  # ms thời lượng shield
        self.can_shoot = True  # cờ cho phép bắn
        self.laser_shoot_time = 0  # thời điểm bắn cuối
        self.cooldown_duration = 150  # ms cooldown giữa các lần bắn
        try:
            self.mask = pygame.mask.from_surface(self.image)  # mask cho va chạm chính xác
        except Exception:
            self.mask = None  # fallback None nếu không tạo được mask

    def laser_timer(self):
        if not self.can_shoot and pygame.time.get_ticks() - self.laser_shoot_time >= self.cooldown_duration:
            self.can_shoot = True  # bật lại khả năng bắn sau cooldown

    def shield_timer(self):
        if self.shield and pygame.time.get_ticks() - self.shield_time >= self.shield_duration:
            self.shield = False  # tắt shield khi hết thời gian

    def update(self, dt):  # hàm update được gọi mỗi frame (dt = delta seconds)
        keys = pygame.key.get_pressed()  # lấy trạng thái phím
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])  # tính hướng ngang
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])  # tính hướng dọc
        self.direction = pygame.Vector2(dx, dy)  # set vector hướng
        if self.direction.length() != 0:
            self.direction = self.direction.normalize()  # chuẩn hóa vector để tốc độ đều
        pos = pygame.Vector2(self.rect.center)  # lấy vị trí hiện tại
        pos += self.direction * self.speed * dt  # tính vị trí mới theo speed và dt
        pos.x = max(self.rect.width//2, min(WINDOW_WIDTH - self.rect.width//2, pos.x))  # giới hạn theo biên ngang
        pos.y = max(self.rect.height//2, min(WINDOW_HEIGHT - self.rect.height//2, pos.y))  # giới hạn theo biên dọc
        self.rect.center = (round(pos.x), round(pos.y))  # gán vị trí (làm tròn)
        self.laser_timer()  # cập nhật timer bắn
        self.shield_timer()  # cập nhật timer shield

class Star(pygame.sprite.Sprite):  # hiệu ứng sao nền
    def __init__(self, all_groups, surf=None):
        if isinstance(all_groups, (list, tuple)):
            super().__init__(*all_groups)
        else:
            super().__init__(all_groups)
        if surf:
            self.image = surf
        else:
            size = randint(1,3)
            surf = pygame.Surface((size,size), pygame.SRCALPHA)
            pygame.draw.circle(surf, WHITE, (size//2,size//2), size//2)
            self.image = surf
        self.rect = self.image.get_rect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))  # vị trí ngẫu nhiên
        self.speed = randint(10,60)  # tốc độ rơi
    def update(self, dt):
        self.rect.y += self.speed * dt  # di chuyển xuống
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = 0  # reset về trên cùng
            self.rect.centerx = randint(0, WINDOW_WIDTH)

class Laser(pygame.sprite.Sprite):  # đạn của player
    def __init__(self, surf, pos, groups):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.image = surf  # surface đạn
        self.rect = self.image.get_rect(midbottom=pos)  # đặt điểm midbottom theo pos truyền vào
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
        self.speed = 750  # tốc độ đạn
    def update(self, dt):
        self.rect.y -= self.speed * dt  # di chuyển lên
        if self.rect.bottom < 0:
            self.kill()  # hủy sprite khi ra khỏi màn hình

class BossBullet(pygame.sprite.Sprite):  # đạn của boss, hỗ trợ 2 kiểu khởi tạo (size_or_pos)
    def __init__(self, size_or_pos, pos=None, groups=None):
        if isinstance(groups, (list, tuple)) or isinstance(groups, pygame.sprite.Group):
            size = size_or_pos
            spawn_pos = pos
            grps = groups
        else:
            spawn_pos = size_or_pos
            grps = pos
            size = None
        if isinstance(grps, (list, tuple)):
            super().__init__(*grps)
        else:
            super().__init__(grps)
        global boss_bullet_img
        try:
            if 'boss_bullet_img' in globals() and boss_bullet_img:
                self.image = boss_bullet_img.copy()
                self.rect = self.image.get_rect(midtop=spawn_pos)
            else:
                size_use = size if size else (18,28)
                surf = pygame.Surface(size_use, pygame.SRCALPHA)
                pygame.draw.rect(surf, (200,60,60), surf.get_rect(), border_radius=4)
                self.image = surf
                self.rect = self.image.get_rect(midtop=spawn_pos)
            try:
                self.mask = pygame.mask.from_surface(self.image)
            except Exception:
                self.mask = None
        except Exception:
            surf = pygame.Surface((18,28), pygame.SRCALPHA)
            pygame.draw.rect(surf, (200,60,60), surf.get_rect(), border_radius=4)
            self.image = surf
            self.rect = self.image.get_rect(midtop=spawn_pos)
            try:
                self.mask = pygame.mask.from_surface(self.image)
            except Exception:
                self.mask = None
        self.speed = 360  # tốc độ rơi của đạn boss
    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Pollution(pygame.sprite.Sprite):  # vật thể ô nhiễm (kẻ thù)
    def __init__(self, surf, pos, groups, difficulty):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.original_surf = surf  # giữ bản gốc để xoay
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(0,1)  # di chuyển xuống
        self.speed = randint(120,260) + difficulty*20  # tốc độ tăng theo difficulty
        self.rotation = 0
        self.rotation_speed = randint(-120,120)  # tốc độ xoay
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
        self.pollution_type = choice(['plastic_waste','air_pollution','solid_waste'])  # chọn loại ô nhiễm
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt  # di chuyển
        if self.rect.top > WINDOW_HEIGHT + 120:
            self.kill()  # hủy khi ra khỏi vùng
            return
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360  # cập nhật góc xoay
        try:
            self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)  # xoay ảnh
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            pass

class GreenItem(pygame.sprite.Sprite):  # vật phẩm xanh, cho thưởng và thông tin
    def __init__(self, pos, groups, difficulty):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.subtype = choice(['reusable_bag','water_bottle','plant','solar_panel','recycling_bin'])  # loại vật phẩm
        img = None
        try:
            subtype_to_idx = {
                'reusable_bag': 0,
                'water_bottle': 1,
                'plant': 2,
                'solar_panel': 3,
                'recycling_bin': 0
            }
            idx = subtype_to_idx.get(self.subtype, 0)
            if 'green_item_images' in globals() and green_item_images and idx < len(green_item_images):
                img = green_item_images[idx].copy()  # lấy ảnh tương ứng nếu có
        except Exception:
            img = None
        if img:
            self.image = img
            self.rect = self.image.get_rect(center=pos)
        else:
            size = 40
            surf = pygame.Surface((size,size), pygame.SRCALPHA)
            pygame.draw.circle(surf, GREEN, (size//2,size//2), size//2)
            pygame.draw.circle(surf, (0,120,0), (size//2,size//2), size//2, 3)
            self.image = surf
            self.rect = self.image.get_rect(center=pos)
        self.speed = randint(80,180) + difficulty*8
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT + 50:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):  # hiệu ứng nổ có khung ảnh
    def __init__(self, frames, pos, groups, sound=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        self.frames = frames or []  # danh sách frames
        self.frame_index = 0.0
        if self.frames:
            self.image = self.frames[0]
        else:
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
            self.frame_index += 10 * dt
            if self.frame_index > 1:
                self.kill()
            return
        self.frame_index += 24 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class Boss(pygame.sprite.Sprite):  # lớp Boss chính với animation, di chuyển bong bóng (bob)
    def __init__(self, groups, frames=None):
        if isinstance(groups, (list, tuple)):
            super().__init__(*groups)
        else:
            super().__init__(groups)
        if frames and len(frames):
            self.frames = frames
            self.image = frames[0]
            self.anim_index = 0.0
        else:
            self.frames = None
            self.image = pygame.Surface((260,120), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (180,30,30), self.image.get_rect())
            self.anim_index = 0.0
        self.rect = self.image.get_rect(midtop=(WINDOW_WIDTH//2, -150))  # bắt đầu ở trên màn hình (entrance)
        try:
            self.mask = pygame.mask.from_surface(self.image)
        except Exception:
            self.mask = None
        self.health = 60
        self.max_health = 60
        self.speed = 140
        self.direction = pygame.Vector2(1,0)
        self.entered = False  # cờ đã vào vị trí chưa
        self.shoot_timer = pygame.time.get_ticks()
        self.shoot_interval = 1200
        self.spawn_pollution_timer = pygame.time.get_ticks()
        self.spawn_pollution_interval = 2000
        self.bob_phase = 0.0
        self.bob_amplitude = 28.0
        self.bob_speed = 2.5
        self.base_y = None
        # faces still kept internally for sprite rendering, but UI icons are removed per request
        try:
            f0 = None
            f1 = None
            face0_path = join(ASSETS_DIR, "boss", "0.png")
            face1_path = join(ASSETS_DIR, "boss", "1.png")
            if exists(face0_path):
                f0 = load_image(face0_path, (48,48))
            if exists(face1_path):
                f1 = load_image(face1_path, (48,48))
            if not f0:
                f0 = pygame.Surface((48,48), pygame.SRCALPHA)
                pygame.draw.circle(f0, (200,230,180), (24,24), 22)
                pygame.draw.circle(f0, (0,0,0), (16,18), 3)
                pygame.draw.circle(f0, (0,0,0), (32,18), 3)
                pygame.draw.arc(f0, (0,120,0), (8,10,32,28), math.pi/8, math.pi - math.pi/8, 3)
            if not f1:
                f1 = pygame.Surface((48,48), pygame.SRCALPHA)
                pygame.draw.circle(f1, (240,180,180), (24,24), 22)
                pygame.draw.polygon(f1, (0,0,0), [(12,14),(20,18),(12,22)])
                pygame.draw.polygon(f1, (0,0,0), [(36,14),(28,18),(36,22)])
                pygame.draw.line(f1, (160,0,0), (12,34), (36,34), 4)
        except Exception:
            f0 = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.circle(f0, (200,230,180), (24,24), 22)
            f1 = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.circle(f1, (240,180,180), (24,24), 22)
        self.faces = (f0, f1)
        self.hard_mode = False

    def update(self, dt):
        if not self.entered:
            self.rect.y += 90 * dt  # di chuyển xuống trong giai đoạn xuất hiện
            if self.rect.top >= 40:
                self.entered = True
                self.base_y = self.rect.y
        else:
            self.rect.x += self.direction.x * self.speed * dt  # di chuyển ngang
            if self.rect.left <= 40:
                self.rect.left = 40
                self.direction.x *= -1  # đổi hướng khi chạm biên
            if self.rect.right >= WINDOW_WIDTH - 40:
                self.rect.right = WINDOW_WIDTH - 40
                self.direction.x *= -1
            self.bob_phase += self.bob_speed * dt
            if self.base_y is None:
                self.base_y = self.rect.y
            bob_y = self.base_y + math.sin(self.bob_phase) * self.bob_amplitude  # tính bob (lên xuống)
            self.rect.y = int(bob_y)
        if self.frames:
            self.anim_index += 6 * dt
            self.image = self.frames[int(self.anim_index) % len(self.frames)]
            self.rect = self.image.get_rect(center=self.rect.center)
            try:
                self.mask = pygame.mask.from_surface(self.image)
            except Exception:
                pass
        if not self.hard_mode and self.health <= (self.max_health // 2):
            self.hard_mode = True
            self.shoot_interval = max(400, self.shoot_interval // 2)  # tăng tần suất bắn
            self.spawn_pollution_interval = max(600, self.spawn_pollution_interval // 2)
            self.bob_speed = 4.0
            self.bob_amplitude = 40.0

    def shoot(self, spawn_fn):  # spawn_fn là hàm callback để tạo đạn
        now = pygame.time.get_ticks()
        if now - self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = now
            if not self.hard_mode:
                centers = [self.rect.midbottom, (self.rect.centerx - 48, self.rect.bottom - 10), (self.rect.centerx + 48, self.rect.bottom - 10)]
            else:
                centers = [
                    (self.rect.centerx - 80, self.rect.bottom - 6),
                    (self.rect.centerx - 40, self.rect.bottom - 6),
                    (self.rect.centerx, self.rect.bottom - 6),
                    (self.rect.centerx + 40, self.rect.bottom - 6),
                    (self.rect.centerx + 80, self.rect.bottom - 6)
                ]
            for c in centers:
                spawn_fn(c)  # gọi callback tạo đạn tại mỗi center

    def spawn_pollution(self, spawn_fn, difficulty):
        now = pygame.time.get_ticks()
        interval = max(600, self.spawn_pollution_interval - difficulty*40)
        if now - self.spawn_pollution_timer >= interval:
            self.spawn_pollution_timer = now
            x = randint(self.rect.left+20, self.rect.right-20)
            spawn_fn((x, self.rect.bottom + 10), difficulty)  # spawn pollution ở dưới boss

# ---------- highscore helpers ----------
def load_highscore():
    try:
        if exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as f:  # mở file đọc
                return int(f.read().strip())  # trả về int
    except Exception:
        pass
    return 0  # fallback 0

def save_highscore(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:  # mở file ghi (ghi đè)
            f.write(str(int(score)))  # ghi điểm (chuyển thành int rồi str)
    except Exception:
        pass

# ---------- save game helper ----------
def save_game_state():
    """
    Lưu trạng thái game chính ra file SAVE_FILE (JSON).
    Ghi: score, high_score, difficulty, level, player pos & lives & shield,
    boss_spawned & boss health & pos (nếu có), state, and timestamp.
    """
    try:
        data = {
            "score": int(score),
            "high_score": int(high_score),
            "difficulty": int(difficulty),
            "level": int(level),
            "state": state,
            "timestamp_ms": pygame.time.get_ticks()
        }
        # player info
        if player:
            try:
                data["player"] = {
                    "lives": int(player.lives),
                    "pos": (int(player.rect.centerx), int(player.rect.centery)),
                    "shield": bool(player.shield),
                    "shield_time": int(player.shield_time),
                    "shield_duration": int(player.shield_duration)
                }
            except Exception:
                data["player"] = None
        else:
            data["player"] = None

        # boss info
        try:
            data["boss_spawned"] = bool(boss_spawned)
            if boss and boss_spawned:
                data["boss"] = {
                    "health": int(getattr(boss, "health", 0)),
                    "max_health": int(getattr(boss, "max_health", 0)),
                    "pos": (int(boss.rect.centerx), int(boss.rect.centery))
                }
            else:
                data["boss"] = None
        except Exception:
            data["boss_spawned"] = False
            data["boss"] = None

        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[save] Game saved to {SAVE_FILE}")
        try:
            # feedback âm thanh nếu có
            if 'menu_click_sound' in globals() and menu_click_sound:
                menu_click_sound.play()
        except Exception:
            pass
        return True
    except Exception as e:
        print("[save] Failed to save game state:", e)
        return False

# ---------- init pygame & mixer ----------
pygame.init()  # khởi tạo pygame (display, font, v.v.)
try:
    pygame.mixer.init()  # khởi tạo mixer nếu có
    pygame.mixer.set_num_channels(32)  # set số kênh audio để phát đồng thời
except Exception as e:
    print("[audio] pygame.mixer.init() failed or unavailable:", e)

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # tạo cửa sổ hiển thị
pygame.display.set_caption("Eco Shooter - UI Update")  # tiêu đề cửa sổ
clock = pygame.time.Clock()  # đồng hồ để quản lý FPS

# ---------- load assets (images, frames, extra UI images) ----------
player_img = None  # placeholder biến ảnh
meteor_img = None
star_img = None
laser_img = None
explosion_frames = []
boss_frames = None
boss_bullet_img = None
green_item_images = []
background_img = None

# Extra UI images requested
captain_img = None
epilogue_img = None
gameover_bg_img = None
win_bg_img = None

try:
    # player
    p_path = join(ASSETS_DIR, "player.png")
    if exists(p_path):
        player_img = load_image(p_path, (64,48))  # load player image nếu có

    # meteor
    meteor_path = join(ASSETS_DIR, "meteor.png")
    if exists(meteor_path):
        meteor_img = load_image(meteor_path, (64,64))
    else:
        meteor_img = load_image(None, (64,64))  # fallback placeholder

    # star
    star_path = join(ASSETS_DIR, "star.png")
    if exists(star_path):
        star_img = load_image(star_path, (3,3))
    else:
        star_img = load_image(None, (3,3))

    # laser
    laser_path = join(ASSETS_DIR, "laser.png")
    if exists(laser_path):
        laser_img = load_image(laser_path, (8,28))
    else:
        laser_img = load_image(None, (8,28))

    # explosion frames (0..20)
    for i in range(21):
        p = join(ASSETS_DIR, "explosion", f"{i}.png")
        if exists(p):
            explosion_frames.append(load_image(p))

    # boss frames
    boss_frames_tmp = []
    for i in range(12):
        p = join(ASSETS_DIR, "boss", f"{i}.png")
        if exists(p):
            boss_frames_tmp.append(load_image(p, (260,120)))
    if boss_frames_tmp:
        boss_frames = boss_frames_tmp

    # boss_bullet image
    bb = join(ASSETS_DIR, "boss_bullet.png")
    if exists(bb):
        boss_bullet_img = load_image(bb, (18,28))

    # green_item images
    for i in range(6):
        p = join(ASSETS_DIR, f"green_item{i}.png")
        if exists(p):
            green_item_images.append(load_image(p, (40,40)))

    # background
    bg_candidates = [join(ASSETS_DIR, "background.PNG"), join(ASSETS_DIR, "background.png")]
    for bp in bg_candidates:
        if exists(bp):
            background_img = load_image(bp, (WINDOW_WIDTH, WINDOW_HEIGHT))
            break

    # ---------------------------
    # Extra UI assets requested by user (with fallback to container path)
    # ---------------------------
    cap_candidates = [join(ASSETS_DIR, "captain.png"), join(ASSETS_DIR, "captain.PNG")]
    for cp in cap_candidates:
        if exists(cp):
            captain_img = load_image(cp, (160, 200))
            break

    # fallback: dev-provided image in container (added)
    dev_cap_path = "/mnt/data/c43735b4-9797-411d-92c3-454ba2222b92.png"
    try:
        if not captain_img and exists(dev_cap_path):
            captain_img = load_image(dev_cap_path, (160, 2000))
            print(f"[assets] Loaded captain image from container: {dev_cap_path}")
    except Exception as e:
        print(f"[assets] Failed loading dev captain image: {e}")

    epi_candidates = [join(ASSETS_DIR, "epilogue.png"), join(ASSETS_DIR, "epilogue.PNG")]
    for ep in epi_candidates:
        if exists(ep):
            epilogue_img = load_image(ep, (160, 220))
            break

except Exception as e:
    print("[assets] error loading assets:", e)

# ---------- sounds ----------
laser_sound = load_sound("laser.wav")  # load hiệu ứng laser
explosion_sound = load_sound("explosion.wav")
pickup_sound = load_sound("pickup.wav")
menu_click_sound = load_sound("menu_click.wav")
quiz_correct_sound = load_sound("quiz_correct.wav")
quiz_wrong_sound = load_sound("quiz_wrong.wav")
boss_spawn_sound = load_sound("damage.ogg")
music_loaded = False
if load_music("game_music.wav") or load_music("game_music.ogg") or load_music(join(AUDIO_SUBDIR, "game_music.wav")):
    try:
        pygame.mixer.music.set_volume(0.25)  # đặt volume nhạc nền
        pygame.mixer.music.play(loops=-1)  # phát lặp vô tận
    except Exception:
        pass

# ---------- fonts ----------
CUSTOM_FONT_PATH = join(ASSETS_DIR, "Oxanium-Bold.ttf")  # đường dẫn font tuỳ chỉnh
CUSTOM_FONT_AVAILABLE = False
try:
    big_font = pygame.font.Font(CUSTOM_FONT_PATH, 72)  # cố thử load font tuỳ chỉnh
    font = pygame.font.Font(CUSTOM_FONT_PATH, 36)
    small_font = pygame.font.Font(CUSTOM_FONT_PATH, 18)
    CUSTOM_FONT_AVAILABLE = True
except Exception:
    big_font = pygame.font.SysFont("Arial", 72)  # fallback fonts hệ thống
    font = pygame.font.SysFont("Arial", 19)
    small_font = pygame.font.SysFont("Arial", 18)
    CUSTOM_FONT_AVAILABLE = False

try:
    font_lives = pygame.font.Font(join(ASSETS_DIR, "DejaVuSans.ttf"), 22)
except Exception:
    font_lives = pygame.font.SysFont("Segoe UI Symbol", 22)

# ---------- text wrapping + render helper ----------
def wrap_lines(text, font_obj, max_width):  # tách text thành nhiều dòng tuân theo max_width
    lines = []
    paragraphs = text.split('\n')
    for para in paragraphs:
        words = para.split(' ')
        if not words:
            lines.append('')
            continue
        line = ''
        for word in words:
            test_line = line + (' ' if line else '') + word
            fw, fh = font_obj.size(test_line)
            if fw <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                if font_obj.size(word)[0] > max_width:
                    part = ''
                    for ch in word:
                        test_part = part + ch
                        if font_obj.size(test_part)[0] <= max_width:
                            part = test_part
                        else:
                            if part:
                                lines.append(part)
                            part = ch
                    if part:
                        line = part
                    else:
                        line = ''
                else:
                    line = word
        if line:
            lines.append(line)
    return lines

def render_wrapped(surface, text, font_name_or_path, starting_size, color, rect, min_font_size=12):  # render text tự co để vừa rect
    size = starting_size
    while size >= min_font_size:
        try:
            if CUSTOM_FONT_AVAILABLE and exists(CUSTOM_FONT_PATH):
                f = pygame.font.Font(CUSTOM_FONT_PATH, size)
            else:
                f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", size)
        except Exception:
            f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", size)
        lines = wrap_lines(text, f, rect.width)
        total_height = len(lines) * f.get_linesize()
        if total_height <= rect.height:
            y = rect.top
            for line in lines:
                surf = f.render(line, True, color)
                surface.blit(surf, (rect.left, y))
                y += f.get_linesize()
            return f, size
        size -= 1
    try:
        if CUSTOM_FONT_AVAILABLE and exists(CUSTOM_FONT_PATH):
            f = pygame.font.Font(CUSTOM_FONT_PATH, min_font_size)
        else:
            f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", min_font_size)
    except Exception:
        f = pygame.font.SysFont(font_name_or_path if font_name_or_path else "Arial", min_font_size)
    lines = wrap_lines(text, f, rect.width)
    y = rect.top
    for line in lines:
        surf = f.render(line, True, color)
        surface.blit(surf, (rect.left, y))
        y += f.get_linesize()
    return f, min_font_size

# ---------- groups & initial entities ----------
all_sprites = pygame.sprite.Group()  # nhóm chứa tất cả sprite
pollution_sprites = pygame.sprite.Group()  # nhóm kẻ thù
green_sprites = pygame.sprite.Group()  # nhóm vật phẩm xanh
laser_sprites = pygame.sprite.Group()  # nhóm đạn của player
explosion_sprites = pygame.sprite.Group()  # nhóm hiệu ứng nổ
boss_sprites = pygame.sprite.Group()  # nhóm boss
boss_bullets = pygame.sprite.Group()  # nhóm đạn boss

for _ in range(30):
    Star(all_sprites, star_img)  # tạo 30 sao nền

# ---------- game state ----------
score = 0
high_score = load_highscore()  # load highscore từ file
difficulty = 0
pollution_timer = pygame.time.get_ticks()
green_timer = pygame.time.get_ticks()
difficulty_time = pygame.time.get_ticks()
state = 'MAIN_MENU'  # trạng thái game (menu, playing...)
player = None
boss = None
mouse_pressed = False
mouse_pos = (0,0)
paused = False
boss_spawned = False
win_timer = 0
level = 0
current_quiz = None
quiz_message_timer = 0
quiz_message = ""
quiz_result_visible = False

# Flag để cho phép save 1 lần mỗi lần vào pause (auto-save on pause)
save_on_pause_allowed = True

# Save manual feedback
save_message = ""
save_message_timer = 0

# ---------- Visual Novel intro content ----------
vn_pages = [
    "Our mission is to save the planet: collect and recycle waste, encourage the use of fabric bags and reusable water bottles.",
    "On this journey, you will face sources of pollution: plastic waste, solid waste, and air pollution. Defeat them to reduce their impact.",
    "The final boss represents harmful consumption habits. Defeat the boss to help restore the environment and inspire the community.",
    "Remember: collect green items to gain educational information and power. Ready? Let’s set out and protect the planet!"
]
vn_page = 0

win_vn_pages = [
    "You have won! The boss – the symbol of polluting habits – has been defeated.",
    "The community is beginning to change: more people are using fabric bags, reusable bottles, and the coastline has less trash.",
    "Small actions create big differences. Thank you for protecting the planet!",
    "A happy ending: Everyone joins forces to preserve the environment. Press ENTER to return to the Menu."
]
win_vn_page = 0

# ---------- basic draw helpers ----------
def draw_text(surface, text, font_obj, color, pos):  # render text với font đã cho tại position
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(topleft=pos)
    surface.blit(txt, rect)
    return rect

def draw_centered(surface, text, font_obj, color, center):  # render text canh giữa
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(center=center)
    surface.blit(txt, rect)
    return rect

def draw_button(surface, rect, text, font_obj, mouse_pos, mouse_pressed, base_color, hover_color, click_sound=None):  # vẽ button cơ bản
    pygame.draw.rect(surface, base_color, rect, border_radius=12)
    hovered = rect.collidepoint(mouse_pos)
    if hovered:
        # slightly darker overlay to show hover
        pygame.draw.rect(surface, hover_color, rect, border_radius=12)
    txt = font_obj.render(text, True, WHITE)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)
    clicked = hovered and mouse_pressed
    if clicked and click_sound:
        try:
            click_sound.play()
        except Exception:
            pass
    return clicked

# ---------- spawn helpers ----------
def spawn_pollution_at(pos=None, difficulty=0):  # spawn đối tượng ô nhiễm
    surf = meteor_img if meteor_img else load_image(None, (64,64))
    if pos is None:
        x = randint(40, WINDOW_WIDTH - 40)
        y = -50
    else:
        x, y = pos
    Pollution(surf, (x, y), (all_sprites, pollution_sprites), difficulty)

def spawn_green_item():  # spawn vật phẩm xanh
    x = randint(40, WINDOW_WIDTH - 40)
    GreenItem((x, -20), (all_sprites, green_sprites), difficulty)

def spawn_boss_bullet_at(pos):  # spawn đạn boss, hỗ trợ ảnh nếu có
    if 'boss_bullet_img' in globals() and boss_bullet_img:
        BossBullet(pos, (all_sprites, boss_bullets))
    else:
        BossBullet((18,28), pos, (all_sprites, boss_bullets))

def player_shoot():  # hàm bắn của player
    global laser_sound
    if player and player.can_shoot:
        player.can_shoot = False
        player.laser_shoot_time = pygame.time.get_ticks()
        surf = laser_img if laser_img else load_image(None, (8,28))
        Laser(surf, player.rect.midtop, (all_sprites, laser_sprites))
        try:
            laser_sound.play()
        except Exception:
            pass

def spawn_boss(difficulty_level=0):  # khởi tạo boss
    global boss_spawned, boss
    boss_spawned = True
    boss = Boss((all_sprites, boss_sprites), frames=boss_frames)
    boss.health = 50 + difficulty_level * 15
    boss.max_health = boss.health
    try:
        boss_spawn_sound.play()
    except Exception:
        pass

def create_explosion(pos):
    AnimatedExplosion(explosion_frames, pos, (all_sprites, explosion_sprites), sound=explosion_sound)

def reset_game():  # đặt lại trạng thái game khi bắt đầu hoặc restart
    global score, difficulty, pollution_timer, green_timer, difficulty_time
    global state, player, boss_spawned, boss, win_timer, level, save_on_pause_allowed
    all_sprites.empty()
    pollution_sprites.empty()
    green_sprites.empty()
    laser_sprites.empty()
    explosion_sprites.empty()
    boss_sprites.empty()
    boss_bullets.empty()
    for _ in range(30):
        Star(all_sprites, star_img)
    player_surf = player_img if player_img else None
    player_obj = Player((all_sprites,), surf=player_surf)
    globals()['player'] = player_obj  # lưu player vào globals
    score = 0
    difficulty = 0
    level = 1
    pollution_timer = pygame.time.get_ticks()
    green_timer = pygame.time.get_ticks()
    difficulty_time = pygame.time.get_ticks()
    boss_spawned = False
    boss = None
    win_timer = 0
    # reset flag save when resetting game so next pause can auto-save once
    save_on_pause_allowed = True

reset_game()  # khởi tạo game lần đầu

# ---------- main loop ----------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # dt tính bằng giây (frame delta)
    now = pygame.time.get_ticks()  # thời gian hiện tại (ms)
    for event in pygame.event.get():  # xử lý event queue
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == 'MAIN_MENU':
                if event.key == pygame.K_RETURN:
                    state = 'VN_INTRO'
                    vn_page = 0
                elif event.key == pygame.K_i:
                    state = 'INSTRUCTIONS'
            elif state == 'INSTRUCTIONS':
                if event.key == pygame.K_ESCAPE:
                    state = 'MAIN_MENU'
            elif state == 'VN_INTRO':
                if event.key == pygame.K_RETURN:
                    vn_page += 1
                    if vn_page >= len(vn_pages):
                        reset_game()
                        state = 'PLAYING'
                elif event.key == pygame.K_ESCAPE:
                    state = 'MAIN_MENU'
            elif state == 'PLAYING':
                if event.key == pygame.K_SPACE:
                    player_shoot()
                if event.key == pygame.K_p:
                    # toggle pause immediately
                    paused = not paused
                    if paused:
                        # khi chuyển sang paused: auto-save 1 lần nếu được phép
                        if save_on_pause_allowed:
                            if save_game_state():
                                save_message = "Game auto-saved on pause."
                            else:
                                save_message = "Auto-save failed."
                            save_message_timer = now
                            save_on_pause_allowed = False
                    else:
                        # khi unpause: cho phép auto-save lại ở lần pause tiếp theo
                        save_on_pause_allowed = True
                if event.key == pygame.K_ESCAPE:
                    state = 'MAIN_MENU'
            elif state in ('GAME_OVER',):
                if event.key == pygame.K_RETURN:
                    state = 'MAIN_MENU'
            elif state == 'QUIZ':
                if event.key in (pygame.K_a, pygame.K_b, pygame.K_c):
                    ans = {pygame.K_a: "A", pygame.K_b: "B", pygame.K_c: "C"}[event.key]
                    if current_quiz:
                        if ans == current_quiz['correct']:
                            quiz_msg = "Correct!"
                            try:
                                quiz_correct_sound.play()
                            except Exception:
                                pass
                            score += 150
                        else:
                            quiz_msg = f"Wrong. The correct answer is {current_quiz['correct']}"
                            try:
                                quiz_wrong_sound.play()
                            except Exception:
                                pass
                        quiz_message = quiz_msg
                        quiz_message_timer = now
                        quiz_result_visible = True
                    state = 'PLAYING'
            elif state == 'WIN_VN':
                if event.key == pygame.K_RETURN:
                    win_vn_page += 1
                    if win_vn_page >= len(win_vn_pages):
                        state = 'MAIN_MENU'
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed = True
            mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = False
            mouse_pos = pygame.mouse.get_pos()

    if state == 'PLAYING' and not paused:
        if now - pollution_timer >= max(600, 1200 - difficulty * 50):
            pollution_timer = now
            spawn_pollution_at(difficulty=difficulty)
        if now - green_timer >= 3500:
            green_timer = now
            spawn_green_item()
        if now - difficulty_time >= 15000:
            difficulty_time = now
            difficulty += 1
            level += 1
        if not boss_spawned and score >= 2000 + difficulty * 1:
            spawn_boss(difficulty_level=difficulty)

    all_sprites.update(dt)  # cập nhật tất cả sprite

    if boss_spawned and boss_sprites:
        for b in boss_sprites:
            b.shoot(lambda pos: spawn_boss_bullet_at(pos))
            b.spawn_pollution(lambda pos, diff: spawn_pollution_at(pos=pos, difficulty=diff), difficulty)

    # collisions: pollution <-> laser
    hits = pygame.sprite.groupcollide(pollution_sprites, laser_sprites, True, True, pygame.sprite.collide_mask)
    for hit in hits:
        score += 50
        create_explosion(hit.rect.center)
        try:
            explosion_sound.play()
        except Exception:
            pass
        if randint(1,10) > 8:
            GreenItem(hit.rect.center, (all_sprites, green_sprites), difficulty)

    # boss hit by laser
    if boss_spawned:
        boss_hits = pygame.sprite.groupcollide(boss_sprites, laser_sprites, False, True, pygame.sprite.collide_mask)
        for b in boss_hits:
            b.health -= 1 + difficulty // 2
            create_explosion(b.rect.center)
            if b.health <= 0:
                create_explosion(b.rect.center)
                score += 2000
                b.kill()
                boss_spawned = False
                state = 'WIN_VN'
                win_vn_page = 0
                win_timer = now

    # player hit by boss bullets
    if player and not player.shield:
        hits = pygame.sprite.spritecollide(player, boss_bullets, True, pygame.sprite.collide_mask)
        if hits:
            player.lives -= 1
            create_explosion(player.rect.center)
            try:
                dmg = load_sound("damage.ogg")
                dmg.play()
            except Exception:
                pass
            if player.lives <= 0:
                state = 'GAME_OVER'
                if score > high_score:
                    save_highscore(score)
                    high_score = score

    # player hit by pollution
    if player and not player.shield:
        hits = pygame.sprite.spritecollide(player, pollution_sprites, True, pygame.sprite.collide_mask)
        if hits:
            player.lives -= 1
            create_explosion(player.rect.center)
            try:
                dmg = load_sound("damage.ogg")
                dmg.play()
            except Exception:
                pass
            if player.lives <= 0:
                state = 'GAME_OVER'
                if score > high_score:
                    save_highscore(score)
                    high_score = score

    # pickups
    if player:
        pickups = pygame.sprite.spritecollide(player, green_sprites, True, pygame.sprite.collide_mask)
        for p in pickups:
            st = getattr(p, 'subtype', None)
            try:
                pickup_sound.play()
            except Exception:
                pass
            if st == 'reusable_bag':
                score += 200
                quiz_message = educational_info.get('reusable_bag', "")
            elif st == 'water_bottle':
                score += 200
                quiz_message = educational_info.get('water_bottle', "")
            elif st == 'plant':
                player.lives = min(player.lives + 1, player.max_lives_display)
                quiz_message = educational_info.get('plant', "")
            elif st == 'solar_panel':
                player.shield = True
                player.shield_time = now
                quiz_message = educational_info.get('solar_panel', "")
            elif st == 'recycling_bin':
                score += 300
                quiz_message = educational_info.get('recycling_bin', "")
            quiz_message_timer = now
            quiz_result_visible = True
            if randint(0, 60) < 8:
                current_quiz = choice(questions)
                state = 'QUIZ'

    # ---------- render ----------
    # draw background if available
    if background_img:
        display_surface.blit(background_img, (0,0))
    else:
        display_surface.fill(BG_COLOR)

    if state == 'MAIN_MENU':
        draw_centered(display_surface, "ECO SHOOTER", big_font, CYAN, (WINDOW_WIDTH//2, 120))
        btn_w, btn_h = 360, 64
        start_rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, 240, btn_w, btn_h)
        instr_rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, 320, btn_w, btn_h)
        quit_rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, 400, btn_w, btn_h)

        if draw_button(display_surface, start_rect, "Start Game", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            state = 'VN_INTRO'
            vn_page = 0
            mouse_pressed = False
        if draw_button(display_surface, instr_rect, "Instructions", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            state = 'INSTRUCTIONS'; mouse_pressed = False
        if draw_button(display_surface, quit_rect, "Quit", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            running = False; mouse_pressed = False

        bar_w = btn_w
        bar_h = 48
        bx = WINDOW_WIDTH//2 - bar_w//2
        by = 520
        pygame.draw.rect(display_surface, (20,20,20,220), (bx, by, bar_w, bar_h), border_radius=8)
        draw_centered(display_surface, f"High Score: {high_score}", font, YELLOW, (WINDOW_WIDTH//2, by + bar_h//2))

    elif state == 'VN_INTRO':
        panel_w, panel_h = WINDOW_WIDTH - 160, 300
        panel_rect = pygame.Rect(80, WINDOW_HEIGHT//2 - panel_h//2, panel_w, panel_h)
        panel_s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_s.fill((12,12,12,230))
        pygame.draw.rect(panel_s, (80,80,80), panel_s.get_rect(), 2, border_radius=12)
        display_surface.blit(panel_s, panel_rect.topleft)

        # Character box (left) - now show captain image if available
        char_rect = pygame.Rect(panel_rect.left + 18, panel_rect.top + 24, 180, panel_h - 48)
        pygame.draw.rect(display_surface, (30,30,40), char_rect, border_radius=8)
        pygame.draw.rect(display_surface, (90,90,110), char_rect, 3, border_radius=8)
        draw_text(display_surface, "Captain", small_font, WHITE, (char_rect.left + 12, char_rect.top + 8))

        # draw captain image if provided; else placeholder box
        if captain_img:
            img_rect = captain_img.get_rect(center=(char_rect.left + char_rect.width//2, char_rect.top + char_rect.height//2))
            display_surface.blit(captain_img, img_rect)
        else:
            face_placeholder = pygame.Surface((char_rect.width - 24, char_rect.height - 56), pygame.SRCALPHA)
            pygame.draw.rect(face_placeholder, (120,120,120), face_placeholder.get_rect(), border_radius=8)
            display_surface.blit(face_placeholder, (char_rect.left + 12, char_rect.top + 36))

        # text area (right)
        text_area = pygame.Rect(char_rect.right + 20, panel_rect.top + 20, panel_rect.right - (char_rect.right + 40), panel_h - 80)
        font_name_to_use = "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial"
        page_text = vn_pages[vn_page] if vn_page < len(vn_pages) else ""
        render_wrapped(display_surface, page_text, font_name_to_use, 26, WHITE, text_area, min_font_size=14)
        draw_text(display_surface, f"Page {vn_page+1}/{len(vn_pages)} - Press ENTER or Next", small_font, (180,180,180), (text_area.left, text_area.bottom + 8))

        next_rect = pygame.Rect(panel_rect.right - 140, panel_rect.bottom - 60, 120, 44)
        if draw_button(display_surface, next_rect, "Next", small_font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
            vn_page += 1
            mouse_pressed = False
            if vn_page >= len(vn_pages):
                reset_game()
                state = 'PLAYING'

        skip_rect = pygame.Rect(panel_rect.left + 12, panel_rect.bottom - 60, 120, 44)
        if draw_button(display_surface, skip_rect, "Skip", small_font, mouse_pos, mouse_pressed, (80,80,80), (110,110,110), click_sound=menu_click_sound):
            state = 'MAIN_MENU'
            mouse_pressed = False

    elif state == 'INSTRUCTIONS':
        draw_centered(display_surface, "Instructions", big_font, MENU_BLUE, (WINDOW_WIDTH//2, 80))
        tips = [
            "Move: Arrow keys or WASD",
            "Shoot: SPACE (cooldown)",
            "Pause: P",
            "Collect green items to learn and gain bonuses.",
            "Answer quiz questions (A/B/C) for extra points.",
            "Pro tip: If text looks too big for your screen, try reducing the window size or font assets."
        ]
        y = 160
        for t in tips:
            rect = pygame.Rect(120, y, 760, 56)
            font_name_to_use = "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial"
            render_wrapped(display_surface, t, font_name_to_use, 28, WHITE, rect, min_font_size=14)
            y += 56
        draw_text(display_surface, "Press ESC to return to menu", small_font, WHITE, (120, y + 20))

    elif state in ('PLAYING', 'QUIZ'):
        all_sprites.draw(display_surface)  # vẽ tất cả sprite

        panel_w, panel_h = 520, 100
        panel_rect = pygame.Rect(8, 8, panel_w, panel_h)
        s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        s.fill((20,20,20,200))
        pygame.draw.rect(s, (80,80,80), s.get_rect(), 2, border_radius=8)
        display_surface.blit(s, panel_rect.topleft)

        draw_text(display_surface, f"Score: {score}", font, WHITE, (16, 14))
        draw_text(display_surface, f"High: {high_score}", small_font, YELLOW, (16, 56))

        hearts = min(player.lives if player else 0, 10)
        lives_text = "❤ " * hearts
        draw_text(display_surface, f"Lives: {lives_text}", font_lives, RED, (220, 16))
        draw_text(display_surface, f"Level: {level}", small_font, WHITE, (220, 56))

        if player and player.shield:
            remaining = max(0, player.shield_duration - (now - player.shield_time))
            ratio = remaining / player.shield_duration
            bar_w = 200; bar_h = 10
            x = WINDOW_WIDTH - bar_w - 16; y = 20
            pygame.draw.rect(display_surface, (60,60,60), (x, y, bar_w, bar_h))
            pygame.draw.rect(display_surface, (0,180,255), (x, y, int(bar_w*ratio), bar_h))

        # ---------- Boss health bar (NO ICONS) ----------
        if boss_spawned and boss_sprites:
            for b in boss_sprites:
                bar_w = 420; bar_h = 18
                left_padding = 12
                right_padding = 12
                available_left = panel_rect.right + left_padding
                available_width = WINDOW_WIDTH - available_left - right_padding
                safe_bar_w = min(bar_w, max(120, available_width))
                center_x = WINDOW_WIDTH//2 - safe_bar_w//2
                safe_x = center_x if center_x >= available_left else available_left
                if safe_x + safe_bar_w > WINDOW_WIDTH - right_padding:
                    safe_bar_w = WINDOW_WIDTH - right_padding - safe_x
                safe_bar_w = max(120, safe_bar_w)
                x = int(safe_x)
                y = 8
                pygame.draw.rect(display_surface, (80,80,80), (x, y, safe_bar_w, bar_h))
                ratio = max(0, b.health) / max(1, b.max_health)
                pygame.draw.rect(display_surface, (200,40,40), (x, y, int(safe_bar_w*ratio), bar_h))
                label = small_font.render("BOSS", True, WHITE)
                label_rect = label.get_rect(center=(x + safe_bar_w//2, y + bar_h + 12))
                display_surface.blit(label, label_rect)

        if paused:
            # overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            display_surface.blit(overlay, (0,0))

            # Title: PAUSED (căn thẳng, to rõ)
            title_y = WINDOW_HEIGHT//2 - 160
            draw_centered(display_surface, "PAUSED", big_font, YELLOW, (WINDOW_WIDTH//2, title_y))

            # Button layout: aligned & straight (centered vertically under title)
            btn_w = 420  # fixed width to ensure straight alignment
            btn_h = 64
            gap = 20
            # compute top of first button so the whole block is centered under the title
            buttons_total_height = 3 * btn_h + 2 * gap
            start_y = title_y + 48  # small gap under title
            # centers the block horizontally
            cx = WINDOW_WIDTH//2 - btn_w//2

            # Individual rects (stacked)
            save_rect = pygame.Rect(cx, start_y, btn_w, btn_h)
            resume_rect = pygame.Rect(cx, start_y + btn_h + gap, btn_w, btn_h)
            menu_rect = pygame.Rect(cx, start_y + 2*(btn_h + gap), btn_w, btn_h)

            # Draw buttons with consistent style
            # Save button: manual save allowed any time while paused
            if draw_button(display_surface, save_rect, "Save Game", font, mouse_pos, mouse_pressed, (0,120,220), (0,90,180), click_sound=menu_click_sound):
                ok = save_game_state()
                if ok:
                    save_message = "Game saved (manual)."
                else:
                    save_message = "Save failed."
                save_message_timer = now
                mouse_pressed = False  # prevent repeated triggers

            # Resume button: unpause immediately
            if draw_button(display_surface, resume_rect, "Resume", font, mouse_pos, mouse_pressed, MENU_BLUE, BLUE, click_sound=menu_click_sound):
                paused = False
                # when resuming, allow next auto-save on next pause
                save_on_pause_allowed = True
                mouse_pressed = False

            # Main Menu button: go back to main menu (unpause -> menu)
            if draw_button(display_surface, menu_rect, "Return to Menu", font, mouse_pos, mouse_pressed, (80,80,80), (110,110,110), click_sound=menu_click_sound):
                paused = False
                state = 'MAIN_MENU'
                mouse_pressed = False

            # small explanatory line under the buttons (optional)
            hint_y = start_y + 3*(btn_h + gap) + 12
            draw_centered(display_surface, "Tip: Press P to toggle Pause. Click Save to store progress.", small_font, (200,200,200), (WINDOW_WIDTH//2, hint_y))

        if state == 'QUIZ' and current_quiz:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,190))
            display_surface.blit(overlay, (0,0))
            draw_centered(display_surface, "QUIZ TIME!", big_font, CYAN, (WINDOW_WIDTH//2, 100))
            q_rect = pygame.Rect(120, 180, WINDOW_WIDTH - 240, 96)
            font_name_to_use = "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial"
            render_wrapped(display_surface, current_quiz['question'], font_name_to_use, 28, WHITE, q_rect, min_font_size=14)
            opt_y = q_rect.bottom + 12
            opt_rect = pygame.Rect(160, opt_y, WINDOW_WIDTH - 320, 48 * len(current_quiz['options']))
            options_text = '\n'.join(current_quiz['options'])
            render_wrapped(display_surface, options_text, font_name_to_use, 26, LIME, opt_rect, min_font_size=14)
            draw_text(display_surface, "Press A / B / C to answer", small_font, WHITE, (120, opt_rect.bottom + 12))

        if quiz_result_visible and now - quiz_message_timer < 4000:
            box_w, box_h = 720, 96
            box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box.fill((20,20,20,220))
            pygame.draw.rect(box, (80,80,80), box.get_rect(), 2, border_radius=10)
            display_surface.blit(box, (WINDOW_WIDTH//2 - box_w//2, WINDOW_HEIGHT - 140))
            msg_rect = pygame.Rect(WINDOW_WIDTH//2 - box_w//2 + 12, WINDOW_HEIGHT - 140 + 12, box_w - 24, box_h - 24)
            render_wrapped(display_surface, quiz_message, "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial", 18, WHITE, msg_rect, min_font_size=12)
        elif quiz_result_visible and now - quiz_message_timer >= 4000:
            quiz_result_visible = False
            quiz_message = ""

        # save manual feedback display (small box near top-right)
        if save_message and now - save_message_timer < SAVE_MESSAGE_DURATION:
            sm_w, sm_h = 320, 48
            sm_x = WINDOW_WIDTH - sm_w - 16
            sm_y = 16
            sm = pygame.Surface((sm_w, sm_h), pygame.SRCALPHA)
            sm.fill((20,20,20,220))
            pygame.draw.rect(sm, (80,80,80), sm.get_rect(), 2, border_radius=8)
            display_surface.blit(sm, (sm_x, sm_y))
            draw_centered(display_surface, save_message, small_font, YELLOW, (sm_x + sm_w//2, sm_y + sm_h//2))
        elif save_message and now - save_message_timer >= SAVE_MESSAGE_DURATION:
            save_message = ""
            save_message_timer = 0

    elif state == 'GAME_OVER':
        # draw game over background image if available; else dim & gradient rectangle
        if gameover_bg_img:
            display_surface.blit(gameover_bg_img, (0,0))
        else:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((30, 10, 10))
            display_surface.blit(overlay, (0,0))
        draw_centered(display_surface, "GAME OVER", big_font, RED, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        draw_centered(display_surface, f"Score: {score}", font, WHITE, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        draw_centered(display_surface, f"High Score: {high_score}", small_font, YELLOW, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
        draw_centered(display_surface, "Press ENTER to return to Menu", small_font, WHITE, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 140))

    elif state == 'WIN_VN':
        # Win epilogue: draw win background if exists
        if win_bg_img:
            display_surface.blit(win_bg_img, (0,0))
        else:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10,40,10,120))
            display_surface.blit(overlay, (0,0))

        panel_w, panel_h = WINDOW_WIDTH - 160, 300
        panel_rect = pygame.Rect(80, WINDOW_HEIGHT//2 - panel_h//2, panel_w, panel_h)
        panel_s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_s.fill((10,40,10,200))
        pygame.draw.rect(panel_s, (80,80,80), panel_s.get_rect(), 2, border_radius=12)
        display_surface.blit(panel_s, panel_rect.topleft)

        # character/celebration box: now attempt to draw epilogue image
        char_rect = pygame.Rect(panel_rect.left + 18, panel_rect.top + 24, 180, panel_h - 48)
        pygame.draw.rect(display_surface, (40,40,30), char_rect, border_radius=8)
        pygame.draw.rect(display_surface, (110,110,90), char_rect, 3, border_radius=8)
        draw_text(display_surface, "Epilogue", small_font, WHITE, (char_rect.left + 12, char_rect.top + 8))

        if epilogue_img:
            img_rect = epilogue_img.get_rect(center=(char_rect.left + char_rect.width//2, char_rect.top + char_rect.height//2))
            display_surface.blit(epilogue_img, img_rect)
        else:
            face_placeholder = pygame.Surface((char_rect.width - 24, char_rect.height - 56), pygame.SRCALPHA)
            pygame.draw.rect(face_placeholder, (160,220,160), face_placeholder.get_rect(), border_radius=8)
            display_surface.blit(face_placeholder, (char_rect.left + 12, char_rect.top + 36))

        text_area = pygame.Rect(char_rect.right + 20, panel_rect.top + 20, panel_rect.right - (char_rect.right + 40), panel_h - 80)
        page_text = win_vn_pages[win_vn_page] if win_vn_page < len(win_vn_pages) else ""
        render_wrapped(display_surface, page_text, "Oxanium-Bold.ttf" if CUSTOM_FONT_AVAILABLE else "Arial", 24, WHITE, text_area, min_font_size=14)
        draw_text(display_surface, f"Page {win_vn_page+1}/{len(win_vn_pages)} - Press ENTER to continue", small_font, (220,220,220), (text_area.left, text_area.bottom + 8))

    pygame.display.flip()  # cập nhật toàn bộ màn hình

# ---------- cleanup ----------
try:
    pygame.mixer.quit()
except Exception:
    pass
pygame.quit()  # thoát pygame. pause menu layout fixed (buttons straight & centered)
