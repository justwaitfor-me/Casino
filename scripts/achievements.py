import json

class AchievementSystem:
    def __init__(self, user_data):
        self.user_data = user_data
        with open("config/data.json", "r") as file:
            data = json.load(file)
        self.achievements = data.get("achievements", {})

    def check_achievements(self):
        achieved = []
        for key, achievement in self.achievements.items():
            if (
                "balance_required" in achievement
                and self.user_data.get("balance", 0) >= achievement['balance_required']
            ):
                achieved.append(key)
            if (
                "wins_required" in achievement
                and self.user_data.get("counts", {}).get("count_winnings", 0)
                >= achievement['wins_required']
            ):
                achieved.append(key)
            if (
                "doubles_required" in achievement
                and self.user_data.get("counts", {}).get("count_doubles", 0)
                >= achievement['doubles_required']
            ):
                achieved.append(key)
            if (
                "leaves_required" in achievement
                and self.user_data.get("counts", {}).get("count_leaves", 0)
                >= achievement['leaves_required']
            ):
                achieved.append(key)
            if (
                "days_claimed_required" in achievement
                and self.user_data.get("counts", {}).get("count_dayly", 0)
                >= achievement['days_claimed_required']
            ):
                achieved.append(key)
            if (
                "leaderboard_first_required" in achievement
                and self.user_data.get("counts", {}).get("count_top_leaderboard", 0)
                >= achievement['leaderboard_first_required']
            ):
                achieved.append(key)
            if (
                "roulette_green_bets_required" in achievement
                and self.user_data.get("counts", {}).get("count_green", 0)
                >= achievement['roulette_green_bets_required']
            ):
                achieved.append(key)
        return achieved

def get_achievement(achievement):
    with open("config/data.json", "r") as file:
        data = json.load(file)
    achievements = data.get("achievements", {})

    if isinstance(achievement, list):
        return [[achievements.get(ach, {}).get("name"), achievements.get(ach, {}).get("emoji")] for ach in achievement]
    else:
        return [achievements.get(achievement, {}).get("name"), achievements.get(achievement, {}).get("emoji")]

if __name__ == "__main__":
    print(get_achievement("balance_patch_1"))
    print(get_achievement(['balance_patch_1", "wins_patch_1']))

