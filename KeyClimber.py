# Key Climber - 2D Platformer Game with Pygame Zero
import pgzrun
from pygame import Rect

# Window and physics configuration
WIDTH, HEIGHT = 960, 540
TILE_SIZE, ROWS, COLS, GRAVITY = 64, 15, 30, 0.6

# Global game state
player, enemies, objects, solid_tiles, tiles_data = None, [], [], [], []
menu_buttons, win_buttons, gameover_buttons = [], [], []
camera_x = camera_y = 0
game_state, lives, has_key, music_on, sounds_on = 'menu', 3, False, True, True

def load_map():
    """Loads map from CSV file and creates solid tiles for collision"""
    global tiles_data, solid_tiles
    tiles_data, solid_tiles = [], []
    valid_row = 0
    with open('terrain_map.csv') as f:
        for line in f:
            if not line.strip(): continue
            if valid_row >= ROWS: break
            for col, tid in enumerate(line.strip().split(',')):
                tid = int(tid)
                if tid >= 0:
                    x, y = col * TILE_SIZE, valid_row * TILE_SIZE
                    tiles_data.append((tid, x, y))
                    solid_tiles.append(Rect(col * TILE_SIZE, valid_row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            valid_row += 1

# ===== GAME CLASSES =====

class Button:
    """Clickable button for menu interface"""
    def __init__(self, text, x, y, width, height, action):
        self.text, self.x, self.y, self.width, self.height, self.action = text, x, y, width, height, action
        self.hovered = False
    
    def contains_point(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height
    
    def draw(self):
        color = (100, 200, 100) if self.hovered else (70, 130, 70)
        screen.draw.filled_rect(Rect(self.x, self.y, self.width, self.height), color)
        screen.draw.text(self.text, center=(self.x + self.width // 2, self.y + self.height // 2), fontsize=30, color='white')

class Player:
    """Main character with movement, collision and sprite animation"""
    def __init__(self, x, y):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.frame = 0
        self.w = TILE_SIZE
        self.h = TILE_SIZE
        self.imgs = ['characters/default/character_yellow_idle', 'characters/default/character_yellow_walk_a', 'characters/default/character_yellow_walk_b']
    
    def update(self):
        self.vx = 0
        if keyboard.left: self.vx = -4
        if keyboard.right: self.vx = 4
        if keyboard.space and self.on_ground: 
            self.vy = -16
            if sounds_on: 
                try: sounds.sfx_jump.play()
                except: pass
        self.vy += GRAVITY
        self.x += self.vx
        self.check_collision_x()
        self.y += self.vy
        self.check_collision_y()
        if self.vx != 0 or not self.on_ground:
            self.frame = (self.frame + 0.15) % len(self.imgs)
        else:
            self.frame = 0 
        if self.y >= (ROWS - 2) * TILE_SIZE: self.die()
    
    def check_collision_x(self):
        r = self.get_rect()
        for tile in solid_tiles:
            if r.colliderect(tile):
                if self.vx > 0: 
                    self.x = tile.left - self.w - TILE_SIZE // 2
                elif self.vx < 0: 
                    self.x = tile.right - TILE_SIZE // 2
    
    def check_collision_y(self):
        r = self.get_rect()
        self.on_ground = False
        for tile in solid_tiles:
            if r.colliderect(tile):
                if self.vy > 0:
                    self.y = tile.top - self.h - TILE_SIZE
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile.bottom - TILE_SIZE
                    self.vy = 0
    
    def die(self):
        global game_state, lives
        lives -= 1
        if sounds_on: 
            try: sounds.sfx_hurt.play()
            except: pass
        if lives <= 0:
            game_state = 'gameover'
            if sounds_on:
                try: sounds.sfx_disappear.play()
                except: pass
        else:
            init_game()
    
    def get_rect(self):
        return Rect(self.x + TILE_SIZE // 2, self.y + TILE_SIZE, self.w, self.h)
    
    def draw(self): 
        screen.blit(self.imgs[int(self.frame)], (self.x - camera_x, self.y - camera_y))

class Enemy:
    """Enemies with auto-patrol and different speeds per type"""
    def __init__(self, kind, x, y, move_range):
        self.kind, self.w, self.h, self.range, self.frame = kind, 48, 48, move_range*TILE_SIZE, 0
        self.x, self.y, self.origin_x = x*TILE_SIZE, y*TILE_SIZE, x*TILE_SIZE
        self.speed = 4.0 if kind == 'mouse' else 1.2
        self.vx = self.speed
        
        if kind == 'bee': self.imgs = ['enemies/default/bee_a', 'enemies/default/bee_b', 'enemies/default/bee_rest']
        elif kind == 'mouse': self.imgs = ['enemies/default/mouse_walk_a', 'enemies/default/mouse_walk_b', 'enemies/default/mouse_rest']
        elif kind == 'slime_fire': self.imgs = ['enemies/default/slime_fire_walk_a', 'enemies/default/slime_fire_walk_b', 'enemies/default/slime_fire_rest']
        elif kind == 'slime_spike': self.imgs = ['enemies/default/slime_spike_walk_a', 'enemies/default/slime_spike_walk_b', 'enemies/default/slime_spike_rest']
    
    def update(self):
        if self.range > 0:
            self.x += self.vx
            if self.x >= self.origin_x + self.range: self.x, self.vx = self.origin_x + self.range, -self.speed
            elif self.x <= self.origin_x: self.x, self.vx = self.origin_x, self.speed
        # Animate sprite (moving or idle)
        self.frame = (self.frame + 0.1) % len(self.imgs)
    
    def get_rect(self): return Rect(self.x, self.y, self.w, self.h)
    def draw(self): screen.blit(self.imgs[int(self.frame)], (self.x - camera_x, self.y - camera_y))

class Item:
    """Collectible objects (key and door)"""
    def __init__(self, kind, x, y):
        self.kind, self.x, self.y, self.collected = kind, x*TILE_SIZE, y*TILE_SIZE, False
        sprites = {'door': 'sprites/door_closed', 'door_top': 'sprites/door_closed_top', 'key': 'sprites/key_yellow'}
        self.img = sprites.get(kind, 'sprites/key_yellow')
    
    def get_rect(self): return Rect(self.x, self.y, 64, 64)
    def draw(self):
        if not self.collected: screen.blit(self.img, (self.x - camera_x, self.y - camera_y))

# ===== INITIALIZATION AND MENUS =====

def init_game():
    """Initializes new game with player, enemies and objects"""
    global player, enemies, objects, game_state, camera_x, camera_y, has_key
    has_key, camera_x, camera_y, game_state = False, 0, 0, 'playing'
    if music_on:
        try:
            music.play('fundo')
            music.set_volume(0.3)
        except: pass
    player = Player(0, 12)
    enemies = [
        Enemy('bee', 18, 7, 5),
        Enemy('bee', 8, 7, 7),
        Enemy('slime_fire', 10, 13, 2),
        Enemy('slime_spike', 16, 12, 2),
        Enemy('slime_spike', 20, 12, 2),
        Enemy('mouse', 5, 2, 23)
    ]
    objects = [
        Item('door', 29, 2),
        Item('door_top', 29, 1),
        Item('key', 3, 8)
    ]

def create_menu_buttons():
    global menu_buttons
    btn_w, btn_h = 250, 50
    start_x = WIDTH // 2 - btn_w // 2
    menu_buttons = [
        Button('START GAME', start_x, 220, btn_w, btn_h, 'start'),
        Button('MUSIC: ON' if music_on else 'MUSIC: OFF', start_x, 290, btn_w, btn_h, 'music'),
        Button('SOUNDS: ON' if sounds_on else 'SOUNDS: OFF', start_x, 360, btn_w, btn_h, 'sounds'),
        Button('EXIT', start_x, 430, btn_w, btn_h, 'exit')
    ]

def create_win_buttons():
    global win_buttons
    btn_w, btn_h = 250, 50
    start_x = WIDTH // 2 - btn_w // 2
    win_buttons = [
        Button('PLAY AGAIN', start_x, HEIGHT // 2 + 60, btn_w, btn_h, 'restart'),
        Button('MAIN MENU', start_x, HEIGHT // 2 + 130, btn_w, btn_h, 'menu')
    ]

def create_gameover_buttons():
    global gameover_buttons
    btn_w, btn_h = 250, 50
    start_x = WIDTH // 2 - btn_w // 2
    gameover_buttons = [
        Button('TRY AGAIN', start_x, HEIGHT // 2 + 60, btn_w, btn_h, 'restart'),
        Button('MAIN MENU', start_x, HEIGHT // 2 + 130, btn_w, btn_h, 'menu')
    ]

def init_menu():
    create_menu_buttons()
    create_win_buttons()
    create_gameover_buttons()
    if music_on:
        try:
            music.play('fundo')
            music.set_volume(0.3)
        except: pass

# ===== GAME LOGIC =====

def update_camera():
    """Updates camera position following the player"""
    global camera_x, camera_y
    camera_x = max(0, min(int(player.x + player.w//2 - WIDTH//2), COLS*TILE_SIZE - WIDTH))
    camera_y = max(0, min(int(player.y + player.h//2 - HEIGHT//2), ROWS*TILE_SIZE - HEIGHT))

def check_collisions():
    """Checks collisions with enemies and collectible objects"""
    global has_key, game_state
    player_rect = player.get_rect()
    
    for enemy in enemies:
        if player_rect.colliderect(enemy.get_rect()):
            player.die()
            return
    
    for obj in objects:
        if player_rect.colliderect(obj.get_rect()):
            if obj.kind == 'key' and not obj.collected:
                obj.collected, has_key = True, True
                if sounds_on: 
                    try: sounds.sfx_coin.play()
                    except: pass
            elif obj.kind == 'door' and has_key:
                game_state = 'win'
                if sounds_on: 
                    try: sounds.sfx_gem.play()
                    except: pass

def update():
    """Updates game state"""
    if game_state == 'playing':
        player.update()
        for enemy in enemies: enemy.update()
        check_collisions()
        update_camera()

# ===== RENDERING =====

def draw():
    if game_state == 'menu':
        for y in range(HEIGHT):
            color_val = int(20 + 40 * y / HEIGHT)
            screen.draw.line((0, y), (WIDTH, y), (color_val//2, color_val//2, color_val))
        
        screen.draw.text('KEY CLIMBER', center=(WIDTH//2 + 4, HEIGHT//4 + 4), fontsize=100, color='black')
        screen.draw.text('KEY CLIMBER', center=(WIDTH//2, HEIGHT//4), fontsize=100, color='gold')
        
        for btn in menu_buttons: btn.draw()
        
        screen.draw.text('Click on buttons to interact', center=(WIDTH//2, HEIGHT - 40), fontsize=20, color='gray')
    elif game_state == 'playing':
        for y in range(HEIGHT):
            screen.draw.line((0,y), (WIDTH,y), (int(100+60*y/HEIGHT), int(90+40*y/HEIGHT), int(70+20*y/HEIGHT)))
        for tid, tx, ty in tiles_data:
            if tx+TILE_SIZE >= camera_x and tx <= camera_x+WIDTH and ty+TILE_SIZE >= camera_y and ty <= camera_y+HEIGHT:
                screen.blit(f'sprites/{tid}', (tx-camera_x, ty-camera_y))
        player.draw()
        for enemy in enemies: enemy.draw()
        for obj in objects: obj.draw()
        
        for i in range(lives): screen.blit('sprites/heart', (10+i*40, 10))
        if has_key: screen.blit('sprites/key_yellow', (WIDTH-74, 10))
        screen.draw.text('ESC=Menu', (WIDTH-120, HEIGHT-30), fontsize=20, color='white')
    elif game_state == 'win':
        for y in range(HEIGHT):
            color_val = int(20 + 60 * y / HEIGHT)
            screen.draw.line((0, y), (WIDTH, y), (0, color_val//2, 0))
        
        screen.draw.text('YOU WIN!', center=(WIDTH//2 + 3, HEIGHT//2-83), fontsize=90, color='darkgreen')
        screen.draw.text('YOU WIN!', center=(WIDTH//2, HEIGHT//2-80), fontsize=90, color='gold')
        
        for btn in win_buttons: btn.draw()
    elif game_state == 'gameover':
        for y in range(HEIGHT):
            color_val = int(10 + 30 * y / HEIGHT)
            screen.draw.line((0, y), (WIDTH, y), (color_val, 0, 0))
        
        screen.draw.text('GAME OVER', center=(WIDTH//2 + 4, HEIGHT//2-104), fontsize=100, color='black')
        screen.draw.text('GAME OVER', center=(WIDTH//2, HEIGHT//2-100), fontsize=100, color='red')
        screen.draw.text('You lost all lives!', center=(WIDTH//2, HEIGHT//2-20), fontsize=30, color='orange')
        
        for btn in gameover_buttons: btn.draw()

# ===== EVENTS =====

def on_mouse_move(pos):
    """Detects button hover"""
    if game_state == 'menu':
        for btn in menu_buttons:
            btn.hovered = btn.contains_point(pos)
    elif game_state == 'win':
        for btn in win_buttons:
            btn.hovered = btn.contains_point(pos)
    elif game_state == 'gameover':
        for btn in gameover_buttons:
            btn.hovered = btn.contains_point(pos)

def on_mouse_down(pos):
    """Processes button clicks"""
    global sounds_on, music_on, game_state, lives, has_key
    if game_state == 'menu':
        for btn in menu_buttons:
            if btn.contains_point(pos):
                if btn.action == 'start':
                    init_game()
                    if sounds_on:
                        try: sounds.sfx_select.play()
                        except: pass
                elif btn.action == 'music':
                    music_on = not music_on
                    if music_on:
                        try:
                            music.play('fundo')
                            music.set_volume(0.3)
                        except: pass
                    else:
                        try: music.stop()
                        except: pass
                    create_menu_buttons()
                elif btn.action == 'sounds':
                    sounds_on = not sounds_on
                    create_menu_buttons()
                elif btn.action == 'exit':
                    exit()
    
    elif game_state == 'win':
        for btn in win_buttons:
            if btn.contains_point(pos):
                if btn.action == 'restart':
                    lives = 3
                    has_key = False
                    init_game()
                elif btn.action == 'menu':
                    game_state = 'menu'
                    init_menu()
    
    elif game_state == 'gameover':
        for btn in gameover_buttons:
            if btn.contains_point(pos):
                if btn.action == 'restart':
                    lives = 3
                    has_key = False
                    init_game()
                elif btn.action == 'menu':
                    lives = 3
                    has_key = False
                    game_state = 'menu'
                    init_menu()

def on_key_down(key):
    """Processes ESC key during gameplay"""
    global game_state
    
    if game_state == 'playing':
        if key == keys.ESCAPE:
            game_state = 'menu'
            init_menu()

# ===== ENTRY POINT =====
load_map()
init_menu()
pgzrun.go()
