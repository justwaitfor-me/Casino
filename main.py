import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select

from datetime import datetime
import os
import random
import json
import dotenv
import logging

from scripts.functions import (
    get_data,
    check_user,
    user,
    counts,
    get_serverdata,
    add_balance,
    subtract_balance,
    log,
    check_banned,
)
from scripts.engine import (
    blackjack_callback,
    guess_the_number_callback,
    double_or_nothing_callback,
    roulette_callback,
    slot_machine_callback,
)
from scripts.achievements import get_achievement

intents = discord.Intents.default()
intents.message_content = True

data = get_data()
dotenv.load_dotenv(".env")

current_date = datetime.now().strftime("%Y-%m-%d")
handler = logging.FileHandler(
    filename=f"logs/discord_{current_date}.log", encoding="utf-8", mode="w"
)


bot = commands.Bot(command_prefix="!", intents=intents)
casino_game = random.choice(data.get("casino_games", {}))

# Check if serverdata.json is there, if not make it
if not os.path.exists("config/serverdata.json"):
    with open("config/serverdata.json", "w") as file:
        json.dump({"developer_mode": False}, file)


@bot.event
async def on_ready():
    log(bot.user.id, bot.user.name, "Bot started", __file__)
    print(f"Logged in as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="/help | /play",
            state="made by justwaitfor_me | assets by murmel265",
        )
    )


@bot.tree.command(name="help", description="Lists all available commands")
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def list(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/help command used", __file__)

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    commands_list = get_data()["commands"]

    embed = discord.Embed(
        title="Available Commands",
        description="\n".join([f"{cmd}: {desc}" for cmd, desc in commands_list]),
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(3, 4)}.png"
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="play", description="Play the casino games")
@app_commands.describe(bet="The amount you want to bet")
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def play(interaction: discord.Interaction, bet: int):
    log(
        interaction.user.id,
        interaction.user.name,
        f"/play command used with bet: {bet}",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    user_data = check_user(interaction)
    balance = user_data["balance"]

    max_bet = int(
        get_serverdata(interaction)[str(interaction.guild.id)]["config"][
            "max_bet"
        ]
    )

    if bet > max_bet:
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            f"The maximum transaction amount is {max_bet}$.",
            ephemeral=True,
        )
        return

    if bet <= 0:
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n" "Your bet must be greater than 0.",
            ephemeral=True,
        )
        return

    if balance < bet:
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            f"You don't have enough money to place this bet. Your current balance is {balance}$.",
            ephemeral=True,
        )
        return

    # Create a Select Menu
    games_menu = Select(
        placeholder="Choose a game...",  # Placeholder text for the menu
        options=[
            # Add options for each game
            discord.SelectOption(
                label="Blackjack",
                description="Play Blackjack",
                emoji="<:casinochip1:1304579248908009562>",
                value="blackjack",  # Unique identifier for this option
            ),
            discord.SelectOption(
                label="Double or Nothing",
                description="Play Double or Nothing",
                emoji="<:casinochip2:1304579236496932904>",
                value="double_or_nothing",
            ),
            discord.SelectOption(
                label="Roulette",
                description="Play Roulette",
                emoji="<:casinochip3:1304579224597954612>",
                value="roulette",
            ),
            discord.SelectOption(
                label="Guess the Number",
                description="Play Guess the Number",
                emoji="<:casinochip4:1304579213189189693>",
                value="guess_the_number",
            ),
            discord.SelectOption(
                label="Slot Machine",
                description="Play Slot Machine",
                emoji="<:casinochip5:1304579195560792185>",
                value="slot_machine",
            ),
            discord.SelectOption(
                label="Pferde Wetten",
                description="Currently unavailable",
                emoji="<:casinochip6:1307379735147577394>",
                value="pferde_wettem",
                default=False,  # You can set this as selected initially if needed
            ),
        ],
        row=1,  # Specify the row for the Select menu
    )

    # Define callback for the Select menu
    async def select_callback(interaction):
        # Check if the user interacting with the menu is the same as the one who invoked the command
        if not user(interaction):
            await interaction.response.send_message(
                "You can't interact with this menu.", ephemeral=True
            )
            return

        selected_game = games_menu.values[0]  # Get the selected value
        if selected_game == "blackjack":
            await blackjack_callback(interaction, bet)
        elif selected_game == "double_or_nothing":
            await double_or_nothing_callback(interaction, bet)
        elif selected_game == "roulette":
            await roulette_callback(interaction, bet)
        elif selected_game == "guess_the_number":
            await guess_the_number_callback(interaction, bet)
        elif selected_game == "slot_machine":
            await slot_machine_callback(interaction, bet)
        elif selected_game == "pferde_wettem":
            await interaction.response.send_message(
                "Pferde Wettem is currently unavailable.", ephemeral=True
            )

    # Attach the callback to the Select menu
    games_menu.callback = select_callback

    # Create a view and add the Select menu
    view = View(timeout=30)
    view.add_item(games_menu)

    # Add the credit button to the view
    credit_button = Button(
        label="Made by justwaitfor_me with python",
        style=discord.ButtonStyle.gray,
        disabled=True,
        emoji="<:python:1307381133075550208>",
        row=2,
    )
    view.add_item(credit_button)

    await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\n"
        f"Welcome to the casino! You've placed a bet of {bet}$. Choose a game to play and try your luck.\n"
        f"`Balance: {balance}$`\n`Bet: {bet}$`\n\n**Available Games:**\n",
        view=view,
        ephemeral=False,
    )


@bot.tree.command(name="daily", description="Claim your daily reward")
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def daily(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/daily command used", __file__)

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    user_data = check_user(interaction)
    last_daily = user_data.get("last_daily")
    current_date = datetime.now().date()

    if (
        last_daily != "Never"
        and datetime.fromisoformat(last_daily).date() == current_date
    ):
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            "You've already claimed your daily reward today. Come back tomorrow!",
            ephemeral=True,
        )
    else:
        counts(interaction.user.id, interaction.guild.id, "count_dayly")

        serverdata = get_serverdata()
        reward_amount = int(
            serverdata[str(interaction.guild.id)]["config"]["daily_reward"]
        )  # Example reward amoun

        add_balance(interaction.user.id, interaction, reward_amount)
        serverdata = get_serverdata()
        userdata = serverdata[str(interaction.guild.id)]["users"]
        userdata[str(interaction.user.id)]["last_daily"] = current_date.isoformat()

        serverdata[str(interaction.guild.id)]["users"] = userdata
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            f"You've claimed your daily reward of {reward_amount}$!\n"
            f"`New Balance: {str(int(user_data['balance'])+reward_amount)}$`",
            ephemeral=False,
        )


@bot.tree.command(name="info", description="Display user information")
@app_commands.describe(user="The user to display information for (optional)")
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):  # noqa: F811
    target_user = user or interaction.user
    log(
        interaction.user.id,
        interaction.user.name,
        f"/info command used for {target_user.name}",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    user_data = check_user(interaction)
    balance = user_data["balance"]

    last_daily = user_data.get("last_daily", "Never")
    if last_daily != "Never":
        last_daily = datetime.strptime(last_daily, "%Y-%m-%d").strftime("%A, %d %B %Y")

    inventory_raw = user_data.get("inventory", [])
    inventory = get_achievement(inventory_raw)

    embed = discord.Embed(
        title=f"User Info for {target_user.name}",
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(url=target_user.avatar.url)
    embed.add_field(name="Balance", value=f"{balance}$", inline=False)
    embed.add_field(name="Last Daily Claim", value=last_daily, inline=False)
    embed.add_field(
        name="Achievements",
        value=f"{' '.join([f'{emoji} `{name}`' for name, emoji in inventory]) if inventory_raw else 'Empty'}",
        inline=False,
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="balance", description="Display your current balance∞")
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def balance(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/balance command used", __file__)

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    user_data = check_user(interaction)
    balance = user_data["balance"]

    embed = discord.Embed(
        title="Your Balance",
        description=f"Your current balance is: **{balance}$**",
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="achievements", description="Display all possible achievements")
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def achievements(interaction: discord.Interaction):
    log(
        interaction.user.id,
        interaction.user.name,
        "/achievements command used",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    achievements_list = data.get("achievements", {})
    embed = discord.Embed(
        title="Achievements",
        description="Here are all the possible achievements you can earn:",
        color=discord.Color.greyple(),
    )
    for achievement in achievements_list:
        achievement_data = achievements_list[achievement]
        embed.add_field(
            name=f"{achievement_data['emoji']} {achievement_data['name']}",
            value=achievement_data["description"],
            inline=False,
        )
        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/phone-{random.randint(1, 5)}.png"
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="leaderboard", description="Display the top users by balance and achievements"
)
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def leaderboard(interaction: discord.Interaction):
    log(
        interaction.user.id,
        interaction.user.name,
        "/leaderboard command used",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    serverdata = get_serverdata()
    user_data = serverdata[str(interaction.guild.id)]["users"]
    sorted_users = sorted(
        user_data.items(), key=lambda x: x[1]["balance"], reverse=True
    )
    top_users = sorted_users[:10]

    embed = discord.Embed(
        title="Leaderboard",
        description=f"Top 10 users by balance and achievements\n**The Banks money is: *{serverdata[str(interaction.guild.id)]["bank"]}$* **",
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/phone-{random.randint(1, 5)}.png"
    )

    for index, (user_id, user_info) in enumerate(top_users, start=1):
        user = await bot.fetch_user(int(user_id))  # noqa: F811
        user_data = check_user(interaction)

        inventory_raw = user_data.get("inventory", [])
        inventory = get_achievement(inventory_raw)

        embed.add_field(
            name=f"{index}. {user.name}",
            value=f"Balance: **{user_info['balance']}$**\n Achievements: {' '.join([f'{emoji} `{name}`' for name, emoji in inventory]) if inventory_raw else 'Empty'}",
            inline=False,
        )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="send", description="Send money to another player")
@app_commands.describe(
    recipient="The user you want to send money to",
    amount="The amount of money you want to send",
)
@app_commands.check(
    lambda i: get_serverdata(i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def send_money(
    interaction: discord.Interaction,
    recipient: discord.Member,
    amount: int,
):
    log(
        interaction.user.id,
        interaction.user.name,
        f"/send command used to send {amount}$ to {recipient.name}",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    sender_data = check_user(interaction)
    check_user(interaction)

    if sender_data["balance"] < amount:
        await interaction.response.send_message(
            f"**{interaction.user.mention}**, you don't have enough money to send. Your current balance is {sender_data['balance']}$.",
            ephemeral=True,
        )
        return

    max_transaction = int(
        get_serverdata(interaction)[str(interaction.guild.id)]["config"][
            "max_transactions"
        ]
    )
    if amount > max_transaction:
        await interaction.response.send_message(
            f"**{interaction.user.mention}**, the maximum transaction amount is {max_transaction}$.",
            ephemeral=True,
        )
        return

    subtract_balance(interaction.user.id, interaction, amount)
    add_balance(recipient.id, interaction, amount)

    await interaction.response.send_message(
        f"**{interaction.user.mention}**, you have successfully sent {amount}$ to {recipient.mention}.\n"
        f"Your new balance: {sender_data['balance'] - amount}$",
        ephemeral=True,
    )

    await interaction.channel.send(
        f"{interaction.user.mention} has sent {amount}$ to {recipient.mention}!"
    )


# ADMIN COMMANDS BELOW
@bot.tree.command(name="add_balance", description="Add balance to a user")
@commands.has_permissions(administrator=True)
async def add_balance_command(
    interaction: discord.Interaction,
    user: discord.Member,  # noqa: F811
    amount: app_commands.Range[int, 1, 10000000000000],
):
    user_data = check_user(interaction)

    add_balance(user.id, interaction, amount)
    log(
        interaction.user.id,
        interaction.user.name,
        f"Added {amount}$ to {user.name}'s balance",
        __file__,
    )
    user_data = check_user(interaction)
    await interaction.response.send_message(
        f"Added {amount}$ to {user.mention}'s balance. New balance: {user_data['balance']}$",
        ephemeral=True,
    )


@bot.tree.command(name="subtract_balance", description="Subtract balance from a user")
@commands.has_permissions(administrator=True)
async def subtract_balance_command(
    interaction: discord.Interaction,
    user: discord.Member,  # noqa: F811
    amount: app_commands.Range[int, 1, 10000000000000],
):
    user_data = check_user(interaction)

    if user_data["balance"] < amount:
        subtract_balance(user.id, interaction, user_data["balance"])
    else:
        subtract_balance(user.id, interaction, amount)
    log(
        interaction.user.id,
        interaction.user.name,
        f"Subtracted {amount}$ from {user.name}'s balance",
        __file__,
    )
    user_data = check_user(interaction)
    await interaction.response.send_message(
        f"Successfully subtracted {amount}$ from {user.mention}'s balance. New balance: {user_data['balance']}$",
        ephemeral=True,
    )


@bot.tree.command(name="download_log", description="Download the current log file")
@commands.has_permissions(administrator=True)
async def download_log_command(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "Downloaded the log file", __file__)

    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/casino_{current_date}.log"
    with open(filename, "rb") as file:
        await interaction.response.send_message(
            "Here is the current log file:",
            file=discord.File(file, filename),
            ephemeral=True,
        )


@bot.tree.command(name="edit_config", description="Edit server configuration")
@commands.has_permissions(administrator=True)
async def edit_server_config(interaction: discord.Interaction):
    serverdata = get_serverdata()
    guild_id = str(interaction.guild.id)
    if guild_id not in serverdata:
        await interaction.response.send_message(
            "Server configuration not found.", ephemeral=True
        )
        return

    class ServerConfigModal(discord.ui.Modal, title="Edit Server Configuration"):
        def __init__(self):
            super().__init__()
            for key, value in serverdata[guild_id]["config"].items():
                if key != "banned_players":
                    self.add_item(
                        discord.ui.TextInput(
                            label=key,
                            default=value,
                            placeholder=f"Enter new value for {key}",
                        )
                    )

        async def on_submit(self, interaction: discord.Interaction):
            for item in self.children:
                serverdata[guild_id]["config"][item.label] = item.value

            with open("config/serverdata.json", "w") as file:
                json.dump(serverdata, file, indent=4)

            await interaction.response.send_message(
                "Configuration updated successfully.", ephemeral=True
            )

    await interaction.response.send_modal(ServerConfigModal())


@bot.tree.command(name="ban_player", description="Toggle ban status for a player")
@commands.has_permissions(administrator=True)
@app_commands.describe(player="Select the player to toggle ban status")
async def ban_player(interaction, player: discord.Member):
    serverdata = get_serverdata()
    guild_id = str(interaction.guild.id)
    if guild_id not in serverdata:
        await interaction.send("Server configuration not found.", ephemeral=True)
        return

    if "banned_players" not in serverdata[guild_id]["config"]:
        serverdata[guild_id]["config"]["banned_players"] = []

    banned_players = serverdata[guild_id]["config"]["banned_players"]
    if player.id in banned_players:
        banned_players.remove(player.id)
        await interaction.response.send_message(
            f"{player.mention} has been unbanned from using the bot.", ephemeral=True
        )
    else:
        banned_players.append(player.id)
        await interaction.response.send_message(
            f"{player.mention} has been banned from using the bot.", ephemeral=True
        )

    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)


@bot.command()
@commands.has_permissions(administrator=True)
async def release_notes(ctx, send_here: bool = False):
    with open(f"docs/{get_data()['version']}.txt", "r") as file:
        notes = file.read()

    release_message = f"** {ctx.guild.default_role} Release Notes:**\n{notes}"

    if send_here:
        # Send only to the current channel
        await ctx.send(release_message)
        return

    # Send to all guilds' system channel or the first available text channel
    for guild in bot.guilds:
        target_channel = guild.system_channel or next(
            (
                channel
                for channel in guild.text_channels
                if channel.permissions_for(guild.me).send_messages
            ),
            None,
        )
        if target_channel:
            try:
                await target_channel.send(release_message)
            except Exception:
                pass


@bot.command()
@commands.has_permissions(administrator=True)
async def brotcast(ctx, *, message: str):
    broadcast_message = f"** {ctx.guild.default_role} Broadcast:**\n{message}"

    for guild in bot.guilds:
        # Prefer system channel or fallback to the first available text channel
        target_channel = guild.system_channel or next(
            (
                channel
                for channel in guild.text_channels
                if channel.permissions_for(guild.me).send_messages
            ),
            None,
        )
        if target_channel:
            try:
                await target_channel.send(broadcast_message)
            except Exception:
                pass


@bot.command()
async def version(ctx):
    await ctx.send(f"Version: {get_data()['version']}")


@bot.command()
@commands.has_permissions(administrator=True)

async def toggle_dev_mode(ctx):
    serverdata = get_serverdata()
    guild_id = str(ctx.guild.id)
    if guild_id not in serverdata:
        await ctx.send("Server configuration not found.", ephemeral=True)
        return

    if "developer_mode" not in serverdata:
        serverdata["developer_mode"] = False

    serverdata["developer_mode"] = not serverdata["developer_mode"]
    with open("config/serverdata.json", "w") as file:
        json.dump(serverdata, file, indent=4)

    if serverdata["developer_mode"]:
        await ctx.send("Development mode enabled.", ephemeral=True)
    else:
        await ctx.send("Development mode disabled.", ephemeral=True)


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("yoo"):
        await message.channel.send(message.author.mention + ", you're welcome!")

    if "jackpot" in message.content:
        await message.channel.send("💰 Jackpot! You're on a winning streak! 💰")

    if "lucky" in message.content:
        await message.channel.send(
            "🍀 Feeling lucky today? Try your luck at the casino! 🍀"
        )

    if "slotmachine" in message.content:
        await message.channel.send("🎰 Welcome to the Slot Machine! 🎰")

    if "casino" in message.content:
        await message.channel.send(
            "🎲 Welcome to the Casino! Place your bets and have fun! 🎲"
        )

    if "gamble" in message.content:
        await message.channel.send(
            "🎲 Ready to gamble? Let's see if fortune favors you! 🎲"
        )

    if "lakers" in message.content.lower():
        await message.channel.send("🐢 Go Lakers!")

    if "lebron" in message.content.lower():
        await message.channel.send("🎩 LeBron James!")

    await bot.process_commands(message)


bot.run(os.environ["TOKEN"])# log_handler=handler)
