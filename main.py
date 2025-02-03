import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput

from datetime import datetime
import os
import random
import json
import dotenv
import logging
import asyncio
import uuid

# Check if serverdata.json is there, if not make it
if not os.path.exists("config/serverdata.json"):
    with open("config/serverdata.json", "w") as file:
        json.dump({"developer_mode": False}, file)

from scripts.poker_cog import PokerCog

from scripts.functions import (
    get_data,
    check_user,
    user,
    counts,
    formatt_int,
    get_serverdata,
    add_balance,
    subtract_balance,
    multiply_balance,
    log,
    check_banned,
    validate_bet,
)

from scripts.engine import (
    blackjack_callback,
    guess_the_number_callback,
    double_or_nothing_callback,
    roulette_callback,
    slot_machine_callback,
    horce_racing_callback,
)

from scripts.achievements import get_achievement

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable member intents
intents.presences = True  # Enable presence intents
intents.message_content = True  # Enable message content intent

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
            name="/help | /play",
            state="made by justwaitfor_me | assets by murmel265",
        )
    )

    await bot.add_cog(PokerCog(bot))
    print(f"Available cogs: {bot.cogs}")  # Check if PokerCog is in the list


@bot.tree.command(name="help", description="Lists all available commands")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def help(interaction: discord.Interaction):
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
        name=get_data()["titel"],
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(3, 4)}.png"
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="dashboard", description="Navigate to the server dashboard")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def dashboard(interaction: discord.Interaction):
    # LIVE CODE
    button = discord.ui.Button(
        style=discord.ButtonStyle.success,
        label="Open Dashboard",
        url=get_data()["dashboard"],
    )
    view = discord.ui.View()
    view.add_item(button)

    return await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\nSadly your Server Dashboard is not ready by now!",
        view=view,
        ephemeral=True,
    )

    #CURRENT BETA
    log(
        interaction.user.id,
        interaction.user.name,
        "/dashboard command used",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    dashboard_url = f"{get_data()["dashboard"]}{interaction.guild.id}"

    embed = discord.Embed(
        title="Server Dashboard",
        description=f"Click the button below to navigate to the server dashboard:\n[Casino Dashboard]({dashboard_url})",
        color=discord.Color.blue(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name=get_data()["titel"],
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(3, 4)}.png"
    )

    button = discord.ui.Button(
        style=discord.ButtonStyle.success,
        label="Open Dashboard",
        url=dashboard_url,
    )
    view = discord.ui.View()
    view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


@bot.tree.command(
    name="my-dashboard", description="Navigate to your personal dashboard"
)
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def user_dashboard(interaction: discord.Interaction):
    # LIVE CODE
    button = discord.ui.Button(
        style=discord.ButtonStyle.success,
        label="Open Dashboard",
        url=get_data()["dashboard"],
    )
    view = discord.ui.View()
    view.add_item(button)

    return await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\nSadly your Personal Dashboard is not ready by now!",
        view=view,
        ephemeral=True,
    )

    # CURRENT BETA
    log(
        interaction.user.id,
        interaction.user.name,
        "/dashboard command used",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    dashboard_url = (
        f"{get_data()["dashboard"]}{interaction.guild.id}/{interaction.user.id}"
    )

    embed = discord.Embed(
        title="My Dashboard",
        description=f"Click the button below to navigate to your dashboard:\n[Casino Dashboard]({dashboard_url})",
        color=discord.Color.blue(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name=get_data()["titel"],
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(3, 4)}.png"
    )

    button = discord.ui.Button(
        style=discord.ButtonStyle.success,
        label="Open Dashboard",
        url=dashboard_url,
    )
    view = discord.ui.View()
    view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


@bot.tree.command(name="play", description="Play the casino games")
@app_commands.describe(bet="The amount you want to bet")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def play(interaction: discord.Interaction, bet: int):
    log(
        interaction.user.id,
        interaction.user.name,
        f"/play command used with bet: {bet}",
        __file__,
    )

    is_valid, error_message = validate_bet(interaction, bet)

    if not is_valid:
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n{error_message}", ephemeral=True
        )

    user_data = check_user(interaction)
    balance = user_data["balance"]

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
                description="Bet on a Horse",
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
            await horce_racing_callback(interaction, bet)

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
        f"Welcome to the casino! You've placed a bet of {formatt_int(bet)}$. Choose a game to play and try your luck.\n"
        f"`Balance: {formatt_int(balance)}$`\n`Bet: {formatt_int(bet)}$`\n\n**Available Games:**\n",
        view=view,
        ephemeral=False,
    )


# The command for starting a poker game
@bot.tree.command(name="poker", description="Start a poker game (beta)")
@app_commands.describe(bet="The amount you want to bet")
async def poker(interaction: discord.Interaction, bet: int):
    # LIVE CODE
    return await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\nSadly our Poker Game is not ready by now!", ephemeral=True
    )

    # CURRENT BETA
    # Validate the bet
    is_valid, error_message = validate_bet(interaction, bet)

    if not is_valid:
        return await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n{error_message}", ephemeral=True
        )

    log(
        interaction.user.id,
        interaction.user.name,
        f"Started a Poker game with bet: {bet}",
        __file__,
    )

    # Get the rooms from the PokerCog
    poker_cog = bot.get_cog("PokerCog")
    if not poker_cog:
        return await interaction.response.send_message(
            "Poker game logic is still booting up. Please try again in one minute",
            ephemeral=True,
        )

    rooms = poker_cog.rooms

    # Create a dropdown for available rooms
    room_options = [
        discord.SelectOption(label=f"{room_id}", value=room_id)
        for room_id in rooms
        if len(rooms[room_id]["players"]) < 4
    ]

    # No available rooms, offer to create a new one
    view = View()
    create_room_button = Button(
        label="Create a New Room", style=discord.ButtonStyle.primary
    )
    create_private_button = Button(
        label="Create a Private Room", style=discord.ButtonStyle.success
    )

    async def create_room_callback(interaction):
        # Create a new game without a password
        room_id = f"game-{interaction.user.name}"
        rooms[room_id] = {
            "players": [interaction.user],
            "pot": bet,
            "deck": [f"{rank}{suit}" for rank in "23456789TJQKA" for suit in "♠♥♦♣"],
            "community_cards": [],
            "player_hands": {},
        }
        random.shuffle(rooms[room_id]["deck"])
        subtract_balance(interaction.user.id, interaction, bet)
        await interaction.response.edit_message(
            content=f"**{interaction.user.mention}** created a new poker game.",
            view=None,
        )
        await poker_cog.start_game(interaction, room_id, bet)

    async def create_private_room_callback(interaction):
        # Modal to input a password
        class GuessModal(Modal):
            """Modal for users to input their guess."""

            pass_input = TextInput(
                label="Password",
                required=True,
            )

            async def on_submit(self, interaction):
                password = self.pass_input.value

                room_id = f"room-{password}"

                if room_id in rooms:
                    await interaction.followup.send(
                        "This room already exists!", ephemeral=True
                    )
                else:
                    rooms[room_id] = {
                        "players": [interaction.user],
                        "pot": bet,
                        "deck": [
                            f"{rank}{suit}" for rank in "23456789TJQKA" for suit in "♠♥♦♣"
                        ],
                        "community_cards": [],
                        "player_hands": {},
                    }
                    random.shuffle(rooms[room_id]["deck"])
                    subtract_balance(interaction.user.id, interaction, bet)
                    await interaction.response.edit_message(
                        content=f"**{interaction.user.mention}** created a new private poker room.",
                        view=None,
                    )
                    await poker_cog.start_game(interaction, room_id, bet)

        await interaction.response.send_modal(
            GuessModal(title="Enter Password for Private Room")
        )

    create_room_button.callback = create_room_callback
    create_private_button.callback = create_private_room_callback

    view.add_item(create_room_button)
    view.add_item(create_private_button)

    async def select_callback(interaction: discord.Interaction):
        # Check if the user interacting with the menu is the same as the one who invoked the command
        if not user(interaction):
            await interaction.response.send_message(
                "You can't interact with this menu.", ephemeral=True
            )
            return

        room_id = select.values[0]
        room = rooms[room_id]

        if interaction.user in room["players"]:
            return await interaction.response.send_message(
                "You are already in this room.", ephemeral=True
            )

        room["players"].append(interaction.user)
        room["pot"] += bet
        subtract_balance(interaction.user.id, interaction, bet)
        await interaction.response.send_message(
            content=f"**{interaction.user.mention}** joined the poker room {room_id}.",
        )
        await poker_cog.start_game(interaction, room_id, bet)

    if room_options:
        # Dropdown to select an existing room
        select = Select(
            placeholder="Choose an available room",
            min_values=1,
            max_values=1,
            options=room_options,
        )

        select.callback = select_callback
        view.add_item(select)

        await interaction.response.send_message("Choose a room to join:", view=view)
    else:
        await interaction.response.send_message(
            "No available rooms. Would you like to create a new room?",
            view=view,
        )


@bot.tree.command(name="luckywheel", description="Spin the wheel and try your luck")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def luckywheel(interaction: discord.Interaction):
    log(
        interaction.user.id, interaction.user.name, "/luckywheel command used", __file__
    )
    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    user_data = check_user(interaction)
    last_wheel = user_data.get("last_wheel")
    current_date = datetime.now().date()

    if (
        last_wheel != "Never"
        and datetime.fromisoformat(last_wheel).date() == current_date
    ):
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            "You've already spinned the wheel today. Come back tomorrow!",
            ephemeral=True,
        )
    else:
        # Define the sections of the wheel
        lucky_options = get_data()["lucky_options"]

        # Extract options and probabilities
        options = [item[0] for item in lucky_options]  # Descriptions
        probabilities = [item[1] for item in lucky_options]  # Probabilities

        # Simulate the spinning animation
        embed = discord.Embed(
            title="🎡 Spinning the Lucky Wheel!",
            description="Get ready to see where it lands!",
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=get_data()["titel"],
            icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
        )

        await interaction.response.send_message(
            embed=embed, content=interaction.user.mention
        )
        message = (
            await interaction.original_response()
        )  # Get the sent message for editing

        for i in range(15):  # Spin 15 times for the animation
            current_option = random.choices(options, weights=probabilities, k=1)[0]
            embed.description = f"**Spinning...**\n{current_option[1]}"
            await message.edit(embed=embed, content=interaction.user.mention)
            await asyncio.sleep(0.3)  # Delay between spins

        # Final result
        final_result = random.choices(options, weights=probabilities, k=1)[0]

        multiply_balance(interaction.user.id, interaction, final_result[0])
        serverdata = get_serverdata()
        userdata = serverdata[str(interaction.guild.id)]["users"]
        userdata[str(interaction.user.id)]["last_wheel"] = current_date.isoformat()

        serverdata[str(interaction.guild.id)]["users"] = userdata
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

        embed.description = f"🎉 **Congratulations! You won:** {final_result[1]} 🎉"
        embed.color = discord.Color.green()
        await message.edit(embed=embed, content=interaction.user.mention)


@bot.tree.command(name="daily", description="Claim your daily reward")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
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
            f"You've claimed your daily reward of {formatt_int(reward_amount)}$!\n"
            f"`New Balance: {formatt_int(int(user_data['balance'])+reward_amount)}$`",
            ephemeral=False,
        )


@bot.tree.command(
    name="prestige", description="Reset your progress to achieve Prestige"
)
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
    == "True"
)
async def prestige(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "/prestige command used", __file__)

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    user_data = check_user(interaction)
    balance = user_data["balance"]

    if user_data["max_bet"] is None:
        max_bet = int(
            get_serverdata(interaction)[str(interaction.guild.id)]["config"]["max_bet"]
        )
    else:
        max_bet = int(user_data["max_bet"])

    if balance < max_bet:
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            f"You need at least {formatt_int(max_bet)}$ to achieve Prestige.",
            ephemeral=True,
        )
        return

    # Warning message with a button
    embed = discord.Embed(
        title="Are you sure you want to Prestige?",
        description=(
            f"**Warning:** This will reset your balance to **1,000$**, and you will lose your current balance of **{formatt_int(balance)}$**. "
            f"In return, your maximum bet will increase to **{formatt_int(int(str(balance)[0]) * (10 ** (len(str(balance)) - 1)))}$**."
        ),
        color=discord.Color.red(),
    )

    confirm_button = Button(label="Confirm Prestige", style=discord.ButtonStyle.green)
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def confirm_callback(button_interaction: discord.Interaction):
        if button_interaction.user.id != interaction.user.id:
            await button_interaction.response.send_message(
                "You cannot confirm this action for another user.", ephemeral=True
            )
            return

        # Prestige logic
        new_max_bet = int(str(balance)[0]) * (10 ** (len(str(balance)) - 1))

        subtract_balance(interaction.user.id, interaction, balance)
        add_balance(interaction.user.id, interaction, 1000)

        # Update the user's max_bet
        serverdata = get_serverdata()
        serverdata[str(interaction.guild.id)]["users"][str(interaction.user.id)][
            "max_bet"
        ] = new_max_bet
        serverdata[str(interaction.guild.id)]["users"][str(interaction.user.id)][
            "prestige_level"
        ] += 1
        with open("config/serverdata.json", "w") as file:
            json.dump(serverdata, file, indent=4)

        await button_interaction.response.edit_message(
            content=(
                f"**Congratulations {interaction.user.mention}!**\n"
                f"You have achieved Prestige! Your new balance is **1,000$**.\n"
                f"Your new maximum bet is **{formatt_int(new_max_bet)}$**."
            ),
            embed=None,
            view=None,
        )

    async def cancel_callback(button_interaction: discord.Interaction):
        if button_interaction.user.id != interaction.user.id:
            await button_interaction.response.send_message(
                "You cannot cancel this action for another user.", ephemeral=True
            )
            return

        await button_interaction.response.edit_message(
            content="Prestige canceled. No changes were made.",
            embed=None,
            view=None,
        )

    # Attach callbacks
    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    # Create a view for buttons
    view = View()
    view.add_item(confirm_button)
    view.add_item(cancel_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@bot.tree.command(name="info", description="Display user information")
@app_commands.describe(user="The user to display information for (optional)")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
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

    user_data = check_user(interaction, target=target_user.id)
    balance = user_data["balance"]
    prestige_level = user_data["prestige_level"]

    last_daily = user_data.get("last_daily", "Never")
    if last_daily != "Never":
        last_daily = datetime.strptime(last_daily, "%Y-%m-%d").strftime("%A, %d %B %Y")

    inventory_raw = user_data.get("inventory", [])
    inventory = get_achievement(inventory_raw)

    inventory_len = len(inventory)
    achievements_len = len(get_data()["achievements"])

    embed = discord.Embed(
        title=f"User Info for {target_user.name}",
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name=get_data()["titel"],
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(url=target_user.avatar.url)
    embed.add_field(name="Balance", value=f"{formatt_int(balance)}$", inline=False)
    embed.add_field(
        name="Prestige Level:", value=f"{formatt_int(prestige_level)}x", inline=False
    )
    embed.add_field(name="Last Daily Claim", value=last_daily, inline=False)
    embed.add_field(
        name=f"Achievements ({inventory_len}/{achievements_len})",
        value=f"{' '.join([f'{emoji} `{name}`' for name, emoji in inventory]) if inventory_raw else 'Empty'}",
        inline=False,
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="balance", description="Display your current balance∞")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
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
        description=f"Your current balance is: **{formatt_int(balance)}$**",
        color=discord.Color.greyple(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name=get_data()["titel"],
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="achievements", description="Display all possible achievements")
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
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
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
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
    top_users = sorted_users[:7]

    embed = discord.Embed(
        title="Leaderboard",
        description=f"Top 10 users by balance and achievements\n**The Banks money is: *{formatt_int(serverdata[str(interaction.guild.id)]['bank'])}$* **",
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name=get_data()["titel"],
        icon_url=f"{str(os.environ['IMAGES'])}/kasino-{random.randint(1, 3)}.png",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/phone-{random.randint(1, 5)}.png"
    )

    for index, (user_id, user_info) in enumerate(top_users, start=1):
        user = await bot.fetch_user(int(user_id))  # noqa: F811
        user_data = check_user(interaction, target=user.id)

        inventory_raw = user_data.get("inventory", [])
        inventory = get_achievement(inventory_raw)

        inventory_len = len(inventory)
        achievements_len = len(get_data()["achievements"])

        embed.add_field(
            name=f"{index}. {user.name}",
            value=f"Balance: **{formatt_int(user_info['balance'])}$**\n **Achievements ({inventory_len}/{achievements_len}):**\n {' '.join([f'{emoji} `{name}`' for name, emoji in inventory]) if inventory_raw else 'Empty'}",
            inline=False,
        )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="send", description="Send money to another player")
@app_commands.describe(
    recipient="The user you want to send money to",
    amount="The amount of money you want to send",
)
@app_commands.check(
    lambda i: get_serverdata(interaction=i)[str(i.guild.id)]["config"]["bot_enabled"]
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
        f"/send command used to send {formatt_int(amount)}$ to {recipient.name}",
        __file__,
    )

    if check_banned(interaction):
        return await interaction.response.send_message(
            content="You are banned from using this bot. (Or the bot is currently in Developer Mode)",
            ephemeral=True,
        )

    sender_data = check_user(interaction)

    if sender_data["balance"] < amount:
        await interaction.response.send_message(
            f"**{interaction.user.mention}**, you don't have enough money to send. Your current balance is {formatt_int(sender_data['balance'])}$.",
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
            f"**{interaction.user.mention}**, the maximum transaction amount is {formatt_int(max_transaction)}$.",
            ephemeral=True,
        )
        return

    subtract_balance(interaction.user.id, interaction, amount)
    add_balance(recipient.id, interaction, amount)

    await interaction.response.send_message(
        f"**{interaction.user.mention}**, you have successfully sent {formatt_int(amount)}$ to {recipient.mention}.\n"
        f"Your new balance: {formatt_int(sender_data['balance'] - amount)}$",
        ephemeral=True,
    )

    await interaction.channel.send(
        f"{interaction.user.mention} has sent {formatt_int(amount)}$ to {recipient.mention}!"
    )


# ADMIN COMMANDS BELOW
@bot.tree.command(name="add_balance", description="Add balance to a user")
@commands.has_permissions(administrator=True)
async def add_balance_command(
    interaction: discord.Interaction,
    user: discord.Member,  # noqa: F811
    amount: int,
):
    user_data = check_user(interaction, target=user.id)

    add_balance(user.id, interaction, amount)
    log(
        interaction.user.id,
        interaction.user.name,
        f"Added {formatt_int(amount)}$ to {user.name}'s balance",
        __file__,
    )

    await interaction.response.send_message(
        f"Added {formatt_int(amount)}$ to {user.mention}'s balance. New balance: {formatt_int(user_data['balance'] + amount)}$",
        ephemeral=True,
    )


@bot.tree.command(name="subtract_balance", description="Subtract balance from a user")
@commands.has_permissions(administrator=True)
async def subtract_balance_command(
    interaction: discord.Interaction,
    user: discord.Member,  # noqa: F811
    amount: int,
):
    user_data = check_user(interaction, target=user.id)

    if user_data["balance"] < amount:
        subtract_balance(user.id, interaction, user_data["balance"])
    else:
        subtract_balance(user.id, interaction, amount)
    log(
        interaction.user.id,
        interaction.user.name,
        f"Subtracted {formatt_int(amount)}$ from {user.name}'s balance",
        __file__,
    )

    await interaction.response.send_message(
        f"Successfully subtracted {formatt_int(amount)}$ from {user.mention}'s balance. New balance: {formatt_int(user_data['balance'] + amount)}$",
        ephemeral=True,
    )


@bot.tree.command(name="download_log", description="Download the current log file")
@commands.has_permissions(administrator=True)
async def download_log_command(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "Downloaded the log file", __file__)

    # Check if the user is a developer
    if interaction.user.id not in get_data()["developer"]:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/casino_{current_date}.log"
    with open(filename, "rb") as file:
        await interaction.response.send_message(
            "Here is the current log file:",
            file=discord.File(file, filename),
            ephemeral=True,
        )


@bot.tree.command(
    name="download_serverdata", description="Download the current serverdata file"
)
@commands.has_permissions(administrator=True)
async def download_serverdata_command(interaction: discord.Interaction):
    log(
        interaction.user.id, interaction.user.name, "Downloaded the data file", __file__
    )

    # Check if the user is a developer
    if interaction.user.id not in get_data()["developer"]:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return

    filename = "config/serverdata.json"
    with open(filename, "rb") as file:
        await interaction.response.send_message(
            "Here is the current data file:",
            file=discord.File(file, filename),
            ephemeral=True,
        )


@bot.tree.command(
    name="list_servers", description="List all servers in the server configuration"
)
@commands.has_permissions(administrator=True)
async def list_servers(interaction: discord.Interaction):
    log(interaction.user.id, interaction.user.name, "Listed serverdata", __file__)

    # Replace `get_serverdata` with your actual function to retrieve server data.
    serverdata = get_serverdata()

    if not serverdata:
        await interaction.response.send_message(
            "Server configuration not found.", ephemeral=True
        )
        return

    guilds = list(serverdata.keys())

    class ServerSelection(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(
                    label=guild, description=f"Configuration for {guild}"
                )
                for guild in guilds
            ]
            super().__init__(
                placeholder="Select a server",
                options=options,
            )

        async def callback(self, interaction: discord.Interaction):
            selected_guild = self.values[0]
            server_config = serverdata[selected_guild]

            server_name = serverdata[selected_guild]["info"]["name"]
            # Check if the user is an administrator in the selected guild
            guild = discord.utils.get(bot.guilds, name=server_name)
            if guild is None:
                await interaction.response.send_message(
                    "Selected server not found in the bot's guilds.", ephemeral=True
                )
                return

            member = guild.get_member(interaction.user.id)
            if member is None or not member.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You must be an admin on the selected server to use this command.",
                    ephemeral=True,
                )
                return

            md_content = f"# Server Data for {server_name}\n\n"
            for key, value in server_config.items():
                if isinstance(value, dict):
                    md_content += f"## {key}\n\n"
                    for subkey, subvalue in value.items():
                        md_content += f"### {subkey}: {str(subvalue).replace("{", "* ").replace("}", "\n").replace("[", "\n").replace("]", "").replace(",", "")}\n\n"
                    md_content += "\n\n"
                else:
                    md_content += f"### {key}: {value}\n"

            # Save the markdown content to a file
            hash_string = uuid.uuid4().hex
            md_filename = f"temp/{hash_string}.temp.md"
            with open(md_filename, "w") as f:
                f.write(md_content)

            # Send the markdown file and the serverdata.json file
            with open(md_filename, "rb") as md_file:
                await interaction.response.send_message(
                    content=f"Here is the configuration for {selected_guild}:",
                    files=[discord.File(md_file, md_filename)],
                    ephemeral=True,
                )

    class ServerSelectionView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(ServerSelection())

    view = ServerSelectionView()
    await interaction.response.send_message(
        "Select a server:", view=view, ephemeral=True
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
async def info(ctx):
    # Get the bot's latency (ping)
    latency = round(bot.latency * 1000)  # Convert from seconds to milliseconds

    # Count the number of servers and users
    total_servers = len(bot.guilds)
    total_users = sum(guild.member_count for guild in bot.guilds)

    # Format and send the response
    await ctx.send(
        f"**Bot Information:**\n"
        f"Bot Name: {bot.user.name}\n"
        f"Bot ID: {bot.user.id}\n"
        f"Version: {get_data()['version']}\n"
        f"Latency: {latency}ms\n"
        f"Servers: {total_servers}\n"
        f"Total Users: {total_users}\n"
        f"Developed by: justwaitfor_me\n"
    )


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif get_serverdata()["developer_mode"]:
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


bot.run(os.environ["TOKEN"] , log_handler=handler)
