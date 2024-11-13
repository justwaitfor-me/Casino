import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

from datetime import datetime
import os
import random
import json
import dotenv

from scripts.functions import get_data, check_user, user, counts, get_userdata, add_balance
from scripts.engine import blackjack_callback, guess_the_number_callback, double_or_nothing_callback, roulette_callback

intents = discord.Intents.default()
intents.message_content = True

data = get_data()
dotenv.load_dotenv(".env")

bot = commands.Bot(command_prefix="!", intents=intents)
casino_game = random.choice(data.get("casino_games", {}))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{casino_game["name"]} | /help for commands",
            state=casino_game["fun_fact"],
        )
    )


@bot.tree.command(name="help", description="Lists all available commands")
async def list(interaction: discord.Interaction):
    commands_list = [
        ("`/help`", "Lists all available commands"),
        ("`/play`", "Play the casino games"),
        ("`/daily`", "Claim your daily reward"),
        ("`/info`", "Display user information"),
        ("`/achievements`", "Display all possible achievements"),
    ]

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
async def play(
    interaction: discord.Interaction, bet: app_commands.Range[int, 1, 10000]
):
    user_data = check_user(interaction.user.id)
    balance = user_data["balance"]

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
    game1_button = Button(
        label="Blackjack",
        style=discord.ButtonStyle.primary,
        disabled=True,
        emoji="<:casinochip1:1304579248908009562>",
        row=1,
    )
    game2_button = Button(
        label="Double or Nothing",
        style=discord.ButtonStyle.danger,
        disabled=False,
        emoji="<:casinochip2:1304579236496932904>",
        row=2,
    )
    game3_button = Button(
        label="Roulett",
        style=discord.ButtonStyle.success,
        disabled=True,
        emoji="<:casinochip3:1304579224597954612>",
        row=3,
    )
    game4_button = Button(
        label="Guess the Number",
        style=discord.ButtonStyle.grey,
        disabled=False,
        emoji="<:casinochip4:1304579213189189693>",
        row=4,
    )

    game1_button.callback = lambda i: blackjack_callback(i, bet) if user(i) else None
    game2_button.callback = lambda i: double_or_nothing_callback(i, bet) if user(i) else None
    game3_button.callback = lambda i: roulette_callback(i, bet) if user(i) else None
    game4_button.callback = lambda i: guess_the_number_callback(i, bet) if user(i) else None

    view = View(timeout=30)
    view.add_item(game1_button)
    view.add_item(game2_button)
    view.add_item(game3_button)
    view.add_item(game4_button)

    await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\n"
        f"Welcome to the casino! You've placed a bet of {bet}$. Choose a game to play and try your luck.\n"
        f"`Balance: {balance}$`\n`Bet: {bet}$`\n\n**Available Games:**\n",
        view=view,
        ephemeral=False,
    )


@bot.tree.command(name="daily", description="Claim your daily reward")
async def daily(interaction: discord.Interaction):
    user_data = check_user(interaction.user.id)

    last_daily = user_data.get("last_daily")
    current_date = datetime.now().date()

    if (
        last_daily is not None
        and datetime.fromisoformat(last_daily).date() == current_date
    ):
        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            "You've already claimed your daily reward today. Come back tomorrow!",
            ephemeral=True,
        )
    else:
        counts(interaction.user.id, "count_dayly")

        reward_amount = 100  # Example reward amount
        add_balance(interaction.user.id, reward_amount)
        userdata = get_userdata()
        userdata[str(interaction.user.id)]["last_daily"] = current_date.isoformat()
        with open("config/userdata.json", "w") as file:
            json.dump(userdata, file, indent=4)

        await interaction.response.send_message(
            f"**Hey {interaction.user.mention}!**\n"
            f"You've claimed your daily reward of {reward_amount}$!\n"
            f"`New Balance: {str(int(user_data['balance'])+100)}$`",
            ephemeral=False,
        )


@bot.tree.command(name="info", description="Display user information")
@app_commands.describe(user="The user to display information for (optional)")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user or interaction.user
    user_data = check_user(target_user.id)
    balance = user_data["balance"]

    last_daily = user_data.get("last_daily", "Never")  
    if last_daily != "Never":  
        last_daily = datetime.strptime(
            last_daily, "%Y-%m-%d"
        ).strftime("%A, %d %B %Y")

    inventory = user_data.get("inventory", [])

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
        value=f"```fix\n{"``` ```fix\n".join(inventory) if inventory else "Empty"}```",
        inline=False,
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="achievements", description="Display all possible achievements")
async def achievements(interaction: discord.Interaction):
    achievements_list = data.get("achievements", {})
    embeds = []
    for achievement in achievements_list:
        achievement_data = achievements_list[achievement]
        embed = discord.Embed(
            title=achievement_data["name"],
            description=achievement_data["description"],
            color=discord.Color.greyple(),
        )

        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/{achievement_data['icon']}?raw=true"
        )

        embeds.append(embed)

    await interaction.response.send_message(embeds=embeds, ephemeral=True)


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("yoo"):
        await message.channel.send(message.author.mention + ", you're welcome!")

    if message.content.startswith("slotmachine"):
        await message.channel.send("🎰 Welcome to the Slot Machine! 🎰")
    await bot.process_commands(message)


bot.run(os.environ["TOKEN"])
