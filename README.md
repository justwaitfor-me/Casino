# Discord Casino Bot

[![GitHub forks](https://badgen.net/github/forks/justwaitfor-me/Casino/)](https://GitHub.com/justwaitfor-me/Casino/)
[![GitHub stars](https://badgen.net/github/stars/justwaitfor-me/Casino/)](https://GitHub.comjustwaitfor-me/Casino/)
[![GitHub watchers](https://badgen.net/github/watchers/justwaitfor-me/Casino/)](https://GitHub.com/justwaitfor-me/Casino/)
[![GitHub commits](https://img.shields.io/github/commits-since/justwaitfor-me/Casino/v1.9.svg)](https://GitHub.com/justwaitfor-me/Casino/)
[![GitHub release](https://img.shields.io/github/release/justwaitfor-me/Casino.svg)](https://GitHub.com/justwaitfor-me/Casino/)
[![GitHub license](https://badgen.net/github/license/justwaitfor-me/Casino/)](https://github.com/justwaitfor-me/Casino/)
### A Discord bot that provides various casino-related features, such as slot machines, betting, and user management.

[![image](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#white)](https://github.com/sponsors/justwaitfor-me)
[![image](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/justwaitforme)
[![image](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/Y2S4j28BXb)
[![image](https://img.shields.io/badge/website-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://casino.justwaitforme.de)

[![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](#)
[![image](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)](#)
[![image](https://img.shields.io/badge/pypi-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](#)
[![image](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=Raspberry%20Pi&logoColor=white)](#)
[![image](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](#)
[![image](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white)](#)


## Features

Slot Machine: Users can play a slot machine game with different payouts and winning chances.
Betting: Users can place bets on their slot machine games, increasing their chances of winning.
User Management: The bot keeps track of user balances, daily rewards, and achievements.
Leaderboard: Users can view a leaderboard to see their rankings based on their balances and achievements.
Achievements: Users can earn achievements by participating in the casino and completing various tasks.
Customizable Configuration: Server administrators can customize various aspects of the bot, such as daily rewards, maximum transactions, and slot machine payouts.

## Installation

1.  Install Python 3.9 or higher.
2.  Create a new Discord bot and obtain its token.
3.  Clone this repository.
4.  Install the required dependencies by running pip install -r requirements.txt.
5.  Create a new file named config.py and add your Discord bot token and other necessary configurations.
6.  Run the bot by executing python bot.py.

## Usage

### Once the bot is running, you can interact with it using commands in Discord. Here are some example commands:

| Command                           | Description                                                       |
| ---                               | ---                                                               |
| /play: <bet>                      | Play a slot machine game with a default bet of 100$.              |
| /balance:                         | View your current balance.                                        |
| /leaderboard:                     | View the top 7 users by balance and achievements.                 |   
| /info:                            | View your user information.                                       |
| /daily:                           | Claim your daily reward.                                          |
| /luckywheel:                      | Claim your lucky wheel reward.                                    |
| /achievements:                    | View all possible achievements.                                   |
| /send <user> <amount>:            | Send money to another user.                                       |
| /add_balance <user> <amount>:     | Add balance to a user (administrator only).                       |
| /subtract_balance <user> <amount>:| Subtract balance from a user (administrator only).                |
| /download_log:                    | Download the current log file (administrator only).               |
| /download_serverdata:             | Download the current serverdata file (administrator only).        |
| /list_servers:                    | Lets you select a server to list the data (administrator only).   |
| /edit_config:                     | Edit server configuration (administrator only).                   |
| /ban_player:                      | Ban a player from the playing (ADMIN).                            |

## Customization

### You can customize various aspects of the bot by modifying the config.py file. Here are some configuration options:

- TOKEN: Your Discord bot token.
- IMAGES: The URL of the directory containing the images used in the bot
- MAX_BET: The maximum amount a user can bet on a slot machine game.
- DAILY_REWARD: The amount of money awarded to users for claiming their daily reward.
- MAX_TRANSACTIONS: The maximum amount of money a user can send or receive in a single transaction.
- SLOT_MACHINE_PAYOUTS: The payouts for each slot machine reel combination.
- ACHIEVEMENTS: The list of achievements that users can earn.

## Aditional Information

### Contributing

**Contributions are welcome! If you find any bugs or have any suggestions for improvements, please feel free to open an issue or submit a pull request.**

### License

**This project is licensed under the MIT License.**

### Acknowledgments

**This bot was inspired by various casino-related Discord bots and tutorials found online.**



[![image](https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white)](#)