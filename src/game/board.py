import random
from collections import defaultdict
from tile import Tile, AnimalType

class Board:
    def __init__(self, cols: int, rows: int, diff: str):
        self.cols = cols
        self.rows = rows
        self.diff = diff  # Game difficulty (e.g., "Normal", "Advanced", "Lunatic")
        self.mismatches = 0
        # Generate the board: a 2D list of Tile objects.
        self.tiles = self.generate_tiles()
        # Flag to indicate whether it's the player's turn (used in Matches).
        self.is_player_turn = True

    def generate_tiles(self):
        total_tiles = self.cols * self.rows

        # Ensure board has an even number of tiles.
        if total_tiles % 2 != 0:
            raise ValueError("Insufficient number of tiles: must be even.")

        # Retrieve animal assets based on difficulty.
        animal_selection = AnimalType.get_animals(self.diff)
        if not animal_selection:
            raise ValueError("Animal selection is empty – please populate the asset list.")

        # Generate a 1D list of tiles (each animal appears in a pair).
        tile_list = []
        for _ in range(total_tiles // 2):
            animal_tile = random.choice(animal_selection)
            tile_list.append(Tile(0, 0, animal_tile))
            tile_list.append(Tile(0, 0, animal_tile))

        # Shuffle the flat list.
        random.shuffle(tile_list)

        # Assign proper x (column) and y (row) coordinates.
        for index, tile in enumerate(tile_list):
            tile.x = index % self.cols
            tile.y = index // self.cols

        # Convert the flat list into a 2D grid using slicing.
        board_tiles = [tile_list[i * self.cols:(i + 1) * self.cols] for i in range(self.rows)]
        return board_tiles

    def remove_tiles(self, tile1: Tile, tile2: Tile):
        """
        Remove the two tiles if they match; otherwise increment mismatches counter.
        Note: check_valid_matches() should be either defined here or in Matches.
        """
        if self.check_valid_matches(tile1, tile2):
            tile1.visible = False
            tile2.visible = False
        else:
            self.mismatches += 1

    def check_valid_matches(self, tile1: Tile, tile2: Tile) -> bool:
        """
        Returns True if both tiles are visible and have the same animal asset.
        (You may move mismatch counting to a higher level if desired.)
        """
        return tile1.visible and tile2.visible and (tile1.animal_tile == tile2.animal_tile)

    def display_board(self):
        """
        Basic console output for debugging.
        In GUI integration, this method might be replaced by actual rendering logic.
        """
        board_lines = []
        for row in self.tiles:
            line = " ".join(f"[{tile.animal_tile}]" if tile.visible else "[X]" for tile in row)
            board_lines.append(line)
        print("\n".join(board_lines))
        print()  # Additional newline for clarity.

    def shuffle(self, mode: str = "Normal"):
        """
        Shuffles the board tiles.
         - In Lunatic mode: shuffles all tiles arbitrarily.
         - In Normal/Advanced mode: shuffles only visible tiles in pairs.
        After shuffling, updates the board grid and tile coordinates.
        """
        if mode == "Lunatic":
            # Flatten all tiles.
            flat_tiles = [tile for row in self.tiles for tile in row]
            random.shuffle(flat_tiles)
            for idx, tile in enumerate(flat_tiles):
                tile.x = idx % self.cols
                tile.y = idx // self.cols
            self.tiles = [flat_tiles[i * self.cols:(i + 1) * self.cols] for i in range(self.rows)]
        else:
            # For Normal / Advanced mode: consider only visible tiles.
            visible_tiles = [tile for row in self.tiles for tile in row if tile.visible]
            if len(visible_tiles) % 2 != 0:
                raise ValueError("Invalid state: the number of visible tiles is not even; cannot form pairs.")

            # Group tiles by animal.
            groups = defaultdict(list)
            for tile in visible_tiles:
                groups[tile.animal_tile].append(tile)

            grouped_pairs = []
            for animal, tiles in groups.items():
                # Ensure a pair can be formed from the group.
                for i in range(0, len(tiles) - 1, 2):
                    grouped_pairs.append((tiles[i], tiles[i+1]))
            random.shuffle(grouped_pairs)

            # Flatten paired tiles back into a list.
            shuffled_visible = [tile for pair in grouped_pairs for tile in pair]

            # Create a new board by replacing only visible tiles.
            new_tiles = []
            visible_iter = iter(shuffled_visible)
            for row in self.tiles:
                new_row = []
                for tile in row:
                    if tile.visible:
                        new_row.append(next(visible_iter))
                    else:
                        new_row.append(tile)
                new_tiles.append(new_row)
            self.tiles = new_tiles

        # For debugging—when integrated with GUI, you might remove or redirect this output.
        self.display_board()
