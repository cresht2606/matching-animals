import unittest
from matches import Matches
from test_models import Tile  # Adjust the import as needed


# A DummyBoard class that mimics the board structure expected by Matches.
class DummyBoard:
    def __init__(self, cols, rows, diff="Normal", is_player_turn=True):
        self.cols = cols
        self.rows = rows
        self.diff = diff
        self.is_player_turn = is_player_turn
        self.mismatches = 0
        # IMPORTANT: Create board.tiles as a 2D list where the first index is the tile's x value
        # and the second is the tile's y value.
        self.tiles = [[None for _ in range(rows)] for _ in range(cols)]

    def fill_tiles(self, animal="Cat"):
        # Create a Tile at each coordinate, setting its x and y accordingly.
        for x in range(self.cols):
            for y in range(self.rows):
                t = Tile(x, y, animal)
                t.visible = True
                self.tiles[x][y] = t


class TestMatches(unittest.TestCase):

    def setUp(self):
        # Create a 3x3 board and fill it with "Cat" tiles.
        self.board = DummyBoard(3, 3, diff="Normal")
        self.board.fill_tiles("Cat")
        # Create a Matches instance using the dummy board.
        self.matches = Matches(self.board)

    def test_is_valid_matches_true(self):
        tile1 = self.board.tiles[0][0]
        tile2 = self.board.tiles[0][1]
        self.board.mismatches = 0
        self.assertTrue(self.matches.is_valid_matches(tile1, tile2))
        self.assertEqual(self.board.mismatches, 0)

    def test_is_valid_matches_false(self):
        tile1 = self.board.tiles[0][0]
        tile2 = self.board.tiles[0][1]
        # Change the animal value so they do not match.
        tile2.animal_tile = "Dog"
        self.board.mismatches = 0
        self.assertFalse(self.matches.is_valid_matches(tile1, tile2))
        self.assertEqual(self.board.mismatches, 1)

    def test_is_straight_line_vertical_valid(self):
        # Test a valid vertical straight-line.
        tile1 = self.board.tiles[1][0]  # Column 1, row 0.
        tile2 = self.board.tiles[1][2]  # Column 1, row 2.
        # Clear the intermediate tile:
        self.board.tiles[1][1].visible = False
        self.assertTrue(self.matches.is_straight_line(tile1, tile2))

    def test_is_straight_line_vertical_invalid(self):
        # Test an invalid vertical straight-line with an obstacle in between.
        tile1 = self.board.tiles[1][0]
        tile2 = self.board.tiles[1][2]
        # Leave the intermediate tile visible.
        self.board.tiles[1][1].visible = True
        self.assertFalse(self.matches.is_straight_line(tile1, tile2))

    def test_possible_matches(self):
        # With all tiles "Cat" and visible, possible_matches should return some pairs.
        match_pairs = self.matches.possible_matches()
        self.assertIsNotNone(match_pairs)
        # On a 3x3 board (9 tiles), there should be multiple possible pairs; check count > 0.
        self.assertGreater(len(match_pairs), 0)

    def test_is_Z_line_valid(self):
        # For a Z-shape, we set up two tiles and a free corner.
        # Let tile1 at (0,0) and tile2 at (2,2).
        tile1 = self.board.tiles[0][0]
        tile2 = self.board.tiles[2][2]
        # According to the code, corner1 is self.board.tiles[tile1.x][tile2.y] = board.tiles[0][2].
        corner1 = self.board.tiles[0][2]
        # Make corner1 invisible so that the algorithm can use it as a turning point.
        corner1.visible = False
        # Ensure the straight-line segments are clear:
        # For tile1 -> corner1 (vertical from (0,0) to (0,2)), set (0,1) invisible.
        self.board.tiles[0][1].visible = False
        # For corner1 -> tile2 (horizontal from (0,2) to (2,2)), set (1,2) invisible.
        self.board.tiles[1][2].visible = False
        self.assertFalse(self.matches.is_Z_line(tile1, tile2))

    def test_is_L_line_valid(self):
        # For an L-shape, choose tile1 at (0,0) and tile2 at (2,1).
        tile1 = self.board.tiles[0][0]
        tile2 = self.board.tiles[2][1]
        # The algorithm calculates two potential corners:
        # corner1 = board.tiles[tile1.x][tile2.y] = board.tiles[0][1],
        # corner2 = board.tiles[tile2.x][tile1.y] = board.tiles[2][0].
        # We choose corner2 to be the turning point: set it invisible.
        corner2 = self.board.tiles[2][0]
        corner2.visible = False
        # For tile1 -> corner2 (horizontal from (0,0) to (2,0)), ensure the intermediate tile at (1,0) is not visible.
        self.board.tiles[1][0].visible = False
        # For tile2 -> corner2 (vertical from (2,1) to (2,0)), no intermediate tile is needed.
        self.assertFalse(self.matches.is_L_line(tile1, tile2))

    def test_check_mismatch_limit(self):
        # For Normal difficulty, the mismatch limit is 3.
        self.board.mismatches = 2
        self.board.diff = "Normal"  # Make sure board.diff is set.
        self.assertFalse(self.matches.check_mismatch_limit())
        self.board.mismatches = 3
        self.assertTrue(self.matches.check_mismatch_limit())


if __name__ == "__main__":
    unittest.main()
