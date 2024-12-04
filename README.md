# Discord Casino Bot

### A Discord bot that provides various casino-related features, such as slot machines, betting, and user management.

![image](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)
![image](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=Raspberry%20Pi&logoColor=white)
![image](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#white)
![image](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)
![image](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![image](https://img.shields.io/badge/pypi-3775A9?style=for-the-badge&logo=pypi&logoColor=white)


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
