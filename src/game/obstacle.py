import random
import asyncio
from typing import Any, Dict

class Obstacle:
    # Frequency dictionary: maps each effect to its base delay (in seconds) per difficulty.
    EFFECT_FREQUENCY: Dict[str, Dict[str, float]] = {
        "tornado": {"Normal": 15, "Advanced": 10, "Lunatic": 5},
        "tile_locking": {"Normal": 30, "Advanced": 25, "Lunatic": 20},
        "time_bomb": {"Normal": 20, "Advanced": 18, "Lunatic": 15},
        "golden_fish": {"Normal": 32, "Advanced": 28, "Lunatic": 28},
        "acid_rain": {"Normal": 10, "Advanced": 8, "Lunatic": 6},
        "shuffle": {"Normal": 15, "Advanced": 12, "Lunatic": 8},
    }

    def __init__(self) -> None:
        # Holds the list of active effect names.
        self.activate_effects: list[str] = []

    async def apply_effects(self, game_manager: Any, effect_name: str) -> None:
        """
        Activates the effect specified by effect_name.
        """
        self.activate_effects.append(effect_name)

        effect_keywords = {
            "tornado": self.apply_tornado,
            "tile_locking": self.apply_tile_locking,
            "time_bomb": self.apply_time_bomb,
            "golden_fish": self.apply_golden_fish,
            "acid_rain": self.apply_acid_rain,
            "shuffle": self.apply_shuffle
        }

        if effect_name in effect_keywords:
            await effect_keywords[effect_name](game_manager)
        else:
            print(f"Effect '{effect_name}' is not recognized.")

    def remove_effects(self) -> None:
        """Clear all active effects."""
        self.activate_effects.clear()

    def require_effects(self) -> bool:
        """Return True if there are any active effects."""
        return bool(self.activate_effects)

    async def apply_tornado(self, game_manager: Any) -> None:
        """
        Applies the tornado effect by shuffling the board a number of times
        based on the game difficulty.
        """
        print("🌪️ Incoming the fierce tornado")
        # Even if frequency is used for scheduling, we can optionally trigger multiple shuffles.
        # For simplicity, perform one quick shake.
        print("🔀 Tornado rages, shaking the board!")
        game_manager.board.shuffle(mode="Normal")
        await asyncio.sleep(0.1)

    async def apply_tile_locking(self, game_manager: Any) -> None:
        """
        Locks a random subset of tiles temporarily then unlocks them
        after a delay determined by the game difficulty.
        """
        print("🔒 Locking tiles! Hold tight!")
        pairs = {
            "Normal": random.randint(3, 4),
            "Advanced": random.randint(2, 3),
            "Lunatic": random.randint(2, 3),
        }
        unlock_times = {"Normal": 30, "Advanced": 25, "Lunatic": 20}
        num_to_lock = pairs.get(game_manager.difficulty, 3)
        all_tiles = [tile for row in game_manager.board.tiles for tile in row]
        if len(all_tiles) < num_to_lock:
            print("Not enough tiles available for locking.")
            return

        locked_tiles = random.sample(all_tiles, num_to_lock)
        for tile in locked_tiles:
            tile.locked = True

        await asyncio.sleep(unlock_times.get(game_manager.difficulty, 30))

        for tile in locked_tiles:
            tile.locked = False

    async def apply_time_bomb(self, game_manager: Any) -> None:
        """
        Activates time bombs on random tiles. Neighboring tiles will be
        temporarily hidden.
        """
        print("💣 Time bomb activated!")
        freq_bombs = {
            "Normal": random.randint(1, 2),
            "Advanced": random.randint(2, 3),
            "Lunatic": random.randint(3, 5),
        }
        num_bombs = freq_bombs.get(game_manager.difficulty, 1)
        current_tiles = [tile for row in game_manager.board.tiles for tile in row]

        for _ in range(num_bombs):
            bomb_tile = random.choice(current_tiles)
            bomb_tile.bomb = True
            bomb_tile.visible = False

            affected_tiles = []
            # Calculate affected neighboring tiles (assuming board.tiles is indexed as [row][col]).
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x = bomb_tile.x + dx
                new_y = bomb_tile.y + dy
                if 0 <= new_x < game_manager.board.cols and 0 <= new_y < game_manager.board.rows:
                    affected_tiles.append(game_manager.board.tiles[new_y][new_x])
            for tile in affected_tiles:
                tile.visible = False

            await asyncio.sleep(random.randint(15, 20))

            bomb_tile.bomb = False
            bomb_tile.visible = True
            for tile in affected_tiles:
                tile.visible = True

    async def apply_golden_fish(self, game_manager: Any) -> None:
        """
        Highlights a random visible tile as the golden fish, granting a time bonus.
        """
        print("🐟 Golden fish detected! Go and hunt for goods!")
        disappear_time = {"Normal": 32, "Advanced": 28, "Lunatic": 28}
        visible_tiles = [tile for row in game_manager.board.tiles for tile in row if tile.visible]
        if not visible_tiles:
            return
        golden_tile = random.choice(visible_tiles)
        golden_tile.gold = True
        game_manager.time_left += 30
        await asyncio.sleep(disappear_time.get(game_manager.difficulty, 32))
        golden_tile.gold = False

    async def apply_acid_rain(self, game_manager: Any) -> None:
        """
        Applies an acid rain effect to a random subset of tiles for a short duration.
        """
        print("🌧️ Incoming acid rains! Watch out!")
        tile_percentages = {"Normal": random.uniform(0.1, 0.15), "Advanced": 0.20, "Lunatic": 0.30}
        percentage = tile_percentages.get(game_manager.difficulty, 0.1)
        all_tiles = [tile for row in game_manager.board.tiles for tile in row]
        num_tiles = int(percentage * len(all_tiles))
        if num_tiles <= 0:
            return

        affected_tiles = random.sample(all_tiles, num_tiles)
        for tile in affected_tiles:
            tile.acid = True
        await asyncio.sleep(random.randint(10, 15))
        for tile in affected_tiles:
            tile.acid = False

    async def apply_shuffle(self, game_manager: Any) -> None:
        """
        Shuffles the board when mismatches exceed a given limit.
        """
        print("Exceeded mismatch moves! Shuffling...")
        if game_manager.matches.check_mismatch_limit():
            shuffle_mode = "Lunatic" if game_manager.difficulty == "Lunatic" else "Normal"
            game_manager.board.shuffle(mode=shuffle_mode)

    async def run_scheduler(self, game_manager: Any) -> None:
        """
        Scheduler method for obstacles that periodically triggers obstacle effects.
        Each effect's delay is defined by the EFFECT_FREQUENCY table.
        """
        # Retrieve a list of available effects.
        effects = list(self.EFFECT_FREQUENCY.keys())
        while game_manager.running:
            # Randomly choose an effect.
            effect = random.choice(effects)
            # Obtain its base delay for the current difficulty.
            delay = self.EFFECT_FREQUENCY.get(effect, {}).get(game_manager.difficulty, 15)
            # Optionally randomize the delay within ±10%.
            delay = random.uniform(delay * 0.9, delay * 1.1)
            print(f"Scheduling effect '{effect}' to occur in {delay:.2f} seconds.")
            await asyncio.sleep(delay)
            if not game_manager.running:
                break
            print(f"Triggering obstacle effect: {effect}")
            await self.apply_effects(game_manager, effect)
