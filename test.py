import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

api_key = ""
player_tag = "%23JUQLRLJ"


class RoyaleAPI:
    BASE_URL = "https://api.clashroyale.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        self.last_request_time = None
        self.min_request_interval = 0.5 

    def _wait_for_rate_limit(self):
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def get_player_info(self, player_tag: str) -> Optional[Dict[str, Any]]:
        # Remove any existing # or %23 and add the proper format
        clean_tag = player_tag.strip('#').strip('%23')
        url = f"{self.BASE_URL}/players/%23{clean_tag}"
        
        self._wait_for_rate_limit()
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                retry_after = int(e.response.headers.get('retry-after', 60))
                print(f"Rate limit reached. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.get_player_info(player_tag)  # Retry the request
            elif e.response.status_code == 403:
                print("Authentication error. Please check your API key.")
            elif e.response.status_code == 404:
                print(f"Player tag {player_tag} not found.")
            else:
                print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
        return None

def display_wins(wins: int, max_display: int = 20):
    """Display wins with a trophy animation, limited to max_display trophies."""
    print(f"\nTotal Wins: {wins} 🏆")
    
    if wins > max_display:
        print(f"Displaying first {max_display} trophies...")
        
    for i in range(min(wins, max_display)):
        print(f"🏆 Win #{i + 1}")
        time.sleep(0.05)
        
    if wins > max_display:
        print(f"... and {wins - max_display} more wins! 🎮")

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv('CLASH_ROYALE_API_KEY')
    if not api_key:
        print("Error: API key not found. Please set CLASH_ROYALE_API_KEY environment variable.")
        return

    # Initialize API client
    api = RoyaleAPI(api_key)
    player_tag = "JUQLRLJ"
    
    try:
        player_data = api.get_player_info(player_tag)
        if player_data:
            wins = player_data.get('wins', 0)
            display_wins(wins)
            
            # Display additional player info
            print(f"\nPlayer Name: {player_data.get('name')}")
            print(f"Trophies: {player_data.get('trophies')}")
            print(f"Level: {player_data.get('expLevel')}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")

if __name__ == "__main__":
    main()