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

# Your actual API endpoint
API_URL = "https://mlb-matchup-analysis-api.onrender.com/"

def fetch_matchups():
    """Fetch today's matchups from your API"""
    try:
        print(f"Fetching matchups from {API_URL}")
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully fetched {len(data)} matchups")
        return data
    except Exception as e:
        print(f"Error fetching matchups: {e}")
        return []

def parse_pitcher_name(pitcher_string):
    """Extract pitcher name from formats like '(L) Patrick Corbin' or 'Trevor Rogers (L)'"""
    cleaned = re.sub(r'\([LRS]\)', '', pitcher_string).strip()
    parts = cleaned.split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return cleaned

def parse_batter_name(lineup_string):
    """Extract batter name from various lineup formats"""
    if re.match(r'^[A-Z0-9]{1,2}\s+\([LRS]\)', lineup_string):
        cleaned = re.sub(r'^[A-Z0-9]{1,2}\s+\([LRS]\)\s+', '', lineup_string)
        cleaned = re.sub(r'\s+\d+$', '', cleaned)
    else:
        cleaned = re.sub(r'^\d+\s+', '', lineup_string)
        cleaned = re.sub(r'\s*\([LRS]\)\s*[A-Z0-9]{1,2}$', '', cleaned)
    
    name = cleaned.strip()
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name

def get_pitcher_arsenal(pitcher_name, all_arsenals):
    last_name = pitcher_name.split(',')[0].lower()
    pitcher_data = all_arsenals.filter(
        pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name)
    )
    
    if len(pitcher_data) == 0:
        return None
    
    pitcher_row = pitcher_data.row(0, named=True)
    
    pitch_types = {
        'ff': 'Four-Seam', 'si': 'Sinker', 'fc': 'Cutter',
        'sl': 'Slider', 'ch': 'Changeup', 'cu': 'Curveball',
        'st': 'Sweeper', 'fs': 'Splitter', 'kn': 'Knuckleball'
    }
    
    arsenal = {}
    for abbr, full_name in pitch_types.items():
        speed_col = f'{abbr}_avg_speed'
        if speed_col in pitcher_row and pitcher_row[speed_col] is not None:
            arsenal[abbr.upper()] = {
                'name': full_name,
                'avg_speed': pitcher_row[speed_col]
            }
    
    return arsenal

def get_batter_vs_pitches(batter_name, pitch_types, all_batter_stats):
    last_name = batter_name.split(',')[0].lower()
    batter_data = all_batter_stats.filter(
        pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name)
    )
    
    if len(batter_data) > 0:
        batter_data = batter_data.filter(pl.col('pitch_type').is_in(pitch_types))
        
        if len(batter_data) > 0:
            return batter_data.select(['pitch_type', 'ba', 'est_ba', 'slg', 
                                     'hard_hit_percent']).to_dicts()
    
    return None

if __name__ == "__main__":
    print(f"Baseball Scraper running at {datetime.now()}")
    
    # Fetch matchups from API
    api_data = fetch_matchups()
    if not api_data:
        print("No matchups found")
        exit()
    
    print(f"Processing {len(api_data)} games...")
    
    # Load Statcast data
    print("Loading 2024 MLB data from Baseball Savant...")
    all_arsenals = statcast_pitch_arsenals_leaderboard(2024)
    all_batter_stats = statcast_pitch_arsenal_stats_leaderboard(2024)
    
    # Process matchups
    all_reports = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, matchup in enumerate(api_data):
        print(f"\nProcessing Game {i+1}: {matchup['away_team']} @ {matchup['home_team']}")
        
        # Parse pitcher names
        away_pitcher = parse_pitcher_name(matchup['away_pitcher'])
        home_pitcher = parse_pitcher_name(matchup['home_pitcher'])
        
        # Get arsenals
        away_arsenal = get_pitcher_arsenal(away_pitcher, all_arsenals)
        home_arsenal = get_pitcher_arsenal(home_pitcher, all_arsenals)
        
        # Build report
        game_report = {
            'game_date': datetime.now().strftime("%Y-%m-%d"),
            'matchup': f"{matchup['away_team']} @ {matchup['home_team']}",
            'pitchers': {
                'away': {
                    'name': away_pitcher,
                    'arsenal': away_arsenal
                },
                'home': {
                    'name': home_pitcher,
                    'arsenal': home_arsenal
                }
            },
            'key_matchups': []
        }
        
        # Get key batter matchups (top 3 from each team)
        if home_arsenal:
            for batter_string in matchup['away_lineup'][:3]:
                batter_name = parse_batter_name(batter_string)
                stats = get_batter_vs_pitches(batter_name, list(home_arsenal.keys()), all_batter_stats)
                
                if stats:
                    avg_ba = sum(s['ba'] for s in stats if s['ba']) / len([s for s in stats if s['ba']])
                    game_report['key_matchups'].append({
                        'batter': batter_name,
                        'team': matchup['away_team'],
                        'vs_pitcher': home_pitcher,
                        'avg_ba': avg_ba,
                        'pitch_stats': stats
                    })
        
        if away_arsenal:
            for batter_string in matchup['home_lineup'][:3]:
                batter_name = parse_batter_name(batter_string)
                stats = get_batter_vs_pitches(batter_name, list(away_arsenal.keys()), all_batter_stats)
                
                if stats:
                    avg_ba = sum(s['ba'] for s in stats if s['ba']) / len([s for s in stats if s['ba']])
                    game_report['key_matchups'].append({
                        'batter': batter_name,
                        'team': matchup['home_team'],
                        'vs_pitcher': away_pitcher,
                        'avg_ba': avg_ba,
                        'pitch_stats': stats
                    })
        
        all_reports.append(game_report)
    
    # Save reports
    output_filename = f"mlb_matchups_{timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(all_reports, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Scraping complete! Processed {len(all_reports)} games")
    print(f"Report saved to: {output_filename}")
    print(f"{'='*60}")
