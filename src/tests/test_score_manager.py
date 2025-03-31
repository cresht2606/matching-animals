import unittest
from score_manager import Score  # Adjust the import as necessary for your project structure

class TestScoreManager(unittest.TestCase):
    def setUp(self):
        self.score_manager = Score()

    def test_initial_state(self):
        # When first created, Score should have all values at their defaults.
        self.assertEqual(self.score_manager.score, 0)
        self.assertEqual(self.score_manager.combo, 1)
        self.assertEqual(self.score_manager.multiplier, 1)
        self.assertEqual(self.score_manager.time_added, 0)

    def test_add_score_base_combo(self):
        # For combo values 1 and 2, no multiplier bonus is applied.
        self.score_manager.combo = 1
        self.score_manager.add_score()
        self.assertEqual(self.score_manager.score, 15)
        self.assertEqual(self.score_manager.multiplier, 1)

        # Reset and test for combo 2:
        self.score_manager.reset_score()
        self.score_manager.combo = 2
        self.score_manager.add_score()
        self.assertEqual(self.score_manager.score, 15)
        self.assertEqual(self.score_manager.multiplier, 1)

    def test_add_score_with_combo_bonus(self):
        # For combos >= 3, the multiplier applies.
        self.score_manager.combo = 3  # Multiplier should be 1 + 0.5*(3-2) = 1.5
        self.score_manager.add_score()
        expected_points = int(15 * 1.5)
        self.assertEqual(self.score_manager.score, expected_points)
        self.assertEqual(self.score_manager.multiplier, 1.5)

    def test_update_combo_matched(self):
        # When matched=True, combo should increment up to the cap (10).
        self.score_manager.combo = 1
        self.score_manager.update_combo(True)
        self.assertEqual(self.score_manager.combo, 2)
        # Test maximum cap behavior:
        self.score_manager.combo = 10
        self.score_manager.update_combo(True)
        self.assertEqual(self.score_manager.combo, 10)

    def test_update_combo_not_matched(self):
        # When matched=False, combo should reset to 1.
        self.score_manager.combo = 5
        self.score_manager.update_combo(False)
        self.assertEqual(self.score_manager.combo, 1)

    def test_apply_time_bonus(self):
        # No bonus should apply if combo is less than 3.
        self.score_manager.combo = 1
        self.score_manager.apply_time_bonus()
        self.assertEqual(self.score_manager.time_added, 0)

        # For combo 3, bonus should be the first element: 12 seconds.
        self.score_manager.reset_score()
        self.score_manager.combo = 3
        self.score_manager.apply_time_bonus()
        self.assertEqual(self.score_manager.time_added, 12)

        # For combo 4, bonus should be 15 seconds.
        self.score_manager.reset_score()
        self.score_manager.combo = 4
        self.score_manager.apply_time_bonus()
        self.assertEqual(self.score_manager.time_added, 15)

    def test_reset_score(self):
        # Modify state values, then reset and verify they return to defaults.
        self.score_manager.score = 100
        self.score_manager.combo = 5
        self.score_manager.multiplier = 2
        self.score_manager.time_added = 50
        self.score_manager.reset_score()
        self.assertEqual(self.score_manager.score, 0)
        self.assertEqual(self.score_manager.combo, 1)
        self.assertEqual(self.score_manager.multiplier, 1)
        self.assertEqual(self.score_manager.time_added, 0)

    def test_return_score(self):
        # Check if the formatted string is correct.
        self.score_manager.score = 90
        self.assertEqual(self.score_manager.return_score(), "Total score: 90")

if __name__ == '__main__':
    unittest.main()
