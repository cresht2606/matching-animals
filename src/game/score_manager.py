class Score:
    def __init__(self, score, multiplier, combo, time_added):
        self.score = 0
        self.multiplier = 1
        self.combo = 1
        self.time_added = 0

    #Score management
    def add_score(self):
        if self.combo == 1 or self.combo == 2:
            self.score += 15
        elif self.combo >= 3:
            self.multiplier = 1 + 0.5 * (self.combo - 3)
            self.score += 15 * self.multiplier
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
        #else:
        #    self.time_added = 10

    def update_combo(self):
        #... When the game_manager class complete, keep on the trigger system
        self.combo += 1