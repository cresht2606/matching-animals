from board import *
class AnimalType:
    #Normal + Advanced Gamemode
    Normanced = []
    #Lunatic Gamemode
    Lunatic = []
    @classmethod
    def get_animals(cls, difficulty):
        if difficulty == "Normal" or difficulty == "Advanced":
            return cls.Normanced
        elif difficulty == "Lunatic":
            return cls.Lunatic
        else:
            raise AttributeError("Invalid difficulty")

class Tile:
    def __init__(self, x, y, animal_tile):
        self.x, self.y = x, y
        self.animal_tile = animal_tile
        self.visible = True

    #Printable representation of a tile: return False if it cannot be visible and vice versa.
    def __repr__(self):
        return f"[{self.animal_tile}]" if self.visible else "[X]"

