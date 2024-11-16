import json
import os
from datetime import datetime

from scripts.achievements import AchievementSystem


def get_data():
    with open("config/data.json", "r") as file:
        return json.load(file)


def get_serverdata(guild_id = None):
    if guild_id is not None:
        check_server(guild_id)

    with open("config/serverdata.json", "r") as file:
        return json.load(file)


def user(interaction):
    if interaction.user != interaction.message.interaction.user:
        return False

    return True


def counts(user_id, guild_id, type: str):
    serverdata = get_serverdata()
    user_data = serverdata[str(guild_id)]['users'][str(user_id)]

    user_data['counts'][type] += 1

    if type == "count_gambles":
        user_data['last_gamble'] = datetime.now().date().isoformat()

    serverdata[str(guild_id)]['users'][str(user_id)] = user_data
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)


def check_server(guild_id):
    serverdata = get_serverdata()

    if str(guild_id) not in serverdata:
        server_data = {
            "config": {
                "prefix": "!",
                "daily_reward": 100,
                "bot_enabled": "True",
                "max_transactions": 1000000,
                "max_bet": 1000000,
            },
            "users": {},
        }

        serverdata[str(guild_id)] = server_data
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

        return check_server(guild_id)

    return serverdata[str(guild_id)]


def check_user(user_id, guild_id):
    serverdata = get_serverdata()
    if str(guild_id) not in serverdata:
        check_server(guild_id)
        serverdata = get_serverdata()

    guild_data = serverdata[str(guild_id)]
    if "users" not in guild_data:
        guild_data['users'] = {}

    if str(user_id) not in guild_data['users']:
        guild_data['users'][str(user_id)] = {
            "balance": 1000,
            "last_daily": "Never",
            "inventory": [],
            "last_gamble": None,
            "counts": {k: 0 for k in ["count_gambles", "count_winnings", "count_leaves", "count_doubles", 
                                      "count_dayly", "count_red", "count_green", "count_black", "count_top_leaderboard"]}
        }

        serverdata[str(guild_id)] = guild_data
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

    user_data = guild_data['users'][str(user_id)]
    achievement_system = AchievementSystem(user_data)
    new_achievements = achievement_system.check_achievements()

    if new_achievements:
        user_data['inventory'].extend([a for a in new_achievements if a not in user_data['inventory']])

        serverdata[str(guild_id)]['users'][str(user_id)] = user_data
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

    return user_data


def subtract_balance(user_id, guild_id, amount):
    serverdata = get_serverdata()
    user_data = check_user(user_id, guild_id)

    user_data['balance'] -= amount

    serverdata[str(guild_id)]['users'][str(user_id)] = user_data
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)


def create_daily_log_file():
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/casino_{current_date}.log"

    if not os.path.exists(filename):
        with open(filename, "w") as log_file:
            log_file.write(f"Casino Log for {current_date}\n")


def is_richest(user_id, guild_id):
    serverdata = get_serverdata()
    guild_data = serverdata[str(guild_id)]
    richest_user = max(guild_data['users'], key=lambda x: guild_data['users'][x]['balance'])

    return str(user_id) == richest_user


def log(user_id, username, action, filename):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/casino_{current_date}.log"

    create_daily_log_file()

    with open(filename, "a") as log_file:
        log_file.write(
            f"[{datetime.now()}] {user_id} - {username} - {action} - {filename}\n"
        )


def add_balance(user_id, guild_id, amount):
    serverdata = get_serverdata()
    user_data = check_user(user_id, guild_id)

    user_data['balance'] += amount
    serverdata[str(guild_id)]['users'][str(user_id)] = user_data
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)

    if is_richest(user_id, guild_id):
        counts(user_id, guild_id, "count_top_leaderboard")

