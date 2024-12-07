from discord.ext import commands
from discord.ui import Button, View
import discord
import random
from datetime import datetime

from scripts.functions import (
    add_balance,
    user,
)


class PokerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rooms = {}

    async def start_game(self, interaction, room_id, bet):
        room = self.rooms[room_id]
        deck = room["deck"]
        players = room["players"]
        pot = room["pot"]

        # Ensure the game starts only with enough players
        if len(players) < 2:
            return await interaction.followup.send(
                "Not enough players to start the game. Minimum 2 players required.",
                ephemeral=True,
            )

        # Deal two cards to each player
        for player in players:
            room["player_hands"][player.id] = [deck.pop(), deck.pop()]

        async def deal_community_cards(round_number: int):
            """Deals the community cards based on the round number."""
            if round_number == 1:
                room["community_cards"].extend([deck.pop() for _ in range(3)])  # Flop
            elif round_number in [2, 3]:
                room["community_cards"].append(deck.pop())  # Turn and River

        async def get_game_embed(state: str):
            """Generates the game embed to show the current state of the game."""
            embed = discord.Embed(
                title=f"Poker Game - {state}",
                description=f"Pot: {pot}$\nPlayers: {', '.join([p.name for p in players])}",
                color=discord.Color.gold(),
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="Community Cards",
                value=" ".join(room["community_cards"])
                if room["community_cards"]
                else "No cards yet.",
                inline=False,
            )
            for player in players:
                if player == interaction.user:
                    embed.add_field(
                        name=f"{player.name}'s Cards",
                        value=" ".join(room["player_hands"][player.id]),
                        inline=True,
                    )
                else:
                    embed.add_field(
                        name=f"{player.name}'s Cards", value="Hidden", inline=True
                    )
            embed.set_footer(text="Make your move!")
            return embed

        async def end_game(winner):
            """Ends the game and announces the winner."""
            add_balance(winner.id, interaction, pot)
            del self.rooms[room_id]

            embed = discord.Embed(
                title="Game Over!",
                description=f"**{winner.mention} wins the pot of {pot}$!**",
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )
            await interaction.channel.send(embed=embed)

        async def poker_round(round_number, bet):
            """Handles one round of poker (betting, community card dealing)."""
            await deal_community_cards(round_number)

            view = View()
            call_button = Button(label="Call", style=discord.ButtonStyle.primary)
            raise_button = Button(label="Raise", style=discord.ButtonStyle.success)
            fold_button = Button(label="Fold", style=discord.ButtonStyle.danger)

            async def call_callback(interaction):
                nonlocal pot
                pot += bet
                await interaction.response.edit_message(
                    embed=await get_game_embed("Call"), view=view
                )

            async def raise_callback(interaction):
                nonlocal pot
                pot += bet * 2  # Adjust the raise multiplier as needed
                await interaction.response.edit_message(
                    embed=await get_game_embed("Raise"), view=view
                )

            async def fold_callback(interaction):
                players.remove(interaction.user)
                if len(players) == 1:
                    await end_game(players[0])
                else:
                    await interaction.response.edit_message(
                        embed=await get_game_embed("Fold"), view=view
                    )

            call_button.callback = lambda i: call_callback(i) if user(i) else None
            raise_button.callback = lambda i: raise_callback(i) if user(i) else None
            fold_button.callback = lambda i: fold_callback(i) if user(i) else None

            view.add_item(call_button)
            view.add_item(raise_button)
            view.add_item(fold_button)

            embed = await get_game_embed(f"Round {round_number}")
            await interaction.channel.send(embed=embed, view=view)

            if len(players) == 1:
                await end_game(players[0])

        # Play the rounds
        for round_number in range(1, 4):  # Pre-flop, Flop, Turn, River
            await poker_round(round_number, bet)

        await end_game(random.choice(players))  # Pick a winner randomly for now


async def setup(bot):
    await bot.add_cog(PokerCog(bot))
