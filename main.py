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
            name=f"{casino_game['name']} | /help for commands",
            state=casino_game['fun_fact'],
        )
    )


@bot.tree.command(name="help", description="Lists all available commands")
@app_commands.check(
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
    == "True"
)
async def list(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/help command used", __file__)
    commands_list = get_data()['commands']

    embed = discord.Embed(
        title="Available Commands",
        description="\n".join([f"{cmd}: {desc}" for cmd, desc in commands_list]),
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png?raw=true",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(3, 4)}.png?raw=true"
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="play", description="Play the casino games")
@app_commands.describe(bet="The amount you want to bet")
@app_commands.check(
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def play(interaction: discord.Interaction, bet: int):
    log(
        interaction.user.id,
        interaction.user.name,
        f"/play command used with bet: {bet}",
        __file__,
    )
    user_data = check_user(interaction.user.id, interaction.guild.id)
    balance = user_data["balance"]

    max_bet = int(
        get_serverdata(str(interaction.guild.id))[str(interaction.guild.id)]["config"][
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
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
    == "True"
)
async def daily(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/daily command used", __file__)
    user_data = check_user(interaction.user.id, interaction.guild.id)
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
            serverdata[str(interaction.guild.id)]['config']['daily_reward']
        )  # Example reward amoun

        add_balance(interaction.user.id, interaction.guild.id, reward_amount)
        serverdata = get_serverdata()
        userdata = serverdata[str(interaction.guild.id)]['users']
        userdata[str(interaction.user.id)]['last_daily'] = current_date.isoformat()

        serverdata[str(interaction.guild.id)]['users'] = userdata
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
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
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
    user_data = check_user(target_user.id, interaction.guild_id)
    balance = user_data['balance']

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
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png?raw=true",
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
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
    == "True"
)
async def balance(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/balance command used", __file__)
    user_data = check_user(interaction.user.id, interaction.guild_id)
    balance = user_data['balance']

    embed = discord.Embed(
        title="Your Balance",
        description=f"Your current balance is: **{balance}$**",
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png?raw=true",
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="achievements", description="Display all possible achievements")
@app_commands.check(
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
    == "True"
)
async def achievements(interaction: discord.Interaction):
    log(
        interaction.user.id,
        interaction.user.name,
        "/achievements command used",
        __file__,
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
            value=achievement_data['description'],
            inline=False,
        )
        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/phone-{random.randint(1, 5)}.png?raw=true"
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="leaderboard", description="Display the top users by balance and achievements"
)
@app_commands.check(
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
    == "True"
)
async def leaderboard(interaction: discord.Interaction):
    log(
        interaction.user.id,
        interaction.user.name,
        "/leaderboard command used",
        __file__,
    )
    serverdata = get_serverdata()
    user_data = serverdata[str(interaction.guild.id)]['users']
    sorted_users = sorted(
        user_data.items(), key=lambda x: x[1]['balance'], reverse=True
    )
    top_users = sorted_users[:10]

    embed = discord.Embed(
        title="Leaderboard",
        description="Top 10 users by balance and achievements",
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png?raw=true",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/phone-{random.randint(1, 5)}.png?raw=true"
    )

    for index, (user_id, user_info) in enumerate(top_users, start=1):
        user = await bot.fetch_user(int(user_id))  # noqa: F811
        user_data = check_user(user.id, interaction.guild.id)

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
    lambda i: get_serverdata(str(i.guild.id))[str(i.guild.id)]['config']['bot_enabled']
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
    sender_data = check_user(interaction.user.id, interaction.guild_id)
    check_user(recipient.id, interaction.guild_id)

    if sender_data['balance'] < amount:
        await interaction.response.send_message(
            f"**{interaction.user.mention}**, you don't have enough money to send. Your current balance is {sender_data['balance']}$.",
            ephemeral=True,
        )
        return

    max_transaction = int(
        get_serverdata(str(interaction.guild.id))[str(interaction.guild.id)]['config'][
            "max_transactions"
        ]
    )
    if amount > max_transaction:
        await interaction.response.send_message(
            f"**{interaction.user.mention}**, the maximum transaction amount is {max_transaction}$.",
            ephemeral=True,
        )
        return

    subtract_balance(interaction.user.id, interaction.guild_id, amount)
    add_balance(recipient.id, interaction.guild_id, amount)

    await interaction.response.send_message(
        f"**{interaction.user.mention}**, you have successfully sent {amount}$ to {recipient.mention}.\n"
        f"Your new balance: {sender_data['balance'] - amount}$",
        ephemeral=True,
    )

    await interaction.channel.send(
        f"{interaction.user.mention} has sent {amount}$ to {recipient.mention}!"
    )

    subtract_balance(interaction.user.id, interaction.guild_id, amount)
    add_balance(recipient.id, interaction.guild_id, amount)

    await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\n"
        f"You have successfully sent {amount}$ to {recipient.mention}.\n"
        f"`Your New Balance: {sender_data['balance'] - amount}$`",
        ephemeral=True,
    )

    await interaction.channel.send(
        f"{interaction.user.mention} has sent {amount}$ to {recipient.mention}!"
    )


@bot.tree.command(name="add_balance", description="Add balance to a user")
@commands.has_permissions(administrator=True)
async def add_balance_command(
    interaction: discord.Interaction,
    user: discord.Member,  # noqa: F811
    amount: app_commands.Range[int, 1, 10000000000000],
):
    user_data = check_user(user.id, interaction.guild_id)

    add_balance(user.id, interaction.guild_id, amount)
    log(
        interaction.user.id,
        interaction.user.name,
        f"Added {amount}$ to {user.name}'s balance",
        __file__,
    )
    user_data = check_user(user.id, interaction.guild_id)
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
    user_data = check_user(user.id, interaction.guild_id)

    if user_data['balance'] < amount:
        subtract_balance(user.id, interaction.guild_id, user_data['balance'])
    else:
        subtract_balance(user.id, interaction.guild_id, amount)
    log(
        interaction.user.id,
        interaction.user.name,
        f"Subtracted {amount}$ from {user.name}'s balance",
        __file__,
    )
    user_data = check_user(user.id, interaction.guild_id)
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
            for key, value in serverdata[guild_id]['config'].items():
                self.add_item(
                    discord.ui.TextInput(
                        label=key,
                        default=value,
                        placeholder=f"Enter new value for {key}",
                    )
                )

        async def on_submit(self, interaction: discord.Interaction):
            for item in self.children:
                serverdata[guild_id]['config'][item.label] = item.value

            with open("config/serverdata.json", "w") as file:
                json.dump(serverdata, file, indent=4)

            await interaction.response.send_message(
                "Configuration updated successfully.", ephemeral=True
            )

    await interaction.response.send_modal(ServerConfigModal())


@bot.command()
@commands.has_permissions(administrator=True)
async def release_notes(ctx):
    with open(f"docs/{get_data()['version']}.txt", "r") as file:
        notes = file.read()
    await ctx.send(f"**{ctx.guild.default_role} Release Notes:**\n{notes}")

@bot.command()
async def version(ctx):
    await ctx.send(f"Version: {get_data()['version']}")

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

    if message.content.startswith("yoo"):
        await message.channel.send(message.author.mention + ", you're welcome!")

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

    await bot.process_commands(message)


bot.run(os.environ['TOKEN'])#, log_handler=handler)
