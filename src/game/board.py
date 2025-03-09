import random
from tile import Tile, AnimalType
from collections import defaultdict

class Board:
    def __init__(self, cols, rows, diff):
        self.cols = cols
        self.rows = rows
        self.diff = diff
        self.tiles = self.generate_tiles()
        self.mismatches = 0

    #Basic operations
    def generate_tiles(self):
        #Barriers based on existing rows, cols
        total_tiles = self.cols * self.rows

        #The board must ensure the pair (Even matches)
        if total_tiles % 2 != 0:
            raise ValueError("Insufficient amount of tiles")

        #Get various types of animal based on difficulty
        animal_selection = AnimalType.get_animals(self.diff)

        #GameBoard
        tile_board = []

        #Tiles as placeholder before arranging
        for _ in range(total_tiles // 2):
            animal_tile = random.choice(animal_selection)
            tile_board.append(Tile(0, 0,animal_tile))
            tile_board.append(Tile(0, 0, animal_tile))

        #Shuffle once the generation is completed
        random.shuffle(tile_board)
        for position, tile in enumerate(tile_board):
            tile.x = position % self.cols
            tile.y = position // self.cols

        #Convert from 1D to 2D list
        return [[tile_board.pop(0) for c in range(self.cols)] for r in range(self.rows)]

    def remove_tiles(self, tile1, tile2):
        if self.check_valid_matches(tile1, tile2):
            tile1.visible = False
            tile2.visible = False
        else:
            self.mismatches += 1

    def display_board(self):
        for rows in self.tiles:
            for cols in rows:
                print(f"[{cols.animal_tile}]" if cols.visible else "[X]", end = " ")
            print()


    #Shuffle mechanism
    def shuffle(self, mode = "Normal"):
        shuffled_tiles = []
        if mode == "Lunatic":
            #Arrange arbitrary tiles
            for rows in self.tiles:
                for cols in rows:
                    shuffled_tiles.append(cols)
            random.shuffle(shuffled_tiles)
        else:
            #Filter out visible tiles
            visible_tiles = []
            for rows in self.tiles:
                for cols in rows:
                    if cols.visible:
                        visible_tiles.append(cols)

            #Avoid cases where the parity goes wrong
            if len(visible_tiles) % 2 != 0:
                raise ValueError("Invalid inputs, shuffle may implement!")

            #Group pairs into the list using Dictionaries
            tile_dict = defaultdict(list)
            for tile in visible_tiles:
                tile_dict[tile.animal_tile].append(tile)

            grouped_pairs = []
            for animal_type, tiles in tile_dict.items():
                for i in range(0, len(tiles), 2):
                    if i + 1 < len(tiles):
                        grouped_pairs.append((tiles[i], tiles[i + 1]))

            #Shuffle pairs
            random.shuffle(grouped_pairs)

            #Retrieve shuffle tiles back to the board
            for pair in grouped_pairs:
                shuffled_tiles.extend(pair)

            for rows in range(self.rows):
                for cols in range(self.cols):
                    if mode == "Lunatic" or self.tiles[rows][cols].visible:
                        if shuffled_tiles: #Ensure the list is not empty
                            # .pop(0): remove index of the first element and return itself.
                            self.tiles[rows][cols] = shuffled_tiles.pop(0)

            self.display_board()












