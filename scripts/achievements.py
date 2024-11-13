import json

class AchievementSystem:
    def __init__(self, user_data):
        self.user_data = user_data
        with open("config\data.json", "r") as file:
            data = json.load(file)
        self.achievements = data.get("achievements", {})

    def check_achievements(self):
        achieved = []
        for key, achievement in self.achievements.items():
            if (
                "balance_required" in achievement
                and self.user_data.get("balance", 0) >= achievement["balance_required"]
            ):
                achieved.append(achievement["name"])
            if (
                "wins_required" in achievement
                and self.user_data.get("counts", {}).get("count_winnings", 0)
                >= achievement["wins_required"]
            ):
                achieved.append(achievement["name"])
            if (
                "doubles_required" in achievement
                and self.user_data.get("counts", {}).get("count_doubles", 0)
                >= achievement["doubles_required"]
            ):
                achieved.append(achievement["name"])
            if (
                "leaves_required" in achievement
                and self.user_data.get("counts", {}).get("count_leaves", 0)
                >= achievement["leaves_required"]
            ):
                achieved.append(achievement["name"])
            if (
                "days_claimed_required" in achievement
                and self.user_data.get("counts", {}).get("count_dayly", 0)
                >= achievement["days_claimed_required"]
            ):
                achieved.append(achievement["name"])
            if key == "leaderboard_patch_1" and self.user_data.get(
                "is_top_leaderboard", False
            ):
                achieved.append(achievement["name"])
        return achieved
