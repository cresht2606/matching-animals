import os, sys, time, pygame, random, collections
from pygame.locals import *

# GAME SETTINGS
FPS = 60
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BOXSIZE = 65
BOARD_WIDTH = 16
BOARD_HEIGHT = 11
ANIMAL_NUM = 32
DUPLICATED_ANIMAL = 4
TIMEBAR_LENGTH = 300
TIMEBAR_WIDTH = 30
LEVEL_MAX = 5
GAMETIME = 180
GET_HINT_TIME = 30

#MUSIC / SOUND TOGGLE
MUSIC_ON = True
SOUND_ON = True

XMARGIN = (WINDOW_WIDTH - (BOXSIZE * BOARD_WIDTH)) // 2
YMARGIN = (WINDOW_HEIGHT - (BOXSIZE * BOARD_HEIGHT)) // 2

#COLORS
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BOLDGREEN = (0, 175, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
NAVYBLUE = (60, 60, 100)

class AssetManager:
    def __init__(self, path):
        self.path = path
        self.animal_images = {}
        self.logo = None
        self.sounds = []
        self.music_tracks = [f"bg_music_{i}.mp3" for i in range(1, 6)]
        self.main_menu_background = []
        self.gameplay_backgrounds = []
        self.main_menu_music = None
        self.click_sound = None
        self.correct_sound = None
        self.wrong_sound = None
        self.heart = None
        self.button = None
        self.load_assets()
    def load_assets(self):
        pygame.mixer.pre_init()
        pygame.mixer.init()

        animal_list = os.listdir(os.path.join(self.path, "animal_icons"))
        for i, filename in enumerate(animal_list):
            image = pygame.image.load(os.path.join("animal_icons", filename))
            self.animal_images[i + 1] = pygame.transform.scale(image, size = (BOXSIZE, BOXSIZE))

        self.click_sound = pygame.mixer.Sound("gui_button_click.mp3")
        self.click_sound.set_volume(1.0)

        self.correct_sound = pygame.mixer.Sound("correct_sound.mp3")

        self.wrong_sound = pygame.mixer.Sound("wrong_sound.mp3")
        self.wrong_sound.set_volume(1.0)

        self.main_menu_music = "main_bg.mp3"

        self.heart = pygame.transform.scale(pygame.image.load("heart.png"), (45, 45))

        logo_path = os.path.join(self.path, "logo_match.png")
        self.logo = pygame.transform.scale(pygame.image.load(logo_path), (400, 400))

        self.button = pygame.transform.scale(pygame.image.load(os.path.join("button.png")), (300, 70))

        #Load gameplay backgrounds
        self.gameplay_backgrounds.append(
            pygame.transform.scale(pygame.image.load("background/bg.jpg"), (WINDOW_WIDTH, WINDOW_HEIGHT)))
        for i in range(1, 7):
            bg = pygame.image.load(f"background/{i}.jpg")
            self.gameplay_backgrounds.append(pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT)))

        #Load main menu background
        main_bg = pygame.image.load(os.path.join("background", "bg.jpg"))
        self.main_menu_background = [pygame.transform.scale(main_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))]


class Board:
    def __init__(self, animals):
        self.animals = animals
        self.grid = self.get_randomized_board()

    def get_randomized_board(self):
        num_animals_on_board = ANIMAL_NUM
        num_duplicates = DUPLICATED_ANIMAL

        list_animals = list(range(1, len(self.animals) + 1))
        random.shuffle(list_animals)
        list_animals = list_animals[:num_animals_on_board] * num_duplicates
        random.shuffle(list_animals)

        board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        k = 0
        for i in range(1, BOARD_HEIGHT - 1):
            for j in range(1, BOARD_WIDTH - 1):
                board[i][j] = list_animals[k]
                k += 1

        return board

    def shuffle_tiles(self):
        visible_tiles = [val for row in self.grid for val in row if val != 0]
        original_order = visible_tiles[:]
        while visible_tiles == original_order:  # Ensure it actually changes
            random.shuffle(visible_tiles)

        idx = 0
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.grid[y][x] != 0:
                    self.grid[y][x] = visible_tiles[idx]
                    idx += 1

    def is_complete(self):
        return all(val == 0 for row in self.grid for val in row)

    def get_hint(self):
        positions = collections.defaultdict(list)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                val = self.grid[y][x]
                if val:
                    positions[val].append((y, x))

        for y1 in range(BOARD_HEIGHT):
            for x1 in range(BOARD_WIDTH):
                val = self.grid[y1][x1]
                if val:
                    for y2, x2 in positions[val]:
                        if (y1, x1) != (y2, x2) and MatchingAnimals.bfs(self.grid, y1, x1, y2, x2):
                            return [(y1, x1), (y2, x2)]
        return []

    def reset(self):
        pokes = [val for row in self.grid for val in row if val != 0]
        original = pokes[:]
        while pokes == original:
            random.shuffle(pokes)

        i = 0
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.grid[y][x] != 0:
                    self.grid[y][x] = pokes[i]
                    i += 1


class MatchingAnimals:
    def __init__(self, path):
        pygame.init()
        self.assets = AssetManager(path)
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Matching Animals")

        font_path = os.path.join(path, "fonts", "DungeonFont.ttf")
        self.font = pygame.font.Font(font_path, 50)
        self.lives_font = pygame.font.Font(font_path, 45)

        self.level = 1
        self.lives = 3
        self.time_bonus = 0
        self.start_time = 0
        self.last_hint_time = time.time()
        self.hint_pair = []
        self.first_selection = None
        self.clicked_boxes = []


    def draw_text_center(self, text, font, color):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.display.blit(surf, rect)
        pygame.draw.rect(self.display, color, rect, 4)

    def draw_lives(self):
        heart_rect = self.assets.heart.get_rect(topleft=(20, 20))
        self.display.blit(self.assets.heart, heart_rect)

        lives_surf = self.lives_font.render(str(self.lives), True, WHITE)
        lives_rect = lives_surf.get_rect(midleft=(heart_rect.right + 10, heart_rect.centery))
        self.display.blit(lives_surf, lives_rect)
    def draw_time_bar(self):
        bar_width = TIMEBAR_LENGTH
        bar_height = TIMEBAR_WIDTH
        time_elapsed = time.time() - self.start_time - self.time_bonus
        progress = max(0, 1 - (time_elapsed / GAMETIME))

        # Align with top margin, but leave enough spacing
        outer_rect = pygame.Rect(WINDOW_WIDTH // 2 - bar_width // 2, 20, bar_width, bar_height)
        inner_rect = pygame.Rect(outer_rect.x + 2, outer_rect.y + 2, int((bar_width - 4) * progress), bar_height - 4)

        pygame.draw.rect(self.display, WHITE, outer_rect, 1)
        pygame.draw.rect(self.display, BOLDGREEN, inner_rect)

    #Highlighting path for each valid pairs
    def get_center_pos(self, grid_pos):
        y, x = grid_pos
        center_x = x * BOXSIZE + XMARGIN + BOXSIZE // 2
        center_y = y * BOXSIZE + YMARGIN + BOXSIZE // 2
        return (center_x, center_y)

    def draw_path(self, path):
        for i in range(len(path) - 1):
            start_pos = self.get_center_pos(path[i])
            end_pos = self.get_center_pos(path[i + 1])
            pygame.draw.line(self.display, RED, start_pos, end_pos, 4)
        pygame.display.update()
        pygame.time.wait(300)


    #Board component
    def draw_board(self, board):
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                val = board.grid[y][x]
                if val != 0:
                    left = x * BOXSIZE + XMARGIN
                    top = y * BOXSIZE + YMARGIN
                    rect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
                    img = self.assets.animal_images[val].copy()
                    if (x, y) in self.clicked_boxes:
                        img.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_SUB)
                    self.display.blit(img, rect)

    def get_box_at_pixel(self, x, y):
        if x < XMARGIN or x >= WINDOW_WIDTH - XMARGIN or y < YMARGIN or y >= WINDOW_HEIGHT - YMARGIN:
            return None, None
        return (x - XMARGIN) // BOXSIZE, (y - YMARGIN) // BOXSIZE

    def draw_hint(self, hint):
        for y, x in hint:
            left = x * BOXSIZE + XMARGIN
            top = y * BOXSIZE + YMARGIN
            pygame.draw.rect(self.display, GREEN, (left, top, BOXSIZE, BOXSIZE), 4)

    #In-game states
    def start_screen(self):
        if MUSIC_ON:
            pygame.mixer.music.load(self.assets.main_menu_music)
            pygame.mixer.music.play(-1, 0.0)

        # Define button dimensions
        button_width, button_height = 300, 70
        spacing = 30
        center_x = WINDOW_WIDTH // 2

        # Logo setup (centered above buttons)
        logo_image = self.assets.logo
        logo_rect = logo_image.get_rect()
        logo_rect.center = (center_x, 200)  # Adjust Y as needed for spacing

        # Button rects
        new_game_btn = pygame.Rect(center_x - button_width // 2, 400, button_width, button_height)
        options_btn = pygame.Rect(center_x - button_width // 2, 400 + button_height + spacing, button_width,
                                  button_height)
        exit_btn = pygame.Rect(center_x - button_width // 2, 400 + 2 * (button_height + spacing), button_width,
                               button_height)

        while True:
            self.display.blit(self.assets.main_menu_background[0], (0, 0))
            self.display.blit(logo_image, logo_rect)

            # Draw buttons
            self.display.blit(self.assets.button, new_game_btn)

            new_game_text = self.font.render("New Game", True, WHITE)
            options_text = self.font.render("Options", True, WHITE)
            exit_text = self.font.render("Exit", True, WHITE)

            #Blit button images
            self.display.blit(self.assets.button, new_game_btn)
            self.display.blit(self.assets.button, options_btn)
            self.display.blit(self.assets.button, exit_btn)

            #Center the text on each button
            self.display.blit(new_game_text, new_game_text.get_rect(center=new_game_btn.center))
            self.display.blit(options_text, options_text.get_rect(center=options_btn.center))
            self.display.blit(exit_text, exit_text.get_rect(center=exit_btn.center))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    if SOUND_ON:
                        self.assets.click_sound.play()
                    if new_game_btn.collidepoint(event.pos):
                        return  # Start game
                    elif options_btn.collidepoint(event.pos):
                        self.options_menu()
                    elif exit_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            self.clock.tick(FPS)

    def options_menu(self):

        global MUSIC_ON, SOUND_ON
        music_on = MUSIC_ON
        sound_on = SOUND_ON

        # Button setup
        button_width = 250
        button_height = 60
        spacing = 20
        center_x = WINDOW_WIDTH // 2

        music_btn = pygame.Rect(center_x - button_width // 2, 300, button_width, button_height)
        sound_btn = pygame.Rect(center_x - button_width // 2, 380, button_width, button_height)
        back_btn = pygame.Rect(center_x - button_width // 2, 460, button_width, button_height)

        while True:
            self.display.fill(NAVYBLUE)

            # Title
            title = self.font.render("OPTIONS", True, WHITE)
            self.display.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 180)))

            # Scale button image to match the actual rect size
            scaled_music_btn = pygame.transform.scale(self.assets.button, (music_btn.width, music_btn.height))
            scaled_sound_btn = pygame.transform.scale(self.assets.button, (sound_btn.width, sound_btn.height))
            scaled_back_btn = pygame.transform.scale(self.assets.button, (back_btn.width, back_btn.height))

            # Blit them
            self.display.blit(scaled_music_btn, music_btn)
            self.display.blit(scaled_sound_btn, sound_btn)
            self.display.blit(scaled_back_btn, back_btn)

            # Labels
            music_label = self.lives_font.render(f"Music: {'On' if music_on else 'Off'}", True, WHITE)
            sound_label = self.lives_font.render(f"Sound: {'On' if sound_on else 'Off'}", True, WHITE)
            back_label = self.lives_font.render("Main Menu", True, WHITE)

            self.display.blit(music_label, music_label.get_rect(center=music_btn.center))
            self.display.blit(sound_label, sound_label.get_rect(center=sound_btn.center))
            self.display.blit(back_label, back_label.get_rect(center=back_btn.center))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    if SOUND_ON:
                        self.assets.click_sound.play()
                    if music_btn.collidepoint(event.pos):
                        music_on = not music_on
                        MUSIC_ON = music_on
                        if MUSIC_ON:
                            pygame.mixer.music.play(-1, 0.0)
                        else:
                            pygame.mixer.music.stop()

                    elif sound_btn.collidepoint(event.pos):
                        sound_on = not sound_on
                        SOUND_ON = sound_on
                        volume = 1 if SOUND_ON else 0
                        self.assets.click_sound.set_volume(volume)
                        self.assets.correct_sound.set_volume(volume)
                        self.assets.wrong_sound.set_volume(volume)

                    elif back_btn.collidepoint(event.pos):
                        return  # Go back to start menu

            self.clock.tick(FPS)

    def play_level(self):
        board = Board(self.assets.animal_images)
        self.start_time = time.time()
        self.time_bonus = 0

        #Only play music if music is ON
        if MUSIC_ON:
            pygame.mixer.music.stop()  # Stop previous music first
            track = self.assets.music_tracks[self.level - 1]
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(-1, 0.0)
        else:
            pygame.mixer.music.stop()  # 🔇 Ensure it's silenced if music is off

        while not board.is_complete():
            self.display.blit(self.assets.gameplay_backgrounds[self.level], (0, 0))
            self.draw_board(board)
            self.draw_lives()
            self.draw_time_bar()

            if time.time() - self.last_hint_time >= GET_HINT_TIME:
                self.hint_pair = board.get_hint()
                self.last_hint_time = time.time()

            if self.hint_pair:
                self.draw_hint(self.hint_pair)

            if not board.get_hint():
                board.shuffle_tiles()

            pygame.display.update()

            #If time runs out, pops up game over screen
            if time.time() - self.start_time > GAMETIME + self.time_bonus:
                self.game_over_screen()
                return


            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    x, y = event.pos
                    boxx, boxy = self.get_box_at_pixel(x, y)
                    if boxx is not None and board.grid[boxy][boxx] != 0:
                        self.handle_tile_click(board, boxx, boxy)
                        self.last_hint_time = time.time()
                        self.hint_pair = []  # clear after user action

            self.clock.tick(FPS)

    def handle_tile_click(self, board, x, y):
        if SOUND_ON:
            self.assets.click_sound.play()

        if self.first_selection is None:
            self.first_selection = (x, y)
            self.clicked_boxes = [(x, y)]

        else:
            # 🚫 Prevent matching a tile to itself
            if (x, y) == self.first_selection:
                self.first_selection = None
                self.clicked_boxes = []
                return

            path = self.bfs(board.grid, self.first_selection[1], self.first_selection[0], y, x)
            if path:
                board.grid[self.first_selection[1]][self.first_selection[0]] = 0
                board.grid[y][x] = 0
                self.assets.click_sound.play()
                self.time_bonus += 1
                self.draw_path(path)
            else:
                if SOUND_ON:
                    self.assets.wrong_sound.play()

            self.first_selection = None
            self.clicked_boxes = []

    def ask_continue_prompt(self):
        font = self.lives_font
        prompt_text = font.render("Continue to next level?", True, WHITE)

        # Button positions and sizes
        button_width, button_height = 180, 60
        yes_rect = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 + 50, button_width, button_height)
        no_rect = pygame.Rect(WINDOW_WIDTH // 2 + 40, WINDOW_HEIGHT // 2 + 50, button_width, button_height)

        # Scale button image to fit buttons
        scaled_yes_button = pygame.transform.scale(self.assets.button, (yes_rect.width, yes_rect.height))
        scaled_no_button = pygame.transform.scale(self.assets.button, (no_rect.width, no_rect.height))

        while True:
            self.display.fill(NAVYBLUE)
            self.display.blit(prompt_text, prompt_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

            # Draw button images
            self.display.blit(scaled_yes_button, yes_rect)
            self.display.blit(scaled_no_button, no_rect)

            # Draw centered text on buttons
            yes_text = font.render("YES", True, WHITE)
            no_text = font.render("NO", True, WHITE)

            self.display.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
            self.display.blit(no_text, no_text.get_rect(center=no_rect.center))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    if SOUND_ON:
                        self.assets.click_sound.play()
                    if yes_rect.collidepoint(event.pos):
                        return True
                    elif no_rect.collidepoint(event.pos):
                        return False

            self.clock.tick(FPS)

    def game_over_screen(self):
        game_over = pygame.transform.scale(pygame.image.load("game_over.png"), (1000, 300))
        logo_rect = game_over.get_rect()
        logo_rect.center = (WINDOW_WIDTH // 2, (WINDOW_HEIGHT // 2) - 200)

        while True:
            self.display.fill(NAVYBLUE)
            self.display.blit(game_over, logo_rect)
            self.draw_text_center('Return To Main Menu', self.font, PURPLE)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    if SOUND_ON:
                        self.assets.click_sound.play()
                    self.start_screen()
                    return

    def run(self):
        while True:
            random.shuffle(self.assets.gameplay_backgrounds)
            random.shuffle(self.assets.music_tracks)
            self.level = 1
            self.lives = 3
            self.start_screen()

            while self.level <= LEVEL_MAX:
                self.play_level()

                if self.level == LEVEL_MAX:
                    break  # Final level finished, break early

                # Prompt to continue or quit
                continue_game = self.ask_continue_prompt()
                if not continue_game:
                    return

                self.level += 1

            self.game_over_screen()

    #Breadth First Search algorithm for finding shortest valid path
    @staticmethod
    def bfs(board, y1, x1, y2, x2):
        def backtrace(parent, start, end):
            path = [end]
            while path[-1] != start:
                path.append(parent[path[-1]])
            path.reverse()
            return [p[:2] for p in path]

        if board[y1][x1] != board[y2][x2]:
            return []

        n, m = len(board), len(board[0])
        q = collections.deque()
        start = (y1, x1, 0, 'none')
        q.append(start)
        visited = {start}
        parent = {}

        directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}

        while q:
            y, x, turns, dir_ = q.popleft()
            if (y, x) == (y2, x2) and (y, x, turns, dir_) != start:
                return backtrace(parent, start, (y, x, turns, dir_))

            for d, (dy, dx) in directions.items():
                ny, nx = y + dy, x + dx
                if 0 <= ny < n and 0 <= nx < m and (board[ny][nx] == 0 or (ny, nx) == (y2, x2)):
                    new_turns = turns if dir_ == d or dir_ == 'none' else turns + 1
                    state = (ny, nx, new_turns, d)
                    if new_turns <= 2 and state not in visited:
                        visited.add(state)
                        parent[state] = (y, x, turns, dir_)
                        q.append(state)
        return []

if __name__ == "__main__":
    PATH = "C:\\Users\\Cresht\\Downloads\\matching_animals"
    game = MatchingAnimals(PATH)
    game.run()