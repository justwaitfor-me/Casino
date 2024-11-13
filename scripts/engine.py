import discord
from discord.ui import View, Button, Modal, TextInput

from datetime import datetime
import os
import random

from scripts.functions import get_data, counts, subtract_balance, add_balance, user

async def blackjack_callback(interaction, bet: int):
    view = View()
    view.timeout = 0.01
    game = "blackjack"

    embed = discord.Embed(
        title=data["games"][game]["friendly_name"],
        description=data["games"][game]["description"],
        color=discord.Color.from_str(data["games"][game]["color"]),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/{data["games"][game]["author_img"]}?raw=true",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.png?raw=true"
    )
    # embed.add_field(name="Field 1", value="This is the value for field 1", inline=False)
    # embed.add_field(name="Field 2", value="This is the value for field 2", inline=True)
    embed.set_footer(
        text="Gambling can lead to financial loss, addiction, and emotional distress—play responsibly or not at all."
    )
    # embed.set_image(url="https://example.com/image.png")

    await interaction.response.edit_message(content="", view=view, embed=embed)


async def double_or_nothing_callback(interaction, bet: int):
    view = View()
    game = "double_or_nothing"

    counts(interaction.user.id, "count_gambles")

    double_or_nothing_chance = data["games"][game]["win_chance"]
    max_rounds = data["games"][game]["max_rounds"]

    current_round = 1
    current_amount = bet

    async def update_embed():
        embed = discord.Embed(
            title=data["games"][game]["friendly_name"],
            description=data["games"][game]["description"],
            color=discord.Color.from_str(data["games"][game]["color"]),
            timestamp=datetime.now(),
        )
        embed.set_author(
            name="Slot Machine",
            icon_url=f"{str(os.environ['IMAGES'])}/{data['games'][game]['author_img']}?raw=true",
        )
        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.gif?raw=true"
        )

        embed.add_field(name="Bet", value=f"{bet}$", inline=True)
        embed.add_field(name="Current Amount", value=f"{current_amount}$", inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(
            name="Current Round", value=f"{current_round}/{max_rounds}", inline=True
        )
        embed.add_field(name="Multiplier", value=f"{2*current_round}x", inline=True)
        embed.add_field(name="", value="", inline=False)

        embed.set_image(
            url=f"{str(os.environ['VIDEOS'])}/win-{random.randint(1, 5)}.gif?raw=true"
        )

        embed.set_footer(
            text="Gambling can lead to financial loss, addiction, and emotional distress—play responsibly or not at all."
        )
        return embed

    async def double_button_callback(interaction):
        nonlocal current_round, current_amount
        counts(interaction.user.id, "count_doubles")

        if random.random() < double_or_nothing_chance:
            result = current_amount * (2 * current_round)
        else:
            result = 0

        if result > current_amount:
            current_amount = result
            current_round += 1
            if current_round > max_rounds:
                await end_game(interaction)
            else:
                await interaction.response.edit_message(
                    embed=await update_embed(), view=view
                )
        else:
            await end_game(interaction, lost=True)

    async def leave_button_callback(interaction):
        counts(interaction.user.id, "count_leaves")
        await end_game(interaction)

    async def end_game(interaction, lost=False):
        embed = await update_embed()
        embed.clear_fields()
        if lost:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You lost everything!**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/loose-{random.randint(1, 6)}.gif?raw=true"
            )
            subtract_balance(interaction.user.id, bet)
        else:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You won {current_amount}$**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/funny-{random.randint(1, 2)}.gif?raw=true"
            )
            add_balance(interaction.user.id, current_amount)

            counts(interaction.user.id, "count_winnings")

        await interaction.response.edit_message(embed=embed, view=None, content="")

    double_button = Button(label="Double", style=discord.ButtonStyle.primary)
    double_button.callback = lambda i: double_button_callback(i) if user(i) else None
    leave_button = Button(label="Leave", style=discord.ButtonStyle.danger)
    leave_button.callback = lambda i: leave_button_callback(i) if user(i) else None

    view.add_item(double_button)
    view.add_item(leave_button)

    if random.random() < double_or_nothing_chance:
        result = bet * (2 * current_round)
    else:
        result = 0
    if result > current_amount:
        current_amount = result
        current_round += 1
        if current_round > max_rounds:
            await end_game(interaction)
        else:
            await interaction.response.edit_message(
                embed=await update_embed(), view=view, content=""
            )
    else:
        await end_game(interaction, lost=True)


async def roulette_callback(interaction, bet: int):
    view = View()
    view.timeout = 0.01
    game = "roulette"

    embed = discord.Embed(
        title=data["games"][game]["friendly_name"],
        description=data["games"][game]["description"],
        color=discord.Color.from_str(data["games"][game]["color"]),
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="Slot Machine",
        icon_url=f"{str(os.environ['IMAGES'])}/{data["games"][game]["author_img"]}?raw=true",
    )
    embed.set_thumbnail(
        url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.png?raw=true"
    )
    # embed.add_field(name="Field 1", value="This is the value for field 1", inline=False)
    # embed.add_field(name="Field 2", value="This is the value for field 2", inline=True)
    embed.set_footer(
        text="Gambling can lead to financial loss, addiction, and emotional distress—play responsibly or not at all."
    )
    # embed.set_image(url="https://example.com/image.png")

    await interaction.response.edit_message(content="", view=view, embed=embed)


async def guess_the_number_callback(interaction, bet: int):
    view = View()
    game = "guessthenumber"

    counts(interaction.user.id, "count_gambles")

    # Game settings
    target_number = random.randint(1, 10)  # Number to guess
    attempts = data["games"][game]["attempts"]  # Number of attempts allowed
    current_attempt = 0
    multiplier = data["games"][game]["multiplier"]  # Multiplier for correct guess
    win_amount = bet * multiplier

    async def update_embed():
        """Creates the dynamic embed to show game state to the user."""
        embed = discord.Embed(
            title=data["games"][game]["friendly_name"],
            description=data["games"][game]["description"],
            color=discord.Color.from_str(data["games"][game]["color"]),
            timestamp=datetime.now(),
        )
        embed.set_author(
            name="Guess The Number",
            icon_url=f"{str(os.environ['IMAGES'])}/{data['games'][game]['author_img']}?raw=true",
        )
        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.png?raw=true"
        )
        embed.add_field(name="Bet", value=f"{bet}$", inline=True)
        embed.add_field(name="Potential Winnings", value=f"{win_amount}$", inline=True)
        embed.add_field(
            name="Attempts", value=f"{attempts - current_attempt}", inline=True
        )
        return embed

    async def end_game(interaction, won: bool):
        """Ends the game with either a win or loss message."""
        embed = await update_embed()
        embed.clear_fields()
        if won:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention}, you guessed correctly and won {win_amount}$!**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/win-{random.randint(1, 5)}.gif?raw=true"
            )
            add_balance(interaction.user.id, win_amount)
            counts(interaction.user.id, "count_winnings")
        else:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention}, you lost! The number was {target_number}.**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/lose-{random.randint(1, 6)}.gif?raw=true"
            )
            subtract_balance(interaction.user.id, bet)

        await interaction.response.edit_message(embed=embed, view=None)

    class GuessModal(Modal):
        """Modal for users to input their guess."""

        guess_input = TextInput(
            label="Enter your guess (1-10)",
            placeholder="Type a number between 1 and 10",
            required=True,
        )

        async def on_submit(self, interaction):
            nonlocal current_attempt
            try:
                user_guess = int(self.guess_input.value)
            except ValueError:
                await interaction.response.send_message(
                    "Please enter a valid number!", ephemeral=True
                )
                return

            current_attempt += 1

            if user_guess == target_number:
                await end_game(interaction, won=True)
            elif current_attempt >= attempts:
                await end_game(interaction, won=False)
            else:
                await interaction.response.send_message(
                    f"Incorrect guess! You have {attempts - current_attempt} attempts left.",
                    ephemeral=True,
                )
                await interaction.followup.edit_message(
                    embed=await update_embed(),
                    view=view,
                    message_id=interaction.message.id,
                )

    async def open_guess_modal(interaction):
        """Opens the guess modal when the user wants to make a guess."""
        await interaction.response.send_modal(GuessModal(title="Guess the Number"))

    async def quit_button_callback(interaction):
        """Allows the user to quit early, ending the game."""
        counts(interaction.user.id, "count_leaves")
        await end_game(interaction, won=False)

    # Set up buttons for guessing and quitting
    guess_button = Button(label="Make a Guess", style=discord.ButtonStyle.primary)
    quit_button = Button(label="Quit", style=discord.ButtonStyle.danger)

    guess_button.callback = open_guess_modal
    quit_button.callback = quit_button_callback

    view.add_item(guess_button)
    view.add_item(quit_button)

    # Send initial game embed
    await interaction.response.edit_message(
        content="", embed=await update_embed(), view=view
    )

data = get_data()