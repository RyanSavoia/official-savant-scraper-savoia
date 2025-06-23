import pybaseballstats
from pybaseballstats.statcast_leaderboards import (
    statcast_pitch_arsenals_leaderboard,
    statcast_pitch_arsenal_stats_leaderboard
)
import polars as pl
import json
import re
import requests
from datetime import datetime

# REPLACE THIS WITH YOUR ACTUAL API ENDPOINT
API_URL = "https://your-api-endpoint.com/matchups"

def fetch_matchups():
    """Fetch today's matchups from your API"""
    try:
        # For testing, use the sample data
        # In production, uncomment the next line and comment out the return statement
        # response = requests.get(API_URL)
        # return response.json()
        
        # Sample data for testing
        return [{"away_team":"TEX","home_team":"BAL","away_pitcher":"(L) Patrick Corbin","home_pitcher":"Trevor Rogers (L)","away_lineup":["1   Sam Haggerty (S) CF","2   Wyatt Langford (R) LF","3   Corey Seager (L) SS","4   Marcus Semien (R) 2B","5   Adolis García (R) RF","6   Jonah Heim (S) C","7   Josh Jung (R) 3B","8   Kyle Higashioka (R) DH","9   Ezequiel Duran (R) 1B"],"home_lineup":["2B (L) Jackson Holliday   1","3B (R) Jordan Westburg   2","SS (L) Gunnar Henderson   3","LF (R) Ramón Laureano   4","C (R) Gary Sánchez   5","CF (L) Cedric Mullins   6","1B (R) Coby Mayo   7","DH (S) Dylan Carlson   8","RF (L) Colton Cowser   9"]}]
    except Exception as e:
        print(f"Error fetching matchups: {e}")
        return []

# [Rest of your parsing and processing code stays the same]
def parse_pitcher_name(pitcher_string):
    """Extract pitcher name from formats like "(L) Patrick Corbin" or "Trevor Rogers (L)" """
    cleaned = re.sub(r"\([LRS]\)", "", pitcher_string).strip()
    parts = cleaned.split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {" ".join(parts[:-1])}"
    return cleaned

# ... [Include all the other functions from the working scraper]

if __name__ == "__main__":
    print(f"Baseball Scraper running at {datetime.now()}")
    
    # Fetch matchups
    api_data = fetch_matchups()
    if not api_data:
        print("No matchups found")
        exit()
    
    print(f"Processing {len(api_data)} games...")
    
    # [Rest of your processing code]
    # Load data and process matchups...
