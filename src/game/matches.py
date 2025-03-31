from board import Board
from tile import Tile


class Matches:
    def __init__(self, board: Board):
        self.board = board

    def possible_matches(self):
        """
        Return a list of all possible matching pairs; if none,
        return an empty list (or optionally None).
        """
        pos_match = []
        for r1 in range(self.board.rows):
            for c1 in range(self.board.cols):
                tile1 = self.board.tiles[r1][c1]
                if not tile1.visible:
                    continue
                # We start the second loop from the current tile to avoid duplicates.
                for r2 in range(r1, self.board.rows):
                    # For each row, calculate start column based on if same row or not.
                    start = c1 + 1 if r1 == r2 else 0
                    for c2 in range(start, self.board.cols):
                        tile2 = self.board.tiles[r2][c2]
                        if tile1 == tile2 or not tile2.visible:
                            continue
                        if self.is_valid_path(tile1, tile2):
                            pos_match.append((tile1, tile2))
        return pos_match if pos_match else None

    def is_valid_matches(self, tile1: Tile, tile2: Tile) -> bool:
        """
        Check that two tiles are identical and visible.
        Side effect: Increase mismatch counter if not matching.
        """
        if tile1.animal_tile != tile2.animal_tile or not tile1.visible or not tile2.visible:
            self.board.mismatches += 1
            return False
        return True

    def is_valid_path(self, tile1: Tile, tile2: Tile) -> bool:
        """
        Returns True if a valid connecting path between tile1 and tile2 exists.
        """
        # First, check base matching conditions.
        if not self.is_valid_matches(tile1, tile2):
            return False

        # Evaluate each possible path shape in order
        if any([self.is_straight_line(tile1, tile2),
                self.is_Z_line(tile1, tile2),
                self.is_L_line(tile1, tile2)]):
            return True

        # If in player's turn, count as mismatch.
        if self.board.is_player_turn:  # Make sure board has is_player_turn attribute defined.
            self.board.mismatches += 1
            self.check_mismatch_limit()
        return False

    def is_straight_line(self, tile1: Tile, tile2: Tile) -> bool:
        """
        Check straight-line connection. Assumes board.tiles is indexed by [row][col],
        where tile.x is the column and tile.y is the row.
        """
        if tile1.x == tile2.x:
            # Vertical path: iterate through rows between tile1 and tile2.
            min_y, max_y = min(tile1.y, tile2.y), max(tile1.y, tile2.y)
            for i in range(min_y + 1, max_y):
                # Check column index remains as tile1.x.
                if self.board.tiles[i][tile1.x].visible:
                    return False
            return True
        if tile1.y == tile2.y:
            # Horizontal path: iterate through columns between tile1 and tile2.
            min_x, max_x = min(tile1.x, tile2.x), max(tile1.x, tile2.x)
            for j in range(min_x + 1, max_x):
                if self.board.tiles[tile1.y][j].visible:
                    return False
            return True
        return False

    def is_Z_line(self, tile1: Tile, tile2: Tile) -> bool:
        """
        Checks for a 'Z' shaped connection.
        Two possible intermediate corners are tile1.x, tile2.y and tile2.x, tile1.y.
        Only proceed if one of the corners is invisible.
        """
        # Calculate potential intermediate corner positions.
        try:
            corner1 = self.board.tiles[tile2.y][tile1.x]
            corner2 = self.board.tiles[tile1.y][tile2.x]
        except IndexError:
            return False  # Out-of-bound indices

        # If corner1 is free, see if path can bend through it.
        if not corner1.visible:
            if self.is_straight_line(tile1, corner1) and self.is_straight_line(corner1, tile2):
                return True
        # Otherwise, if corner2 is free.
        if not corner2.visible:
            if self.is_straight_line(tile1, corner2) and self.is_straight_line(corner2, tile2):
                return True

        return False

    def is_L_line(self, tile1: Tile, tile2: Tile) -> bool:
        """
        Checks for an 'L' shaped connection.
        In an L-shape, there is one bend. There are two potential corners.
        """
        try:
            corner1 = self.board.tiles[tile2.y][tile1.x]
            corner2 = self.board.tiles[tile1.y][tile2.x]
        except IndexError:
            return False

        # Lower L-shape: if corner1 is free, then tile1->corner1 and tile2->corner1 are straight.
        if not corner1.visible:
            if self.is_straight_line(tile1, corner1) and self.is_straight_line(tile2, corner1):
                return True
        # Upper L-shape: if corner2 is free.
        if not corner2.visible:
            if self.is_straight_line(tile1, corner2) and self.is_straight_line(tile2, corner2):
                return True

        return False

    def check_mismatch_limit(self) -> bool:
        """
        Returns True if mismatches have reached or exceeded the limit for the current difficulty.
        """
        mismatch_map = {"Normal": 3, "Advanced": 3, "Lunatic": 2}
        limit = mismatch_map.get(self.board.diff, None)
        if limit is None:
            print("Unexpected behaviour... Returning to its default state")
            return False
        else:
            return self.board.mismatches >= limit
