import json
import os
from datetime import datetime

from scripts.achievements import AchievementSystem


def get_data():
    with open("config/data.json", "r") as file:
        return json.load(file)


def get_serverdata(interaction=None):
    if interaction is not None:
        check_server(interaction)

    with open("config/serverdata.json", "r") as file:
        return json.load(file)


def get_footer():
    data = get_data()
    return f"{data['footer_text']} | Version: {data['version']}"


def user(interaction):
    if interaction.user != interaction.message.interaction.user:
        return False

    return True

def formatt_int(longint:int):
    return f"{longint:,}".replace(",", ".")


def counts(user_id, guild_id, type: str):
    serverdata = get_serverdata()
    user_data = serverdata[str(guild_id)]["users"][str(user_id)]

    user_data["counts"][type] += 1

    if type == "count_gambles":
        user_data["last_gamble"] = datetime.now().date().isoformat()

    serverdata[str(guild_id)]["users"][str(user_id)] = user_data
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)


def check_server(interaction):
    serverdata = get_serverdata()
    guild_id = interaction.guild.id

    server_data = {
        "config": {
            "prefix": "!",
            "daily_reward": 100,
            "bot_enabled": "True",
            "max_transactions": 1000000,
            "max_bet": 1000000,
            "banned_players": [],
        },
        "info": get_serverinfo(interaction),
        "bank": 0,
        "users": {},
    }

    if str(guild_id) not in serverdata:
        serverdata[str(guild_id)] = server_data
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

    # Check and add missing keys
    for key, value in server_data.items():
        if key not in serverdata[str(guild_id)]:
            serverdata[str(guild_id)][key] = value

    # Check and add missing keys
    for key, value in server_data["config"].items():
        if key not in serverdata[str(guild_id)]["config"]:
            serverdata[str(guild_id)]["config"][key] = value

    # Check and add missing keys
    for key, value in server_data["info"].items():
        if key not in serverdata[str(guild_id)]["info"]:
            serverdata[str(guild_id)]["info"][key] = value


    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)

    return serverdata[str(guild_id)]


def check_user(interaction, target=None):
    serverdata = get_serverdata()
    guild_id = interaction.guild.id
    user_id = target or interaction.user.id

    if str(guild_id) not in serverdata:
        check_server(interaction)
        serverdata = get_serverdata()

    guild_data = serverdata[str(guild_id)]
    if "users" not in guild_data:
        guild_data["users"] = {}

    default_user_data = {
        "balance": 1000,
        "last_daily": "Never",
        "last_wheel": "Never",
        "inventory": [],
        "last_gamble": None,
        "counts": {
            k: 0
            for k in [
                "count_gambles",
                "count_winnings",
                "count_leaves",
                "count_doubles",
                "count_dayly",
                "count_red",
                "count_green",
                "count_black",
                "count_top_leaderboard",
            ]
        },
    }

    # Add missing keys for user
    if str(user_id) not in guild_data["users"]:
        guild_data["users"][str(user_id)] = default_user_data
    else:
        user_data = guild_data["users"][str(user_id)]
        for key, value in default_user_data.items():
            if key not in user_data:
                user_data[key] = value
            elif isinstance(value, dict):
                # Handle nested dictionaries
                for sub_key, sub_value in value.items():
                    if sub_key not in user_data[key]:
                        user_data[key][sub_key] = sub_value

    serverdata[str(guild_id)] = guild_data
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)

    user_data = guild_data["users"][str(user_id)]
    achievement_system = AchievementSystem(user_data)
    new_achievements = achievement_system.check_achievements()

    if new_achievements:
        user_data["inventory"].extend(
            [a for a in new_achievements if a not in user_data["inventory"]]
        )

        serverdata[str(guild_id)]["users"][str(user_id)] = user_data
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

    return user_data


def check_banned(interaction):
    serverdata = get_serverdata()
    guild_id = str(interaction.guild.id)
    if str(guild_id) not in serverdata:
        check_server(interaction)
        serverdata = get_serverdata()
    if guild_id not in serverdata:
        return True

    if "banned_players" not in serverdata[guild_id]["config"]:
        serverdata[guild_id]["config"]["banned_players"] = []

    if (
        serverdata["developer_mode"]
        and interaction.user.id not in get_data()["developer"]
    ):
        return True

    banned_players = serverdata[guild_id]["config"]["banned_players"]
    return interaction.user.id in banned_players


def subtract_balance(user_id, interaction, amount):
    serverdata = get_serverdata()
    guild_id = interaction.guild.id
    user_data = check_user(interaction, target=user_id)

    if user_data["balance"] < amount:
        user_data["balance"] = 0
    else:
        user_data["balance"] -= amount

    serverdata[str(guild_id)]["users"][str(user_id)] = user_data
    serverdata[str(guild_id)]["bank"] += amount
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)



def add_balance(user_id, interaction, amount):
    serverdata = get_serverdata()
    guild_id = interaction.guild.id
    user_data = check_user(interaction, target=user_id)

    if user_data["balance"] + amount >= get_data()["max_balance"]:
        user_data["balance"] = get_data()["max_balance"]
    else:
        user_data["balance"] += amount

    serverdata[str(guild_id)]["users"][str(user_id)] = user_data
    serverdata[str(guild_id)]["bank"] -= amount
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)

    if is_richest(user_id, guild_id):
        counts(user_id, guild_id, "count_top_leaderboard")


def multiply_balance(user_id, interaction, multiplier):
    user_data = check_user(interaction, target=user_id)

    amount = user_data["balance"] * multiplier
    add_balance(user_id, interaction, amount)


def create_daily_log_file():
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/casino_{current_date}.log"

    if not os.path.exists(filename):
        with open(filename, "w") as log_file:
            log_file.write(f"Casino Log for {current_date}\n")


def is_richest(user_id, guild_id):
    serverdata = get_serverdata()
    guild_data = serverdata[str(guild_id)]
    richest_user = max(
        guild_data["users"], key=lambda x: guild_data["users"][x]["balance"]
    )

    return str(user_id) == richest_user


def log(user_id, username, action, filename):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/casino_{current_date}.log"

    create_daily_log_file()

    with open(filename, "a") as log_file:
        log_file.write(
            f"[{datetime.now()}] {user_id} - {username} - {action} - {filename}\n"
        )


def get_serverinfo(interaction):
    guild = interaction.guild

    # Gathering general guild information
    guild_info = {
        "id": guild.id,
        "name": guild.name,
        "owner_id": guild.owner_id,
        "member_count": guild.member_count,
        "created_at": str(guild.created_at),
        "region": str(guild.region) if hasattr(guild, "region") else "N/A",
        "description": guild.description,
        "boost_count": guild.premium_subscription_count,
        "boost_tier": guild.premium_tier,
        "channels": [],
        "roles": [],
        "members": [],
    }

    # Gathering channel information
    for channel in guild.channels:
        guild_info["channels"].append(
            {
                "id": channel.id,
                "name": channel.name,
                "type": str(channel.type),
                "category": channel.category.name if channel.category else None,
                "position": channel.position,
            }
        )

    # Gathering role information
    for role in guild.roles:
        guild_info["roles"].append(
            {
                "id": role.id,
                "name": role.name,
                "color": str(role.color),
                "permissions": str(role.permissions),
                "position": role.position,
            }
        )

    # Gathering member information
    for member in guild.members:
        guild_info["members"].append(
            {
                "id": member.id,
                "name": member.name,
                "discriminator": member.discriminator,
                "nickname": member.nick,
                "roles": [role.name for role in member.roles],
                "joined_at": str(member.joined_at),
                "status": str(member.status),
            }
        )

    return guild_info