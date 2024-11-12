import discord
from discord.ext import commands
import asyncio
from discord import app_commands
import os, dotenv, datetime, random, json
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

dotenv.load_dotenv(".env")

with open('data.json', 'r') as file:
    data = json.load(file)

casino_game = random.choice(data.get('casino_games', {}))

async def blackjack_callback(interaction):
    view = View()
    view.timeout = 0.01
    
    embed = discord.Embed(
        title="Embed Title",
        description="This is the description of the embed.",
        color=discord.Color.blue()  # You can also use other colors
    )
    embed.set_author(name="Slot Machine", icon_url="assets/img/kasino-4.png")
    embed.set_thumbnail(url="https://example.com/thumbnail.png")
    embed.add_field(name="Field 1", value="This is the value for field 1", inline=False)
    embed.add_field(name="Field 2", value="This is the value for field 2", inline=True)
    embed.set_footer(text="This is the footer text", icon_url="https://example.com/footer_icon.png")
    embed.set_image(url="https://example.com/image.png")
    
    await interaction.response.edit_message(content="", view=view, embed=embed)

async def double_or_nothing_callback(interaction):
    view = View()
    view.timeout = 0.01
    await interaction.response.edit_message(content=f"Double or Nothing game started, {interaction.user.mention}!", view=view)

async def roulette_callback(interaction):
    view = View()
    view.timeout = 0.01
    await interaction.response.edit_message(content=f"Roulette game started, {interaction.user.mention}!", view=view)

async def guess_the_number_callback(interaction):
    view = View()
    view.timeout = 0.01
    await interaction.response.edit_message(content=f"Guess the Number game started, {interaction.user.mention}!", view=view)

def check_user(user_id):
    if str(user_id) in data.get('users_data', {}):
        return data['users_data'][str(user_id)]
    else:
        new_user = {
            "balance": 1000,
            "last_daily": None,
            "inventory": []
        }
        
        # Create a new user in the data file
        data.setdefault('users_data', {})[str(user_id)] = new_user
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
        return new_user

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{casino_game["name"]} | /help for commands",
            state=casino_game["fun_fact"]
        )
    )
    
@bot.tree.command(name='help', description='Lists all available commands')
async def list(interaction: discord.Interaction):
    options = ",".join(casino_game['options'])
    await interaction.response.send_message(f"Available options: {options}")



@bot.tree.command(name="play", description="Play the casino games")
async def play(interaction: discord.Interaction):
    game1_button = Button(label="Blackjack", style=discord.ButtonStyle.primary, disabled=False, emoji="<:casinochip1:1304579248908009562>", row=1)
    game2_button = Button(label="Double or Nothing", style=discord.ButtonStyle.danger, disabled=False, emoji="<:casinochip2:1304579236496932904>", row=2)
    game3_button = Button(label="Roulett", style=discord.ButtonStyle.success, disabled=False, emoji="<:casinochip3:1304579224597954612>", row=3)
    game4_button = Button(label="Guess the Number", style=discord.ButtonStyle.grey, disabled=False, emoji="<:casinochip4:1304579213189189693>", row=4)

    game1_button.callback = blackjack_callback
    game2_button.callback = double_or_nothing_callback
    game3_button.callback = roulette_callback
    game4_button.callback = guess_the_number_callback

    view = View()
    view.add_item(game1_button)
    view.add_item(game2_button)
    view.add_item(game3_button)
    view.add_item(game4_button)


    user_data = check_user(interaction.user.id)
    balance = user_data['balance']

    await interaction.response.send_message(
        f"**Hey {interaction.user.mention}!**\n"
        f"Welcome to the casino! Choose a game to play and try your luck.\n"
        f"`Balance: {balance}$`\n\n**Available Games:**\n",
        view=view,
        ephemeral=True
    )



@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    await bot.process_commands(message)

bot.run(os.environ['TOKEN'])