from typing import List, Any
class AnimalType:
    """
    Manages animal resources for different game modes.

    Attributes:
        Normanced (List[Any]): Animal identifiers or images for Normal/Advanced modes.
        Lunatic (List[Any]): Animal identifiers or images for Lunatic mode.
    """

    Normanced: List[Any] = []
    Lunatic: List[Any] = []
    @classmethod
    def get_animals(cls, difficulty):
        """
        Retrieves the list of animal resources based on the selected game difficulty.

        Args:
            difficulty (str): Must be either "Normal", "Advanced", or "Lunatic".

        Returns:
            List[Any]: The corresponding list of animal assets.

        Raises:
            AttributeError: If an invalid difficulty is provided.
        """
        if difficulty == "Normal" or difficulty == "Advanced":
            return cls.Normanced
        elif difficulty == "Lunatic":
            return cls.Lunatic
        else:
            raise AttributeError("Invalid difficulty")

class Tile:
    """
    Represents a single game tile in Matching Animals.

    Attributes:
        x (int): The tile's x-coordinate.
        y (int): The tile's y-coordinate.
        animal_tile (Any): The animal asset or identifier. This could be an image, a string, etc.
        visible (bool): Determined if the tile is visible.
        locked (bool): Indicates a temporary locked state.
        bomb (bool): Indicates if the tile has a bomb effect.
        gold (bool): Indicates if the tile contains a bonus (gold) effect.
        exploded (bool): Indicates if the tile has been exploded.
        acid (bool): Indicates if the tile is affected by an acid effect.
    """
    def __init__(self, x, y, animal_tile):
        self.x, self.y = x, y
        self.animal_tile = animal_tile
        self.visible = True

        #Temporary effects on each tiles
        self.locked = False
        self.bomb = False
        self.gold = False
        self.exploded = False
        self.acid = False

    #Printable representation of a tile: return False if it cannot be visible and vice versa.
    def __repr__(self):
        """
        Returns a string representation of the tile for debugging.
        If the tile is visible, displays the associated animal asset; otherwise, displays "[X]".
        """
        return f"[{self.animal_tile}]" if self.visible else "[X]"