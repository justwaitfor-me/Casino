import json
from datetime import datetime

from scripts.achievements import AchievementSystem

def get_data():
    with open("config/data.json", "r") as file:
        return json.load(file)


def get_userdata():
    with open("config/userdata.json", "r") as file:
        return json.load(file)


def user(interaction):
    if interaction.user != interaction.message.interaction.user:
        return False

    return True


def counts(user_id, type: str):
    userdata = get_userdata()

    userdata[str(user_id)]["counts"][type] += 1

    if type == "gamble":
        userdata[str(user_id)]["last_gamble"] = datetime.now().date()

    with open("config/userdata.json", "w") as file:
        json.dump(userdata, file, indent=4)


def check_user(user_id):
    userdata = get_userdata()

    if str(user_id) not in userdata:
        user_data = {
            "balance": 1000,
            "last_daily": None,
            "inventory": [],
            "last_gamble": None,
            "counts": {
                "count_gambles": 0,
                "count_winnings": 0,
                "count_leaves": 0,
                "count_doubles": 0,
                "count_dayly": 0,
            },
        }

        # Create a new user in the data file
        userdata[str(user_id)] = user_data
        with open("config/userdata.json", "w") as file:
            json.dump(userdata, file, indent=4)

        return check_user(user_id)

    user_data = userdata[str(user_id)]

    # Check for new achievements
    achievement_system = AchievementSystem(user_data)
    new_achievements = achievement_system.check_achievements()

    # Add new achievements to the user's inventory
    for achievement in new_achievements:
        if achievement not in user_data["inventory"]:
            userdata[str(user_id)]["inventory"].append(achievement)

    # Update the user data file with new achievement
    with open("config/userdata.json", "w") as file:
        json.dump(userdata, file, indent=4)

    return userdata[str(user_id)]


def subtract_balance(user_id, amount):
    userdata = get_userdata()
    check_user(user_id)

    userdata[str(user_id)]["balance"] -= amount
    with open("config/userdata.json", "w") as file:
        json.dump(userdata, file, indent=4)


def add_balance(user_id, amount):
    userdata = get_userdata()
    check_user(user_id)

    userdata[str(user_id)]["balance"] += amount
    with open("config/userdata.json", "w") as file:
        json.dump(userdata, file, indent=4)
