# Slot Machine Discord Bot

Welcome to the Slot Machine Discord Bot! This bot offers various games like Blackjack, Roulette, and Guess the Number for you to play and enjoy on Discord.

## Features

- **Play popular games** including Blackjack, Double or Nothing, Roulette, and Guess the Number.
- **Daily Rewards** with the `/daily` command.
- **Track Achievements** and player stats.
- **Easy to use** with Discord's slash commands and buttons.

## Commands

- **`/help`** - Displays help text.
- **`/play <bet_amount>`** - Starts a game session. Specify the bet amount to join.
- **`/daily`** - Claims daily rewards (once per day).
- **`/info [user]`** - Shows player information.
- **`/achievements`** - Lists available achievements in the bot.

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/justwaitfor-me/Casino.git
   cd Casino
   ```

2. **Install dependencies:**
   Make sure you have Python installed. Then install the necessary libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the `.env` file:**
   Create a `.env` file in the project root and add your Discord bot token and other environment variables:

   ```plaintext
   DISCORD_TOKEN=your_discord_token_here
   ```

4. **Run the bot:**
   Start the bot by running:
   ```bash
   python bot.py
   ```

---

## Usage

1. **Add the bot to your server:**
   Invite the bot using the OAuth2 URL provided in Discord’s Developer Portal.

2. **Playing Games:**

   - Use `/play <bet_amount>` to start a game.
   - Follow on-screen instructions to select a game and play.

3. **Claiming Rewards:**
   - Use `/daily` to claim daily rewards and `/achievements` to view available achievements.

---

## Contributing

We welcome contributions to the Slot Machine Discord Bot! Follow these steps to contribute:

1. **Fork the repository.**
2. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. **Make your changes** to the codebase.
4. **Test your changes** to ensure they work as expected.
5. **Commit and push** your changes to your branch:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature-name
   ```
6. **Open a pull request** in the main repository with a description of your changes.

### Code Style

- Follow PEP 8 for Python code.
- Document functions and modules with clear comments and docstrings.

---

## File Structure

- `scripts/functions.py`: Contains main bot functions.
- `scripts/engine.py`: Handles game logic.
- `config/userdata.json`: Stores user data and stats.
- `.env`: Stores environment variables (like your bot token).

---

## License

This project is licensed under the MIT License.

---

Enjoy gaming with the Slot Machine Discord Bot!
