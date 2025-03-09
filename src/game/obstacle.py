import random
import time

class Obstacle:
    def __init__(self, position, effect, duration):
        self.position = position
        self.effect = effect
        self.duration = duration

    def apply_effect(self, game_manager, mode):
        if self.effect == "tornado":
            self.apply_tornado(game_manager, mode)
        elif self.effect == "tile_locking":
            self.apply_tile_locking(game_manager, mode)
        elif self.effect == "time_bomb":
            self.apply_time_bomb(game_manager, mode)
        elif self.effect == "golden_fish":
            self.apply_golden_fish(game_manager)
        elif self.effect == "acid_rain":
            self.apply_acid_rain(game_manager, mode)
        elif self.effect == "shuffle":
            self.apply_shuffle(game_manager, mode)

    def apply_tornado(self, game_manager, mode):
        times = {"Normal": 0, "Advanced": 1, "Lunatic": 2}
        for _ in range(times[mode]):
            positions = [tile.position for tile in game_manager.board.tiles]
            random.shuffle(positions)
            for i, tile in enumerate(game_manager.board.tiles):
                tile.position = positions[i]
            time.sleep(random.randint(5, 10))

    def apply_tile_locking(self, game_manager, mode):
        pairs = {"Normal": 3, "Advanced": 2, "Lunatic": 2}
        unlock_times = {"Normal": 30, "Advanced": 25, "Lunatic": 20}
        locked_tiles = random.sample(game_manager.board.tiles, pairs[mode])
        for tile in locked_tiles:
            tile.locked = True
        time.sleep(unlock_times[mode])
        for tile in locked_tiles:
            tile.locked = False

    def apply_time_bomb(self, game_manager, mode):
        bombs = {"Normal": 1, "Advanced": 2, "Lunatic": 3}
        for _ in range(bombs[mode]):
            bomb_tile = random.choice(game_manager.board.tiles)
            bomb_tile.bomb = True
            time.sleep(random.randint(15, 20))
            bomb_tile.explode()
            bomb_tile.bomb = False

    def apply_golden_fish(self, game_manager):
        golden_fish_tile = random.choice(game_manager.board.tiles)
        golden_fish_tile.gold = True
        time.sleep(28)  # 32s in Normal mode
        golden_fish_tile.gold = False

    def apply_acid_rain(self, game_manager, mode):
        tile_percentage = {"Normal": 0.15, "Advanced": 0.20, "Lunatic": 0.30}
        num_tiles = int(tile_percentage[mode] * len(game_manager.board.tiles))
        affected_tiles = random.sample(game_manager.board.tiles, num_tiles)
        for tile in affected_tiles:
            tile.acid = True
        time.sleep(random.randint(10, 15))
        for tile in affected_tiles:
            tile.acid = False

    def apply_shuffle(self, game_manager, mode):
        mismatches = {"Normal": 3, "Advanced": 2, "Lunatic": 2}
        shuffle_time = random.randint(5, 7)
        if game_manager.mismatches >= mismatches[mode]:
            positions = [tile.position for tile in game_manager.board.tiles]
            random.shuffle(positions)
            for i, tile in enumerate(game_manager.board.tiles):
                tile.position = positions[i]
            time.sleep(shuffle_time)

