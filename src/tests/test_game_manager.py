import unittest
import asyncio
from game_manager import Game  # Adjust import based on your project structure
from tile import AnimalType  # Import AnimalType to set dummy data


class TestGameManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Populate AnimalType lists with dummy values to avoid empty sequence errors.
        AnimalType.Normanced = ["DummyAnimal"]
        AnimalType.Lunatic = ["DummyAnimal"]

        # Create an instance of Game with a given difficulty.
        self.game = Game("Normal")

        # Override board.display_board to do nothing (so output is suppressed in test)
        self.game.board.display_board = lambda: None

        # Override time_duration to end quickly.
        async def fake_time_duration():
            self.game.time_left = 0
            await asyncio.sleep(0.001)
            await self.game.game_over()

        self.game.time_duration = fake_time_duration

        # Override player interaction to immediately end the game.
        async def fake_player_interaction():
            self.game.game_state = False

        self.game.async_player_interaction = fake_player_interaction

        # Override the obstacle scheduler so that it does nothing.
        async def fake_run_scheduler(gm):
            return

        self.game.obstacle.run_scheduler = fake_run_scheduler

    async def test_main_game_loop(self):
        # Run the main game loop; with our overrides the game should terminate quickly.
        await self.game.main_game_loop()
        # Assert that the game state is ended and game over flag is set.
        self.assertFalse(self.game.game_state)
        self.assertTrue(self.game.flag)
        self.assertEqual(self.game.time_left, 0)


if __name__ == "__main__":
    unittest.main()
