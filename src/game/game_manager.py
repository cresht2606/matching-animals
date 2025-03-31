import asyncio
from board import Board
from matches import Matches
from obstacle import Obstacle
from tile import Tile
from score_manager import Score


class Game:
    def __init__(self, difficulty):
        # Game state and configuration
        self.difficulty = difficulty
        self.game_state = True  # True means the game is currently running
        self.flag = False  # General flag (e.g., can be used for game over status)

        # Create the board, matches, score manager, and obstacles
        self.board_creation()
        self.matches = Matches(self.board)
        self.score_manager = Score()
        self.obstacle = Obstacle()

        # Set initial time based on difficulty
        self.time_left = self.time_object()

    def board_creation(self):
        board_diff = {"Normal": (16, 9), "Advanced": (16, 9), "Lunatic": (16, 12)}
        rows, cols = board_diff.get(self.difficulty)
        self.board = Board(rows, cols, self.difficulty)

    def score_object(self):
        return self.score_manager.return_score()

    def time_object(self):
        time_diff = {"Normal": 240, "Advanced": 300, "Lunatic": 360}
        return time_diff.get(self.difficulty, 240)

    async def time_duration(self):
        """Asynchronous game timer that counts down once per second."""
        while self.game_state and self.time_left > 0:
            print(f"Game Running | ⏳ Estimated Time Left: {self.time_left} seconds")
            await asyncio.sleep(1)
            self.time_left -= 1
        print("✔️ Time's up!")
        await self.game_over()

    async def game_over(self):
        """Handles game over state."""
        print("Game Over!")
        self.flag = True
        self.game_state = False

    async def async_player_interaction(self):
        """
        Asynchronous version of player interaction.
        It uses asyncio.to_thread to run the blocking input calls off the event loop.
        In a full GUI integration, these inputs would be replaced with event handlers.
        """
        while self.game_state and self.time_left > 0:
            try:
                # Run blocking input in a thread so that the event loop is not blocked.
                x1 = await asyncio.to_thread(input, "Enter the x-coordinate for tile 1: ")
                y1 = await asyncio.to_thread(input, "Enter the y-coordinate for tile 1: ")
                x2 = await asyncio.to_thread(input, "Enter the x-coordinate for tile 2: ")
                y2 = await asyncio.to_thread(input, "Enter the y-coordinate for tile 2: ")
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                tile1, tile2 = self.board.tiles[y1][x1], self.board.tiles[y2][x2]

                # Validate tile visibility and selection.
                if not tile1.visible or not tile2.visible:
                    print("Invalid tile selection, one of these has already been matched!")
                    continue
                if (x1, y1) == (x2, y2):
                    print("You must select two different tiles!")
                    continue

                # Validate matching path.
                if self.matches.is_valid_path(tile1, tile2):
                    print("✅ Match found!")
                    self.board.remove_tiles(tile1, tile2)
                    self.score_manager.update_combo(matched=True)
                    self.score_manager.add_score()
                    self.score_manager.apply_time_bonus()
                    self.time_left += self.score_manager.time_added
                    # Trigger obstacle effects concurrently.
                    await self.apply_effects()
                else:
                    print("❌ Invalid match!")
                    self.score_manager.update_combo(matched=False)
                    self.board.mismatches += 1
                    await self.apply_shuffle()
            except (IndexError, ValueError):
                print("Invalid coordinates input. Please try again!")

    async def apply_effects(self):
        """
        Asynchronously triggers all active obstacle effects.
        The effects are executed as independent tasks, and the active effects list is then cleared.
        """
        tasks = []
        for effect in list(self.obstacle.activate_effects):
            tasks.append(asyncio.create_task(self.obstacle.apply_effects(self, effect)))
        if tasks:
            await asyncio.gather(*tasks)
        self.obstacle.remove_effects()

    async def apply_shuffle(self):
        """
        Applies a shuffle to the board based on various conditions:
         - If no valid matches exist.
         - If mismatch limits are reached.
         - As an external factor (e.g., tornado effect).
        """
        if not self.matches.possible_matches():
            self.board.shuffle(mode="Normal")
            return
        if self.matches.check_mismatch_limit():
            if self.difficulty in ("Normal", "Advanced"):
                self.board.shuffle(mode="Normal")
            elif self.difficulty == "Lunatic":
                self.board.shuffle(mode="Lunatic")
            return
        if "tornado" in self.obstacle.activate_effects:
            await self.obstacle.apply_tornado(self)

    async def main_game_loop(self):
        """
        The main game loop is managed asynchronously.
        It concurrently runs the timer, player interaction, and the obstacle scheduler.
        """
        self.board.display_board()
        timer_task = asyncio.create_task(self.time_duration())
        player_task = asyncio.create_task(self.async_player_interaction())
        # Start the obstacle scheduler concurrently.
        obstacle_task = asyncio.create_task(self.obstacle.run_scheduler(self))
        await asyncio.gather(timer_task, player_task, obstacle_task)

    def start_game(self):
        """Entry point to start the game; runs the main game loop in asyncio."""
        asyncio.run(self.main_game_loop())

    def pause(self):
        self.game_state = False

    def restart(self):
        self.__init__(self.difficulty)
        self.start_game()
