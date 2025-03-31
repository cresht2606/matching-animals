import unittest
from test_models import Tile, AnimalType

class TestAnimalType(unittest.TestCase):
    def setUp(self):
        # For testing, we populate the lists with sample data.
        AnimalType.Normanced = ["Lion", "Tiger", "Elephant"]
        AnimalType.Lunatic = ["Hippo", "Rhino"]

    def test_get_animals_normal(self):
        # For Normal and Advanced difficulties, Normanced list is expected.
        animals_normal = AnimalType.get_animals("Normal")
        self.assertEqual(animals_normal, AnimalType.Normanced)
        animals_advanced = AnimalType.get_animals("Advanced")
        self.assertEqual(animals_advanced, AnimalType.Normanced)

    def test_get_animals_lunatic(self):
        # For Lunatic difficulty, the Lunatic list should be returned.
        animals_lunatic = AnimalType.get_animals("Lunatic")
        self.assertEqual(animals_lunatic, AnimalType.Lunatic)

    def test_get_animals_invalid(self):
        # An invalid difficulty should raise an AttributeError.
        with self.assertRaises(AttributeError):
            AnimalType.get_animals("Easy")

class TestTile(unittest.TestCase):
    def setUp(self):
        # Create a sample Tile with a simple string for the asset (e.g., "Lion").
        self.tile = Tile(0, 0, "Lion")

    def test_initial_values(self):
        # Verify that the Tile is set to its correct initial state.
        self.assertEqual(self.tile.x, 0)
        self.assertEqual(self.tile.y, 0)
        self.assertEqual(self.tile.animal_tile, "Lion")
        self.assertTrue(self.tile.visible)
        self.assertFalse(self.tile.locked)
        self.assertFalse(self.tile.bomb)
        self.assertFalse(self.tile.gold)
        self.assertFalse(self.tile.exploded)
        self.assertFalse(self.tile.acid)

    def test_repr_visible(self):
        # Check that when the tile is visible, __repr__ returns the animal asset.
        expected_repr = "[Lion]"
        self.assertEqual(repr(self.tile), expected_repr)

    def test_repr_invisible(self):
        # When the tile is not visible, __repr__ should return "[X]".
        self.tile.visible = False
        expected_repr = "[X]"
        self.assertEqual(repr(self.tile), expected_repr)

if __name__ == "__main__":
    unittest.main()
