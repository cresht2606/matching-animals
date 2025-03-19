from board import *
from tile import *

class Matches:
    def __init__(self, board):
        self.board = board

    #Check valid matches
    def possible_matches(self):
        #Storing pairs as tuples
        pos_match = []
        for r1 in range(self.board.rows):
            for c1 in range(self.board.cols):
                tile1 = self.board.tiles[r1][c1]
                #Base case: if it doesn't exist any tiles → skip the current tile
                if not tile1.visible:
                    continue
                for r2 in range(r1, self.board.rows):
                    for c2 in range((c1 + 1) if r1 == r2 else 0, self.board.cols):
                        tile2 = self.board.tiles[r2][c2]
                        #Both tiles must be different and visible
                        if tile1 != tile2 and tile2.visible:
                            if self.is_valid_path(tile1, tile2):
                                pos_match.append((tile1, tile2))
        return pos_match if pos_match else None

    # Check if tiles are identical and visible
    def is_valid_matches(self, tile1, tile2):
        if tile1.animal_tile != tile2.animal_tile or not tile1.visible or not tile2.visible:
            self.board.mismatches += 1
            return False
        return True

    #Helper function to pass through each condition type
    def is_valid_path(self, tile1, tile2):
        #First check: if two tiles are non-identical
        if not self.is_valid_matches(tile1, tile2):
            return False

        #Second check: if two tiles are identical but neither in any shapes
        if any([self.is_straight_line(tile1, tile2),
                self.is_Z_line(tile1, tile2),
                self.is_L_line(tile1, tile2)
                ]):
            return True

        #Else return False and trigger the mismatch system
        if self.board.is_player_turn:
            self.board.mismatches += 1
            self.check_mismatch_limit()
        return False

    #Check valid paths
    def is_straight_line(self, tile1, tile2):
        if tile1.x == tile2.x:
            min_y, max_y = min(tile1.y, tile2.y), max(tile1.y, tile2.y)
            for i in range(min_y + 1, max_y):
                if self.board.tiles[tile1.x][i].visible:
                    return False
            return True

        if tile1.y == tile2.y:
            min_x, max_x = min(tile1.x, tile2.x), max(tile1.x, tile2.x)
            for j in range(min_x + 1, max_x):
                #In the interval between two matches, if there is an obstacle
                if self.board.tiles[j][tile1.y].visible == True:
                    return False
            return True


    def is_Z_line(self, tile1, tile2):
        corner1, corner2 = self.board.tiles[tile1.x][tile2.y], self.board.tiles[tile2.x][tile1.y]
        middle1, middle2 = self.board.tiles[tile1.x][tile1.y], self.board.tiles[tile2.x][tile2.y]

        if not corner1.visible:
            if self.is_straight_line(tile1, corner1) and self.is_straight_line(corner1, middle1) and self.is_straight_line(middle1, tile2):
                return True
        if not corner2.visible:
            if self.is_straight_line(tile1, corner2) and self.is_straight_line(corner2, middle2) and self.is_straight_line(middle2, tile2):
                return True
        return False

    def is_L_line(self, tile1, tile2):
        corner1, corner2 = self.board.tiles[tile1.x][tile2.y], self.board.tiles[tile2.x][tile1.y]
        #Check lower L-shape
        if not corner1.visible:
            if self.is_straight_line(tile1, corner1) and self.is_straight_line(tile2, corner1):
                return True

        #Check upper L-shape
        if not corner2.visible:
            if self.is_straight_line(tile1, corner2) and self.is_straight_line(tile2, corner2):
                return True
        return False

    #Boolean expression for checking mismatches - difficulty
    def check_mismatch_limit(self):
        mismatch_map = {"Normal" : 3, "Advanced" : 3, "Lunatic" : 2}
        limit = mismatch_map.get(self.board.diff, None)
        if limit is None:
            print("Unexpected behaviour... Returning to its default state")
            return False
        else:
            return self.board.mismatches >= limit