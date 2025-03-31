import unittest
import asyncio
import random
from unittest.mock import patch

from obstacle import Obstacle
from test_models import Tile  # Assuming your Tile class is defined in tile.py


# --- Dummy Classes to Simulate Game Environment ---

class DummyBoard:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.shuffle_calls = 0  # Count how many times shuffle is called
        # Create a grid of Tile objects (using "Dummy" as a placeholder asset)
        self.tiles = [[Tile(c, r, "Dummy") for c in range(cols)] for r in range(rows)]

    def shuffle(self, mode="Normal"):
        self.shuffle_calls += 1


class DummyMatches:
    def __init__(self, limit_exceeded=True):
        self.limit_exceeded = limit_exceeded

    def check_mismatch_limit(self):
        return self.limit_exceeded


class DummyGameManager:
    def __init__(self, difficulty: str):
        self.difficulty = difficulty  # "Normal", "Advanced", or "Lunatic"
        self.running = True
        self.time_left = 100
        self.board = DummyBoard(4, 4)
        self.matches = DummyMatches()


# --- Fake Sleep Replacement for Unit Testing ---
# We replace asyncio.sleep with a no-op coroutine to avoid actual delays.
async def fake_sleep(_seconds):
    pass


# --- Unit Tests for Obstacle Class ---

class TestObstacle(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.obstacle = Obstacle()

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_apply_tornado(self):
        # In Advanced mode, tornado should trigger a board shuffle.
        gm = DummyGameManager("Advanced")
        await self.obstacle.apply_tornado(gm)
        # Our apply_tornado executes one shuffle.
        self.assertEqual(gm.board.shuffle_calls, 1)

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_apply_tile_locking(self):
        # Verify that after tile locking, no tile remains locked.
        gm = DummyGameManager("Normal")
        all_tiles = [tile for row in gm.board.tiles for tile in row]
        for tile in all_tiles:
            tile.locked = False
        await self.obstacle.apply_tile_locking(gm)
        # When the effect is applied, tiles are locked then unlocked.
        self.assertTrue(all(not tile.locked for tile in all_tiles))

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_apply_time_bomb(self):
        # Before the effect, no tile should have bomb active and all are visible.
        gm = DummyGameManager("Advanced")
        for row in gm.board.tiles:
            for tile in row:
                self.assertFalse(tile.bomb)
                self.assertTrue(tile.visible)
        await self.obstacle.apply_time_bomb(gm)
        # After the effect, bomb flags should be cleared and all tiles visible.
        for row in gm.board.tiles:
            for tile in row:
                self.assertFalse(tile.bomb)
                self.assertTrue(tile.visible)

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_apply_golden_fish(self):
        # Golden fish should add 30 seconds and then clear the gold flag.
        gm = DummyGameManager("Normal")
        prev_time = gm.time_left
        await self.obstacle.apply_golden_fish(gm)
        for row in gm.board.tiles:
            for tile in row:
                self.assertFalse(tile.gold)
        self.assertEqual(gm.time_left, prev_time + 30)

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_apply_acid_rain(self):
        # After acid rain, no tile should remain marked with acid.
        gm = DummyGameManager("Lunatic")
        all_tiles = [tile for row in gm.board.tiles for tile in row]
        await self.obstacle.apply_acid_rain(gm)
        for tile in all_tiles:
            self.assertFalse(tile.acid)

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_apply_shuffle(self):
        # When mismatch limit is exceeded, board.shuffle should be invoked.
        gm = DummyGameManager("Lunatic")
        initial_shuffle = gm.board.shuffle_calls
        await self.obstacle.apply_shuffle(gm)
        self.assertGreater(gm.board.shuffle_calls, initial_shuffle)

    @patch("asyncio.sleep", new=fake_sleep)
    async def test_run_scheduler(self):
        # Test that the run_scheduler can run for a short period without error.
        gm = DummyGameManager("Advanced")

        async def stop_game():
            await asyncio.sleep(0.1)
            gm.running = False

        # Run the obstacle scheduler and stop_game concurrently.
        scheduler_task = asyncio.create_task(self.obstacle.run_scheduler(gm))
        stopper_task = asyncio.create_task(stop_game())
        await asyncio.gather(scheduler_task, stopper_task)
        self.assertFalse(gm.running)


if __name__ == "__main__":
    unittest.main()
