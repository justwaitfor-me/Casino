import discord
from discord.ui import View, Button, Modal, TextInput

from datetime import datetime
import os
import random
import asyncio

from scripts.functions import get_data, counts, subtract_balance, add_balance, user


async def blackjack_callback(interaction, bet: int):
    view = View()
    game = "blackjack"

    print(f"Current game: {game} by user {interaction.user.name} at {datetime.now()}")

    counts(interaction.user.id, interaction.guild_id, "count_gambles")

    player_hand = []
    dealer_hand = []
    current_amount = bet

    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4  # Simplified deck

    random.shuffle(deck)

    card_emojis = data["games"][game]["card_emojis"]
    descriptions = data["games"][game]["descriptions"]

    # Modify the draw_card function to return the card number and its corresponding emoji
    def draw_card(hand):
        card = deck.pop()
        hand.append(card)
        if sum(hand) > 21 and 11 in hand:  # Convert Ace to 1 if busting
            hand[hand.index(11)] = 1
        return card, card_emojis[str(card)]

    async def update_embed(final=False):
        # Convert the hands to emoji strings
        player_hand_emojis = " ".join([card_emojis[str(card)] for card in player_hand])
        dealer_hand_emojis = (
            " ".join([card_emojis[str(card)] for card in dealer_hand[:1]])
            + f" + {card_emojis["1"]}"
            if len(dealer_hand) > 1
            else card_emojis[str(dealer_hand[0])]
        )

        if not final:
            description = f"{data['games'][game]['description']}\n\n{"".join(descriptions)}"
        else:
            description = f"{data['games'][game]['description']}"

        embed = discord.Embed(
            title=data["games"][game]["friendly_name"],
            description=description,
            color=discord.Color.from_str(data["games"][game]["color"]),
            timestamp=datetime.now(),
        )

        embed.set_author(
            name="Blackjack",
            icon_url=f"{str(os.environ['IMAGES'])}/{data['games'][game]['author_img']}?raw=true",
        )
        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.gif?raw=true"
        )
        embed.add_field(
            name=f"{interaction.user.name}'s Hand",
            value=f"{player_hand} (Total: {sum(player_hand)})",
            inline=False,
        )
        embed.add_field(name="Current Bet", value=f"{current_amount}$", inline=True)
        embed.set_footer(
            text="Gambling can lead to financial loss, addiction, and emotional distress—play responsibly or not at all."
        )

        content = f"\n# {player_hand_emojis} (Total: {sum(player_hand)})\n# {dealer_hand_emojis}"

        return [embed, content]

    async def hit_button_callback(interaction):
        nonlocal player_hand
        draw_card(player_hand)
        if sum(player_hand) > 21:
            await end_game(interaction, lost=True)
        else:
            await interaction.response.edit_message(
                embed=(await update_embed())[0],
                view=view,
                content=f"{interaction.user.mention}{(await update_embed())[1]}",
            )

    async def stand_button_callback(interaction):
        nonlocal dealer_hand
        while sum(dealer_hand) < 17:  # Dealer hits until 17 or more
            draw_card(dealer_hand)

        if sum(dealer_hand) > 21 or sum(player_hand) > sum(dealer_hand):
            await end_game(interaction, lost=False)
        elif sum(player_hand) == sum(dealer_hand):
            await end_game(interaction, tie=True)
        else:
            await end_game(interaction, lost=True)

    async def end_game(interaction, lost=False, tie=False):
        embed = (await update_embed(final=True))[0]
        embed.clear_fields()
        if lost:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You lost your bet of {bet}$**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/loose-{random.randint(1, 6)}.gif?raw=true"
            )
            subtract_balance(interaction.user.id, interaction.guild_id, bet)
        elif tie:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} It's a tie! Your bet of {bet}$ is returned.**",
                inline=False,
            )
        else:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You won {2 * bet}$!**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/win-{random.randint(1, 5)}.gif?raw=true"
            )
            add_balance(interaction.user.id, interaction.guild_id, 2 * bet)

            counts(interaction.user.id, interaction.guild_id, "count_winnings")

        await interaction.response.edit_message(
            embed=embed, view=None, content=interaction.user.mention
        )

    # Deal initial cards
    draw_card(player_hand)
    draw_card(player_hand)
    draw_card(dealer_hand)
    draw_card(dealer_hand)

    # Buttons
    hit_button = Button(label="Hit", style=discord.ButtonStyle.primary)
    hit_button.callback = lambda i: hit_button_callback(i) if user(i) else None

    stand_button = Button(label="Stand", style=discord.ButtonStyle.secondary)
    stand_button.callback = lambda i: stand_button_callback(i) if user(i) else None

    view.add_item(hit_button)
    view.add_item(stand_button)

    await interaction.response.edit_message(
        embed=(await update_embed())[0], view=view, content=f"{interaction.user.mention}{(await update_embed())[1]}"
    )


async def double_or_nothing_callback(interaction, bet: int):
    view = View()
    game = "double_or_nothing"

    print(f"Current game: {game} by user {interaction.user.name} at {datetime.now()}")

    counts(interaction.user.id, interaction.guild_id, "count_gambles")

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
        counts(interaction.user.id, interaction.guild_id, "count_doubles")

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
        counts(interaction.user.id, interaction.guild_id, "count_leaves")
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
            subtract_balance(interaction.user.id, interaction.guild_id, bet)
        else:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You won {current_amount}$**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/funny-{random.randint(1, 2)}.gif?raw=true"
            )
            add_balance(interaction.user.id, interaction.guild_id, current_amount)

            counts(interaction.user.id, interaction.guild_id, "count_winnings")

        await interaction.response.edit_message(
            embed=embed, view=None, content=interaction.user.mention
        )

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
                embed=await update_embed(), view=view, content=interaction.user.mention
            )
    else:
        await end_game(interaction, lost=True)


async def roulette_callback(interaction, bet: int):
    game = "roulette"
    counts(interaction.user.id, interaction.guild_id, "count_gambles")

    roulette_colors = data["games"][game]["roulette_colors"]
    roulette_odds = data["games"][game]["roulette_odds"]
    roulette_multiplier = data["games"][game]["roulette_multiplier"]

    current_amount = bet
    selected_color = None

    print(f"Current game: {game} by user {interaction.user.name} at {datetime.now()}")

    class RouletteModal(Modal):
        """Modal for user to select their roulette color."""

        color_input = TextInput(
            label="Choose a color (Red, Black, Green)",
            placeholder="Enter Red, Black, or Green",
            required=True,
        )

        async def on_submit(self, interaction):
            nonlocal selected_color, current_amount
            user_color = self.color_input.value.strip().capitalize()

            if user_color not in roulette_colors:
                await interaction.response.send_message(
                    "Invalid color! Please choose Red, Black, or Green.",
                    ephemeral=True,
                )
                return

            selected_color = user_color
            counts(
                interaction.user.id, interaction.guild_id, f"count_{user_color.lower()}"
            )

            roll_result = random.choices(roulette_colors, weights=roulette_odds, k=1)[
                0
            ]  # Simulates the roulette roll

            if roll_result == selected_color:
                current_amount *= roulette_multiplier[user_color]
                counts(interaction.user.id, interaction.guild_id, "count_winnings")
                await end_game(interaction, roll_result, won=True)
            else:
                current_amount = 0
                await end_game(interaction, roll_result, won=False)

    async def update_embed():
        embed = discord.Embed(
            title=data["games"][game]["friendly_name"],
            description=data["games"][game]["description"],
            color=discord.Color.from_str(data["games"][game]["color"]),
            timestamp=datetime.now(),
        )
        embed.set_author(
            name="Roulette Table",
            icon_url=f"{str(os.environ['IMAGES'])}/{data['games'][game]['author_img']}?raw=true",
        )

        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.gif?raw=true"
        )

        embed.add_field(name="Bet", value=f"{bet}$", inline=True)
        embed.add_field(
            name="Selected Color", value=f"{selected_color or 'None'}", inline=True
        )
        embed.add_field(name="Current Amount", value=f"{current_amount}$", inline=False)

        embed.set_footer(
            text="Gambling can lead to financial loss, addiction, and emotional distress—play responsibly or not at all."
        )
        return embed

    async def end_game(interaction, roll_result, won: bool):
        embed = await update_embed()
        embed.clear_fields()

        if won:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You won {current_amount}$ on {roll_result}!**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/funny-{random.randint(1, 2)}.gif?raw=true"
            )

            add_balance(interaction.user.id, interaction.guild_id, current_amount)
            counts(interaction.user.id, interaction.guild_id, "count_winnings")
        else:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention} You lost everything on {roll_result}!**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/loose-{random.randint(1, 6)}.gif?raw=true"
            )
            subtract_balance(interaction.user.id, interaction.guild_id, bet)

        await interaction.response.edit_message(
            embed=embed, view=None, content=interaction.user.mention
        )

    # Open the roulette modal for user input
    await interaction.response.send_modal(
        RouletteModal(title="Roulette Color Selection")
    )


async def guess_the_number_callback(interaction, bet: int):
    view = View()
    game = "guessthenumber"

    print(f"Current game: {game} by user {interaction.user.name} at {datetime.now()}")

    counts(interaction.user.id, interaction.guild_id, "count_gambles")

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
            add_balance(interaction.user.id, interaction.guild_id, win_amount)
            counts(interaction.user.id, interaction.guild_id, "count_winnings")
        else:
            embed.add_field(
                name="Result",
                value=f"**{interaction.user.mention}, you lost! The number was {target_number}.**",
                inline=False,
            )
            embed.set_image(
                url=f"{str(os.environ['VIDEOS'])}/lose-{random.randint(1, 6)}.gif?raw=true"
            )
            subtract_balance(interaction.user.id, interaction.guild_id, bet)

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
        counts(interaction.user.id, interaction.guild_id, "count_leaves")
        await end_game(interaction, won=False)

    # Set up buttons for guessing and quitting
    guess_button = Button(label="Make a Guess", style=discord.ButtonStyle.primary)
    guess_button.callback = lambda i: open_guess_modal(i) if user(i) else None
    quit_button = Button(label="Quit", style=discord.ButtonStyle.danger)
    quit_button.callback = lambda i: quit_button_callback(i) if user(i) else None

    view.add_item(guess_button)
    view.add_item(quit_button)

    # Send initial game embed
    await interaction.response.edit_message(
        content=interaction.user.mention, embed=await update_embed(), view=view
    )


async def slot_machine_callback(interaction, bet: int):
    game = "slot_machine"
    counts(interaction.user.id, interaction.guild_id, "count_gambles")

    # Slot data from the JSON configuration
    slot_data = data["games"][game]["slot_data"]  # New JSON structure
    slot_symbols = [item["symbol"] for item in slot_data]
    slot_odds = [item["odds"] for item in slot_data]
    slot_multipliers = {item["symbol"]: item["multiplier"] for item in slot_data}
    additional_multipliers = {
        item["symbol"]: item["additional_multiplier"] for item in slot_data
    }

    # Current bet and result placeholder
    current_amount = bet
    spin_result = None

    print(f"Current game: {game} by user {interaction.user.name} at {datetime.now()}")

    async def update_embed(spin_result=None):
        # Create a dynamic description based on slot_data
        if spin_result is None:
            chances_description = "\n".join(
                f"{item['symbol']}: **Chance:** {item['odds']:.1%} | "
                f"**Multiplier:** {item['multiplier']}x | **Additional:** +{item['additional_multiplier']}x"
                for item in slot_data
            )
            chances_description += "\n\n" + "".join(data["games"][game]["descriptions"])
        else:
            chances_description = ""

        description = (
            f"**Chances and Multipliers:**\n{chances_description}\n\n"
            f"{data['games'][game]['description']}"
        )

        embed = discord.Embed(
            title=data["games"][game]["friendly_name"],
            description=description,
            color=discord.Color.from_str(data["games"][game]["color"]),
            timestamp=datetime.now(),
        )
        embed.set_author(
            name="Slot Machine",
            icon_url=f"{str(os.environ['IMAGES'])}/{data['games'][game]['author_img']}?raw=true",
        )
        embed.set_thumbnail(
            url=f"{str(os.environ['IMAGES'])}/croupier-{random.randint(1, 2)}.png?raw=true"
        )

        embed.add_field(name="Bet", value=f"{bet}$", inline=True)

        if spin_result:
            embed.add_field(
                name="Spin Result", value=" | ".join(spin_result), inline=False
            )

        embed.set_footer(
            text="Gambling can lead to financial loss, addiction, and emotional distress—play responsibly or not at all."
        )
        return embed

    # Spin button click handler
    class SpinButtonView(View):
        def __init__(self, interactionx: discord.Interaction):
            super().__init__()
            self.interactionx = interactionx  # Store interactionx for later use

        @discord.ui.button(label="Spin", style=discord.ButtonStyle.green)
        async def spin_button(self, button: Button, interaction: discord.Interaction):
            nonlocal spin_result, current_amount

            # Spin the reels with random emojis and update the embed
            spin_result = [
                random.choices(
                    slot_symbols, weights=slot_odds, k=2
                )  # Three symbols per line
                for _ in range(3)  # Three lines
            ]

            prev_result = [
                random.choices(slot_symbols, weights=slot_odds, k=2) for _ in range(3)
            ]
            current_result = [
                random.choices(slot_symbols, weights=slot_odds, k=2) for _ in range(3)
            ]

            prev_arrow = random.choice(data["games"][game]["arrows"])
            current_arrow = random.choice(data["games"][game]["arrows"])

            left_arrow = ""
            right_arrow = ""

            for i in range(16):  # Update the spin 10 times to simulate animation
                future_result = [
                    random.choices(slot_symbols, weights=slot_odds, k=2)
                    for _ in range(3)
                ]
                future_arrow = random.choice(data["games"][game]["arrows"])

                content = f"{self.interactionx.user.mention}\n# {future_arrow}{" | ".join([f"{' | '.join(line)}" for line in future_result])}{future_arrow}\n# **{current_arrow}{right_arrow}{" | ".join([f"{' | '.join(line)}" for line in current_result])}{left_arrow}{current_arrow}**\n# {prev_arrow}{" | ".join([f"{' | '.join(line)}" for line in prev_result])}{prev_arrow}"

                prev_result = current_result
                current_result = future_result

                prev_arrow = current_arrow
                current_arrow = future_arrow

                await self.interactionx.followup.edit_message(
                    self.interactionx.message.id,
                    content=content,
                    view=None,
                    embed=None,
                )  # Correct usage of interactionx

                if i < 11:
                    await asyncio.sleep(0.1)  # Wait before updating again
                elif i == 14:
                    current_arrow = ""
                    right_arrow = data["games"][game]["final_arrows"][0]
                    left_arrow = data["games"][game]["final_arrows"][1]
                else:
                    await asyncio.sleep(0.1 * (i / 2))  # Wait before updating again

            await asyncio.sleep(1.5)

            embed = await update_embed([f"{' | '.join(line)}" for line in prev_result])

            # Initialize variables
            win = 0
            consecutive_count = 1  # Start with the first symbol
            last_symbol = prev_result[0][0]  # The first symbol in the first row

            # Flatten the grid of symbols (assuming prev_result is a 2D list)
            symbols = [symbol for sublist in prev_result for symbol in sublist]

            # Iterate through the flattened list of symbols
            for i in range(1, len(symbols)):
                symbol = symbols[i]

                if symbol == last_symbol:
                    consecutive_count += (
                        1  # Increment the consecutive count for the same symbol
                    )
                else:
                    # Handle the previous sequence of symbols
                    if (
                        consecutive_count >= 3
                    ):  # Only process sequences with 2 or more consecutive symbols
                        base_multiplier = slot_multipliers[
                            last_symbol
                        ]  # Base multiplier for the symbol
                        additional_multiplier = additional_multipliers.get(
                            last_symbol, 1
                        )

                        # Total multiplier for the sequence
                        total_multiplier = base_multiplier * (
                            (consecutive_count - 1) + additional_multiplier
                        )

                        # Calculate the win for this sequence
                        sequence_win = bet * total_multiplier
                        win += sequence_win

                    # Reset for the new symbol
                    consecutive_count = 1
                    last_symbol = symbol

            # After the loop, check the last sequence of symbols
            if consecutive_count >= 3:
                base_multiplier = slot_multipliers[last_symbol]
                additional_multiplier = additional_multipliers.get(last_symbol, 1)
                total_multiplier = base_multiplier * (
                    (consecutive_count - 1) + additional_multiplier
                )

                # Calculate the win for this last sequence
                sequence_win = bet * total_multiplier
                win += sequence_win

            # Gewinnanzeige
            if win > 0:
                counts(
                    self.interactionx.user.id,
                    self.interactionx.guild_id,
                    "count_winnings",
                )
                embed.add_field(
                    name="Result",
                    value=f"**{self.interactionx.user.mention} You won {win}$ on the spin!**",
                    inline=True,
                )
                embed.add_field(
                    name="Multiplayers",
                    value=f"Base multiplayer: {base_multiplier}\nAditional multiplayer: {additional_multiplier}\n**Total multiplayer: {total_multiplier}**",
                    inline=False,
                )
                embed.set_image(
                    url=f"{str(os.environ['VIDEOS'])}/funny-{random.randint(1, 2)}.gif?raw=true"
                )
                add_balance(self.interactionx.user.id, self.interactionx.guild_id, win)
            else:
                embed.add_field(
                    name="Result",
                    value=f"**{self.interactionx.user.mention} You lost everything on the spin!**",
                    inline=False,
                )
                embed.set_image(
                    url=f"{str(os.environ['VIDEOS'])}/loose-{random.randint(1,6)}.gif?raw=true"
                )
                subtract_balance(
                    self.interactionx.user.id, self.interactionx.guild_id, bet
                )

            await self.interactionx.followup.edit_message(
                self.interactionx.message.id,
                embed=embed,
                view=None,
                content=self.interactionx.user.mention,
            )

    # Create the Spin button view with interactionx
    view = SpinButtonView(interaction)

    embed = await update_embed()
    await interaction.response.edit_message(
        embed=embed, view=view, content=interaction.user.mention
    )


data = get_data()
