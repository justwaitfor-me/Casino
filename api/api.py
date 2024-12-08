from flask import Flask, request, jsonify
from waitress import serve
from flask_cors import CORS  # Import CORS for handling cross-origin requests
import threading
import asyncio

from scripts.functions import get_data

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Global variable to hold the bot instance
api_bot = None


# Endpoint to send a message via Discord bot
@app.route("/send-message", methods=["POST"])
def send_message():
    # Read data from the incoming JSON request
    data = request.json
    channel_id = data.get("channel_id")
    message = data.get("message")

    # Validate input
    if not channel_id or not message:
        return jsonify(
            {"status": "error", "message": "Missing channel_id or message"}
        ), 400

    # Use bot reference to send the message (provided during API initialization)
    try:
        channel = api_bot.get_channel(int(channel_id))
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(message), api_bot.loop)
            return jsonify({"status": "success", "message": "Message sent"}), 200
        else:
            return jsonify({"status": "error", "message": "Channel not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/get-data", methods=["GET"])
def get_data_route():
    try:
        # Get the key from query parameters
        key = request.args.get("key")

        # Validate the key
        if not key:
            return jsonify(
                {"status": "error", "message": "Missing 'key' parameter"}
            ), 400

        # Attempt to retrieve the data using the key
        data_dict = get_data()

        # Check if the key exists key the data
        if str(key) not in data_dict:
            return jsonify(
                {"status": "error", "message": f"Data not found for key: {key}"}
            ), 404

        # Return the data associated with the given key
        return jsonify({"status": "success", "data": data_dict[str(key)]}), 200

    except Exception as e:
        # Catch all unexpected errors and log them
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500


# Function to start the Flask API using Waitress in a separate thread
def run_api(bot):
    """
    Starts the Flask API using Waitress in a separate thread.
    :param bot: The Discord bot instance
    """
    global api_bot
    api_bot = bot  # Link the bot instance to the API

    # Start the Flask app using Waitress in a separate thread
    def start_server():
        serve(app, host="0.0.0.0", port=5000)

        # Log the Flask app startup
        app.logger.info("Flask app started on http://0.0.0.0:5000")

    thread = threading.Thread(target=start_server)
    thread.daemon = True  # Ensure the thread closes when the main program exits
    thread.start()
