from xmlrpc.client import boolean
import requests
import json
import os
import time


# Environment variables for Client ID, Client Secret, and Refresh Token
CLIENT_ID = ""
CLIENT_SECRET = ""
REFRESH_TOKEN = ""
ACCESS_TOKEN = ""

# Function to refresh the access token using the refresh token
def refresh_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, data=payload)
    response_data = response.json()

    if response.status_code == 200 and "access_token" in response_data:
        new_access_token = response_data['access_token']
        # Save or update the new access token in a secure location
        return new_access_token
    else:
        raise Exception("Failed to refresh access token")

def post_to_discord(webhook_url, content):
    payload = {
        "content": content
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 204:
        print("Message sent to Discord successfully!")
    else:
        print("Failed to send message to Discord.")
        
# Function to check streamer status
def check_streamer(streamer_name, new_access_token):
    twitch_api_url = f"https://api.twitch.tv/helix/streams?user_login={streamer_name}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {new_access_token}"
    }
    
    response = requests.get(twitch_api_url, headers=headers)
    data = response.json()

    # Check if the access token is expired or invalid
    if response.status_code == 401:
        # Refresh the access token
        access_token = refresh_access_token()
        # Retry the request with the new access token
        return check_streamer(streamer_name, access_token)

    if "data" in data and len(data["data"]) > 0:
        print("Streamer is live!")
        return True
    else:
        # Streamer is not live
        print("Streamer is NOT live!")
        return False

# Example usage
try:
    streamer_name = "enter streamer name here"
    access_token = refresh_access_token()  # Get a valid access token
    check_streamer(streamer_name, access_token)  # Replace with actual streamer name
    discord_webhook = "" #Discord Webhook
    while True:
        if check_streamer(streamer_name, access_token):
            message = f"Streamer is live: check streamer out here:  \nhttps://twitch.tv/{streamer_name}"
            post_to_discord(discord_webhook, message)
            time.sleep(3600*4)  # Begin to check again in 4 hours
        
        time.sleep(60)  # Check every 60 sec
except Exception as e:
    print(f"Error: {e}")
