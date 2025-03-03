class Tile:
    def __init__(self, x, y, animal_tile):
        self.x, self.y = x, y
        self.animal_tile = animal_tile
        self.visible = True

    #Printable representation of a tile: return False if it cannot be visible and vice versa.
    def __repr__(self):
        return f"[{self.animal_tile}]" if self.visible else "[X]"

#CLI Test
if __name__ == "__main__":
    tile1 = Tile(5, 7, "Cat")
    tile2 = Tile(8, 1, "Dog")

    print("Property of tile1", tile1)
    print("Property of tile2 - Before: ", tile2)
    tile2.visible = False
    print("Property of tile2 - After: ", tile2)
