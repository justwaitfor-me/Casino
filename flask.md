# Flask API Setup with Waitress, CORS, and PHP Integration

This guide walks through setting up a Flask API with Waitress, enabling CORS for cross-origin requests, and using PHP to send requests to the Flask API.

---

## **1. Flask API Setup**

### Install Required Packages

Install the necessary packages for Flask, Waitress, and CORS:

```bash
pip install flask waitress flask-cors
```

### Create `api.py` for Flask API

Create the Flask API in a file named `api.py`:

```python
from flask import Flask, request, jsonify
from waitress import serve
from flask_cors import CORS  # Enable CORS
import threading
import asyncio

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

api_bot = None  # Global bot instance

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    channel_id = data.get('channel_id')
    message = data.get('message')

    if not channel_id or not message:
        return jsonify({'status': 'error', 'message': 'Missing channel_id or message'}), 400

    try:
        channel = api_bot.get_channel(int(channel_id))
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(message), api_bot.loop)
            return jsonify({'status': 'success', 'message': 'Message sent'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Channel not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_api(bot):
    global api_bot
    api_bot = bot  # Link bot instance
    def start_server():
        serve(app, host="0.0.0.0", port=5000)
    thread = threading.Thread(target=start_server)
    thread.daemon = True  # Close thread with main program
    thread.start()
```

---

## **2. Run Flask API with Waitress**

In your **`main.py`**, integrate the Flask API:

```python
import discord
from discord.ext import commands
from scripts.api import run_api

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")
    run_api(bot)  # Start Flask API

bot.run("YOUR_BOT_TOKEN")
```

### Run the bot and API

```bash
python main.py
```

API will be available at `http://<raspberry_pi_ip>:5000`.

---

## **3. Enable CORS**

### Why Enable CORS?

CORS allows the Flask API to accept requests from different domains (e.g., from a PHP client).

In `api.py`, CORS is enabled with:

```python
CORS(app)  # Allow requests from any origin
```

### Restrict Origins (Optional)

To allow only specific domains:

```python
CORS(app, origins=["http://your-php-server.com"])
```

---

## **4. PHP Integration**

### PHP Script to Send Messages

Create a PHP script `send_message.php` to send messages to your Flask API:

```php
<?php

$api_url = 'http://<raspberry_pi_ip>:5000/send-message';  // Flask API URL
$channel_id = '123456789012345678';  // Discord Channel ID
$message = 'Hello from PHP!';

$data = array('channel_id' => $channel_id, 'message' => $message);

$ch = curl_init($api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

$response = curl_exec($ch);
if(curl_errno($ch)) {
    echo 'Error:' . curl_error($ch);
} else {
    echo 'Response: ' . $response;
}
curl_close($ch);
?>
```

### How to Test

1. Replace `<raspberry_pi_ip>` with your server's IP.
2. Run the PHP script in your browser or command line:

   ```bash
   php send_message.php
   ```

### Expected Response

```json
{
    "status": "success",
    "message": "Message sent"
}
```

---

## **5. Troubleshooting**

- **CORS**: Ensure your Flask server allows the correct origins using the `CORS(app)` configuration.
- **Port Issues**: Ensure that the Flask API is accessible and port 5000 is open.
- **Bot Permissions**: Ensure the Discord bot has permission to send messages to the specified channel.
