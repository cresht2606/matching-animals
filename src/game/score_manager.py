class Score:
    def __init__(self):
        self.score = 0
        self.multiplier = 1
        self.combo = 1
        self.time_added = 0

    #Score management
    def add_score(self):
        if self.combo == 1 or self.combo == 2:
            self.multiplier = 1
            self.score += 15
        elif self.combo >= 3:
            self.multiplier = 1 + 0.5 * (self.combo - 2)
            self.score += int(15 * self.multiplier)

    def reset_score(self):
        self.score = 0
        self.multiplier = 1
        self.combo = 1
        self.time_added = 0

    def return_score(self):
        return f"Total score: {self.score}"

    #Enhancements
    def apply_time_bonus(self):
        default_time_bonus = [12, 15, 17, 20, 25, 30]
        if self.combo >= 3: #Must start at 3rd consecutive combo
            index = min(self.combo - 3, len(default_time_bonus) - 1)
            self.time_added += default_time_bonus[index]

    def update_combo(self, matched):
        #If it's matched -> Update the combo. Else reset the combo if mismatches or time runs out (Soon)
        if matched:
            self.combo = min(self.combo + 1, 10)
        else:
            self.combo = 1


def test_score():
    print("Initializing Score System...")
    score = Score()

    # Simulate multiple match events:
    print(">>> Simulating 6 consecutive matches...")
    for i in range(6):
        score.update_combo(True)
        score.add_score()
        score.apply_time_bonus()
        print(f"After match {i+1} => Combo: {score.combo}, Score: {score.score}, Time Bonus: {score.time_added}")

    # Print results after a series of successful updates:
    print("\nResults after consecutive matches:")
    print(f"Total score: {score.return_score()}")
    print(f"Total combos: {score.combo}")

    # Simulate a mismatch
    print("\nSimulating a mismatch...")
    score.update_combo(False)
    score.add_score()
    score.apply_time_bonus()

    # Results after mismatch:
    print("Results after a mismatch:")
    print(f"Total score: {score.return_score()}")
    print(f"Total combos: {score.combo}")

if __name__ == "__main__":
    test_score()
