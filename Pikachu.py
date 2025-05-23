import pygame
import sys
import random
import time
import os
import collections
from pygame.locals import *

# Constants
FPS = 30
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BOX_SIZE = 70
BOARD_WIDTH = 14
BOARD_HEIGHT = 9
NUM_ANIMALS_ON_BOARD = 21
NUM_SAME_ANIMALS = 4
TIME_BAR_LENGTH = 300
TIME_BAR_WIDTH = 30
LEVEL_MAX = 5
INITIAL_LIVES = 3
GAME_TIME = 180
HINT_INTERVAL = 25

# Colors
GRAY = (100, 100, 100)
NAVY_BLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BOLD_GREEN = (0, 175, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)

class AssetManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.animals = {}
        self.backgrounds = []
        self.music = []
        self.sounds = {}
        self.effect_sounds = []
        self._load_assets()

    def _load_assets(self):
        # Animal icons
        icons_dir = os.path.join(self.base_path, 'animal_icon')
        for idx, fname in enumerate(os.listdir(icons_dir), start=1):
            img = pygame.image.load(os.path.join(icons_dir, fname))
            self.animals[idx] = pygame.transform.scale(img, (BOX_SIZE, BOX_SIZE))

        # Background images
        bg_dir = os.path.join(self.base_path, 'animal_background')
        for fname in sorted(os.listdir(bg_dir)):
            img = pygame.image.load(os.path.join(bg_dir, fname))
            self.backgrounds.append(pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT)))

        # Music tracks
        for i in range(1, 6):
            path = os.path.join(self.base_path, f'animal_music/bg_music_{i}.mp3')
            self.music.append(path)

        # Sounds
        self.sounds['click'] = pygame.mixer.Sound(os.path.join(self.base_path, 'gui_button_click.mp3'))
        self.sounds['correct_sound'] = pygame.mixer.Sound(os.path.join(self.base_path, 'correct_sound.mp3'))
        self.sounds['wrong_sound'] = pygame.mixer.Sound(os.path.join(self.base_path, 'wrong_sound.mp3'))

        # Effect sounds
        eff_dir = os.path.join(self.base_path, 'sound_effect')
        for fname in os.listdir(eff_dir):
            snd = pygame.mixer.Sound(os.path.join(eff_dir, fname))
            self.effect_sounds.append(snd)

        # Heart icon
        heart_path = os.path.join(self.base_path, 'heart.png')
        img = pygame.image.load(heart_path)
        self.heart = pygame.transform.scale(img, (BOX_SIZE, BOX_SIZE))

class Board:
    def __init__(self):
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.grid = []
        self._populate()

    def _populate(self):
        ids = list(asset_manager.animals.keys())
        random.shuffle(ids)
        selected = ids[:NUM_ANIMALS_ON_BOARD] * NUM_SAME_ANIMALS
        random.shuffle(selected)
        self.grid = [[0]*self.width for _ in range(self.height)]
        k = 0
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                self.grid[y][x] = selected[k]
                k += 1

    def is_complete(self):
        return all(cell == 0 for row in self.grid for cell in row)

    def get_hint(self):
        pos = collections.defaultdict(list)
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != 0:
                    pos[self.grid[y][x]].append((y, x))
        for val, cells in pos.items():
            for (y1, x1), (y2, x2) in zip(cells, cells[1:]):
                if self._bfs(y1, x1, y2, x2):
                    return [(y1, x1), (y2, x2)]
        return []

    def reset(self):
        nonzero = [self.grid[y][x] for y in range(self.height) for x in range(self.width) if self.grid[y][x] != 0]
        while True:
            random.shuffle(nonzero)
            if any(self.grid[y][x] != nonzero[i] for i,(y,x) in enumerate(( (yy,xx) for yy in range(self.height) for xx in range(self.width) if self.grid[yy][xx]!=0 ))):
                break
        it = iter(nonzero)
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != 0:
                    self.grid[y][x] = next(it)

    def alter(self, y1, x1, y2, x2, level):
        def compress_line(line, forward=True):
            vals = [v for v in line if v!=0]
            if not forward:
                vals = [0]*(len(line)-len(vals)) + vals
            else:
                vals = vals + [0]*(len(line)-len(vals))
            return vals

        if level == 2:
            for x in (x1, x2):
                col = [self.grid[y][x] for y in range(self.height)]
                new = compress_line(col, forward=True)
                for y in range(self.height): self.grid[y][x] = new[y]
        if level == 3:
            for x in (x1, x2):
                col = [self.grid[y][x] for y in range(self.height)]
                new = compress_line(col, forward=False)
                for y in range(self.height): self.grid[y][x] = new[y]
        if level == 4:
            for y in (y1, y2):
                row = self.grid[y]
                new = compress_line(row, forward=True)
                self.grid[y] = new
        if level == 5:
            for y in (y1, y2):
                row = self.grid[y]
                new = compress_line(row, forward=False)
                self.grid[y] = new

    def _bfs(self, y1, x1, y2, x2):
        if self.grid[y1][x1] != self.grid[y2][x2]: return []
        n, m = self.height, self.width
        q = collections.deque([(y1,x1,0,None)])
        visited = set([(y1,x1,0,None)])
        parent = {}
        dirs = [(-1,0,'up'),(1,0,'down'),(0,-1,'left'),(0,1,'right')]
        while q:
            y,x,turns,dir0 = q.popleft()
            if (y,x)==(y2,x2):
                path=[]
                cur=(y,x,turns,dir0)
                while cur!=(y1,x1,0,None):
                    path.append((cur[0],cur[1]))
                    cur=parent[cur]
                path.append((y1,x1))
                return list(reversed(path))
            for dy,dx,nd in dirs:
                ny, nx = y+dy, x+dx
                if 0<=ny<n and 0<=nx<m and (self.grid[ny][nx]==0 or (ny,nx)==(y2,x2)):
                    nturns = turns + (0 if dir0==nd or dir0 is None else 1)
                    state=(ny,nx,nturns,nd)
                    if nturns<=2 and state not in visited:
                        visited.add(state)
                        parent[state]=(y,x,turns,dir0)
                        q.append(state)
        return []

class Game:
    def __init__(self, path):
        pygame.init()
        pygame.mixer.pre_init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Matching Animals')
        self.path = path
        global asset_manager
        asset_manager = AssetManager(path)
        self.level = 1
        self.lives = INITIAL_LIVES

        font_path = os.path.join(self.path, "animal_fonts/DungeonFont.ttf")
        self.font_big = pygame.font.Font(font_path, 60)
        self.font_small = pygame.font.Font(font_path, 45)

        # default volumes
        self.music_volume = 0.5
        self.sfx_volume   = 0.5
        pygame.mixer.music.set_volume(self.music_volume)
        for snd in asset_manager.sounds.values():
            snd.set_volume(self.sfx_volume)

    def run(self):
        while True:
            self.show_start_screen()
            self.level = 1
            self.lives = INITIAL_LIVES
            while self.level <= LEVEL_MAX:
                level_complete = self.run_level()
                if not level_complete:
                    self.show_game_over()
                    break  # return to main menu
                self.level += 1
                pygame.time.wait(1000)

    def show_start_screen(self):

        logo_surf = pygame.image.load(os.path.join(self.path, "animal_components/logo_match.png"))
        logo_surf = pygame.transform.scale(logo_surf, (WINDOW_WIDTH // 3, WINDOW_HEIGHT // 2 - 50))
        logo_rect = logo_surf.get_rect(centerx=WINDOW_WIDTH // 2)

        bg = pygame.image.load(os.path.join(self.path, "animal_background/main_bg.jpg"))
        bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

        pygame.mixer.music.load(os.path.join(self.path, "animal_music/bg_music_main.mp3"))
        pygame.mixer.music.set_volume(self.music_volume)  # use your existing volume setting
        pygame.mixer.music.play(-1, 0.0)

        # 1) define your labels and fonts
        labels = [
            ("NEW GAME", self.font_big),
            ("OPTIONS",  self.font_big),
            ("EXIT",     self.font_big)
        ]

        # 2) compute max text width + padding
        PADDING_X = 10
        PADDING_Y = 5

        text_sizes = [font.size(txt) for txt, font in labels]
        max_text_width = max(w for w, h in text_sizes)
        max_text_height = max(h for w, h in text_sizes)

        btn_width  = max_text_width + 2 * PADDING_X
        btn_height = max_text_height + 2 * PADDING_Y

        # load & scale your button image once
        btn_img = pygame.image.load(os.path.join(self.path, "animal_components/button.png"))
        btn_img = pygame.transform.scale(btn_img, (btn_width, btn_height))

        # 3) build button rects centered vertically
        total_height = len(labels) * btn_height + (len(labels) - 1) * PADDING_Y
        start_y = (WINDOW_HEIGHT - total_height) // 2
        vertical_offset = 100  # ← how many pixels to move down
        start_y += vertical_offset

        buttons = []
        for i, (txt, font) in enumerate(labels):
            surf = font.render(txt, True, WHITE)
            rect = pygame.Rect(0, 0, btn_width, btn_height)
            rect.centerx = WINDOW_WIDTH // 2
            rect.top = start_y + i * (btn_height + PADDING_Y)
            buttons.append((surf, rect))

        # 4) event loop
        while True:
            self.screen.blit(bg, (0, 0))
            # draw logo above buttons
            # place it so its bottom is just above the first button
            first_btn_top = buttons[0][1].top
            logo_rect.bottom = first_btn_top - 20  # 20px gap
            self.screen.blit(logo_surf, logo_rect)

            for surf, rect in buttons:
                # draw button background image
                self.screen.blit(btn_img, rect.topleft)
                # draw text (centered in rect)
                text_rect = surf.get_rect(center=rect.center)
                self.screen.blit(surf, text_rect)

            pygame.display.update()
            self.clock.tick(FPS)

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == MOUSEBUTTONUP:
                    mx, my = e.pos
                    asset_manager.sounds['click'].play()
                    # check which button was clicked
                    if   buttons[0][1].collidepoint(mx, my): return        # NEW GAME
                    elif buttons[1][1].collidepoint(mx, my): self.show_options_menu()
                    elif buttons[2][1].collidepoint(mx, my): pygame.quit(); sys.exit()


    def show_options_menu(self):
        """Simple mixer for music & SFX + a Return button"""
        return_txt = self.font_small.render('Return', True, WHITE)
        return_rect = return_txt.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 80))

        # slider lines
        music_line = pygame.Rect(150, 200, 550, 4)
        sfx_line   = pygame.Rect(150, 300, 550, 4)
        knob_w, knob_h = 16, 26
        adjusting = None

        # re-use the same button.png as your “Return” background
        return_img = pygame.image.load(os.path.join(self.path, "animal_components/button.png"))
        return_img = pygame.transform.scale(return_img, (return_rect.width, return_rect.height))

        while True:
            self.screen.fill(NAVY_BLUE)
            # labels
            self.screen.blit(self.font_small.render('Music Volume', True, WHITE), (music_line.x, music_line.y - 80))
            self.screen.blit(self.font_small.render('SFX Volume',   True, WHITE), (sfx_line.x,   sfx_line.y + 10))
            # draw lines
            pygame.draw.rect(self.screen, WHITE, music_line)
            pygame.draw.rect(self.screen, WHITE, sfx_line)
            # draw knobs
            mv_x = music_line.x + int(self.music_volume * music_line.w) - knob_w//2
            sv_x = sfx_line.x   + int(self.sfx_volume   * sfx_line.w)   - knob_w//2
            music_knob = pygame.Rect(mv_x, music_line.y - knob_h//2, knob_w, knob_h)
            sfx_knob   = pygame.Rect(sv_x, sfx_line.y   - knob_h//2, knob_w, knob_h)
            pygame.draw.rect(self.screen, GREEN, music_knob)
            pygame.draw.rect(self.screen, GREEN, sfx_knob)

            # draw “Return” button with image background
            self.screen.blit(return_img, return_rect.topleft)
            self.screen.blit(return_txt, return_rect)

            pygame.display.update()
            self.clock.tick(FPS)

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == MOUSEBUTTONDOWN:
                    asset_manager.sounds['click'].play()
                    if music_knob.collidepoint(e.pos):
                        adjusting = 'music'
                    elif sfx_knob.collidepoint(e.pos):
                        adjusting = 'sfx'
                    elif return_rect.collidepoint(e.pos):
                        return
                elif e.type == MOUSEBUTTONUP:
                    adjusting = None
                elif e.type == MOUSEMOTION and adjusting:
                    mx, _ = e.pos
                    if adjusting == 'music':
                        rel = (mx - music_line.x) / music_line.w
                        self.music_volume = max(0.0, min(1.0, rel))
                        pygame.mixer.music.set_volume(self.music_volume)
                    else:
                        rel = (mx - sfx_line.x) / sfx_line.w
                        self.sfx_volume = max(0.0, min(1.0, rel))
                        for snd in asset_manager.sounds.values():
                            snd.set_volume(self.sfx_volume)

    def run_level(self):
        board = Board()
        clicked = []
        first = None

        #Time estimation + bonus
        start_time = time.time()
        time_bonus = 0

        last_hint_time = start_time
        bar_pos = ((WINDOW_WIDTH - TIME_BAR_LENGTH)//2, 10)
        bar_size = (TIME_BAR_LENGTH, TIME_BAR_WIDTH)
        bg = random.choice(asset_manager.backgrounds)
        music = random.choice(asset_manager.music)

        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

        while True:
            now = time.time()
            elapsed = now - start_time
            # End the level when time runs out
            if elapsed >= GAME_TIME + time_bonus:
                pygame.mixer.music.stop()
                return False

            self.screen.blit(bg, (0,0))
            self.draw_board(board)
            self.draw_clicked(board, clicked)
            self.draw_time_bar(elapsed, bar_pos, bar_size)
            self.draw_lives()

            if now - last_hint_time > HINT_INTERVAL:
                hint = board.get_hint()
                last_hint_time = now
                if hint:
                    self.draw_hint(hint)

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit(); sys.exit()
                if e.type == MOUSEBUTTONUP:
                    x, y = e.pos
                    bx = (x - (WINDOW_WIDTH - BOX_SIZE * BOARD_WIDTH)//2)//BOX_SIZE
                    by = (y - (WINDOW_HEIGHT - BOX_SIZE * BOARD_HEIGHT)//2)//BOX_SIZE
                    if 0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT and board.grid[by][bx] != 0:
                        clicked.append((by, bx))
                        if not first:
                            first = (by, bx)
                            asset_manager.sounds['click'].play()
                        else:
                            path = board._bfs(first[0], first[1], by, bx)
                            if path:
                                if random.random() < 0.2:
                                    random.choice(asset_manager.effect_sounds).play()
                                asset_manager.sounds['correct_sound'].play()
                                board.grid[first[0]][first[1]] = 0
                                board.grid[by][bx] = 0
                                self.draw_path(path)
                                time_bonus += 1
                                board.alter(first[0], first[1], by, bx, self.level)
                                if board.is_complete():
                                    return True
                            else:
                                asset_manager.sounds['wrong_sound'].play()
                            clicked = []
                            first = None

            pygame.display.update()
            self.clock.tick(FPS)
        pygame.mixer.music.stop()

    def draw_board(self, board):
        xm = (WINDOW_WIDTH-BOX_SIZE*BOARD_WIDTH)//2
        ym = (WINDOW_HEIGHT-BOX_SIZE*BOARD_HEIGHT)//2
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                val = board.grid[y][x]
                if val:
                    rect = pygame.Rect(x*BOX_SIZE+xm, y*BOX_SIZE+ym, BOX_SIZE, BOX_SIZE)
                    self.screen.blit(asset_manager.animals[val], rect)

    def draw_clicked(self, board, clicked):
        xm = (WINDOW_WIDTH-BOX_SIZE*BOARD_WIDTH)//2
        ym = (WINDOW_HEIGHT-BOX_SIZE*BOARD_HEIGHT)//2
        for by,bx in clicked:
            rect = pygame.Rect(bx*BOX_SIZE+xm, by*BOX_SIZE+ym, BOX_SIZE, BOX_SIZE)
            img = asset_manager.animals[board.grid[by][bx]].copy()
            img.fill((60,60,60), special_flags=pygame.BLEND_RGB_SUB)
            self.screen.blit(img, rect)

    def draw_time_bar(self, elapsed, pos, size):
        pct = max(0,1-elapsed/GAME_TIME)
        pygame.draw.rect(self.screen, WHITE, (*pos, *size), 1)
        inner = (pos[0]+2, pos[1]+2, (size[0]-4)*pct, size[1]-4)
        pygame.draw.rect(self.screen, BOLD_GREEN, inner)

    def draw_lives(self):
        self.screen.blit(asset_manager.heart, (10,10))
        txt = self.font_small.render(str(self.lives), True, WHITE)
        self.screen.blit(txt, (65,10))

    def draw_path(self, path):
        xm = (WINDOW_WIDTH-BOX_SIZE*BOARD_WIDTH)//2
        ym = (WINDOW_HEIGHT-BOX_SIZE*BOARD_HEIGHT)//2
        for i in range(len(path)-1):
            y1,x1 = path[i]; y2,x2 = path[i+1]
            p1 = (x1*BOX_SIZE+xm+BOX_SIZE//2, y1*BOX_SIZE+ym+BOX_SIZE//2)
            p2 = (x2*BOX_SIZE+xm+BOX_SIZE//2, y2*BOX_SIZE+ym+BOX_SIZE//2)
            pygame.draw.line(self.screen, RED, p1, p2, 4)
        pygame.display.update(); pygame.time.wait(300)

    def draw_hint(self, hint):
        xm = (WINDOW_WIDTH-BOX_SIZE*BOARD_WIDTH)//2
        ym = (WINDOW_HEIGHT-BOX_SIZE*BOARD_HEIGHT)//2
        for y,x in hint:
            rect = pygame.Rect(x*BOX_SIZE+xm, y*BOX_SIZE+ym, BOX_SIZE, BOX_SIZE)
            pygame.draw.rect(self.screen, GREEN, rect, 2)

    def show_game_over(self):
        playAgainSurf = self.font_big.render('Return', True, PURPLE)
        playAgainRect = playAgainSurf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        while True:
            self.screen.fill(NAVY_BLUE)
            self.screen.blit(playAgainSurf, playAgainRect)
            pygame.draw.rect(self.screen, PURPLE, playAgainRect, 4)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    if playAgainRect.collidepoint(event.pos):
                        return  # Return to main menu

if __name__ == '__main__':
    PATH = 'C:\\Users\\Cresht\\Downloads\\matching-animals\\matching-animals-main'
    game = Game(PATH)
    game.run()
