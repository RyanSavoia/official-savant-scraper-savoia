import pybaseballstats
from pybaseballstats.statcast_leaderboards import (
    statcast_pitch_arsenals_leaderboard,
    statcast_pitch_arsenal_stats_leaderboard
)
import polars as pl
import json
import re
import requests
import os
from datetime import datetime

# Your actual API endpoint
API_URL = "https://mlb-matchup-analysis-api.onrender.com/"
SEASON_YEAR = 2025  # Current season

# Webhook URL - set this as environment variable on Render
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

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
    # Remove numbers from start/end
    cleaned = re.sub(r'^\d+\s+', '', lineup_string)
    cleaned = re.sub(r'\s+\d+$', '', cleaned)
    
    # Remove handedness indicators (L), (R), (S)
    cleaned = re.sub(r'\([LRS]\)', '', cleaned)
    
    # Remove position abbreviations (must be 1-2 uppercase letters at word boundaries)
    # Common positions: C, 1B, 2B, 3B, SS, LF, CF, RF, DH
    position_pattern = r'\b(C|1B|2B|3B|SS|LF|CF|RF|DH)\b'
    cleaned = re.sub(position_pattern, '', cleaned)
    
    # Clean up extra spaces
    name = ' '.join(cleaned.split()).strip()
    
    # Split name parts
    parts = name.split()
    
    # Handle names properly
    if len(parts) >= 2:
        # Handle cases like "Ronald Acuña Jr." - Jr. is part of last name
        if parts[-1].lower() in ['jr', 'jr.', 'sr', 'sr.', 'ii', 'iii']:
            last_name = f"{parts[-2]} {parts[-1]}"
            first_name = ' '.join(parts[:-2])
        else:
            last_name = parts[-1]
            first_name = ' '.join(parts[:-1])
        
        return f"{last_name}, {first_name}"
    
    return name

def get_pitcher_arsenal(pitcher_name, all_arsenals):
    last_name = pitcher_name.split(',')[0].lower()
    pitcher_data = all_arsenals.filter(
        pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name)
    )
    
    if len(pitcher_data) == 0:
        print(f"  ⚠️  No arsenal data found for: {pitcher_name}")
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
    """Get batter's stats against specific pitch types - with better error handling"""
    last_name = batter_name.split(',')[0].lower()
    
    # First try exact last name match
    batter_data = all_batter_stats.filter(
        pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name)
    )
    
    if len(batter_data) == 0:
        # Try alternative spellings or partial matches
        # For names like "García" try without accent
        last_name_no_accent = last_name.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        if last_name_no_accent != last_name:
            batter_data = all_batter_stats.filter(
                pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name_no_accent)
            )
    
    if len(batter_data) > 0:
        # Filter by pitch types
        batter_pitch_data = batter_data.filter(pl.col('pitch_type').is_in(pitch_types))
        
        if len(batter_pitch_data) > 0:
            return batter_pitch_data.select(['pitch_type', 'ba', 'est_ba', 'slg', 
                                           'hard_hit_percent']).to_dicts()
        else:
            # Player exists but no data against these pitch types
            print(f"    ⚠️  {batter_name} found but no data vs pitch types: {pitch_types}")
            return None
    else:
        print(f"    ⚠️  No batting data found for: {batter_name}")
        return None

def send_to_webhook(data, webhook_url):
    """Send data to webhook"""
    if not webhook_url:
        print("Warning: No webhook URL configured")
        return False
    
    try:
        print(f"Sending data to webhook: {webhook_url}")
        response = requests.post(webhook_url, json=data, timeout=30)
        response.raise_for_status()
        print(f"Successfully sent data to webhook. Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"Error sending to webhook: {e}")
        return False

if __name__ == "__main__":
    print(f"Baseball Scraper running at {datetime.now()}")
    
    # Fetch matchups from API
    api_data = fetch_matchups()
    if not api_data:
        print("No matchups found")
        exit()
    
    print(f"Processing {len(api_data)} games...")
    
    # Load Statcast data for current season
    print(f"Loading {SEASON_YEAR} MLB data from Baseball Savant...")
    all_arsenals = statcast_pitch_arsenals_leaderboard(SEASON_YEAR)
    all_batter_stats = statcast_pitch_arsenal_stats_leaderboard(SEASON_YEAR)
    
    print(f"Loaded {len(all_arsenals)} pitchers and {len(all_batter_stats)} batter records")
    
    # Process matchups
    all_reports = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, matchup in enumerate(api_data):
        print(f"\n{'='*50}")
        print(f"Processing Game {i+1}: {matchup['away_team']} @ {matchup['home_team']}")
        
        # Parse pitcher names
        away_pitcher = parse_pitcher_name(matchup['away_pitcher'])
        home_pitcher = parse_pitcher_name(matchup['home_pitcher'])
        
        print(f"  Away: {matchup['away_pitcher']} → {away_pitcher}")
        print(f"  Home: {matchup['home_pitcher']} → {home_pitcher}")
        
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
                    'original_name': matchup['away_pitcher'],
                    'arsenal': away_arsenal
                },
                'home': {
                    'name': home_pitcher,
                    'original_name': matchup['home_pitcher'],
                    'arsenal': home_arsenal
                }
            },
            'key_matchups': [],
            'missing_data': []  # Track what's missing
        }
        
        # Process away team batters vs home pitcher
        if home_arsenal:
            print(f"\n  Checking {matchup['away_team']} batters vs {home_pitcher}:")
            for j, batter_string in enumerate(matchup['away_lineup'][:3]):
                batter_name = parse_batter_name(batter_string)
                print(f"    Batter {j+1}: {batter_string} → {batter_name}")
                stats = get_batter_vs_pitches(batter_name, list(home_arsenal.keys()), all_batter_stats)
                
                if stats and any(s['ba'] is not None for s in stats):
                    valid_stats = [s for s in stats if s['ba'] is not None]
                    avg_ba = sum(s['ba'] for s in valid_stats) / len(valid_stats)
                    game_report['key_matchups'].append({
                        'batter': batter_name,
                        'team': matchup['away_team'],
                        'vs_pitcher': home_pitcher,
                        'avg_ba': avg_ba,
                        'pitch_stats': stats
                    })
                    print(f"      ✓ Found data: {avg_ba:.3f} AVG")
                else:
                    game_report['missing_data'].append(f"{batter_name} vs {home_pitcher}")
        else:
            print(f"  ⚠️  No arsenal for {home_pitcher}, skipping {matchup['away_team']} batters")
        
        # Process home team batters vs away pitcher
        if away_arsenal:
            print(f"\n  Checking {matchup['home_team']} batters vs {away_pitcher}:")
            for j, batter_string in enumerate(matchup['home_lineup'][:3]):
                batter_name = parse_batter_name(batter_string)
                print(f"    Batter {j+1}: {batter_string} → {batter_name}")
                stats = get_batter_vs_pitches(batter_name, list(away_arsenal.keys()), all_batter_stats)
                
                if stats and any(s['ba'] is not None for s in stats):
                    valid_stats = [s for s in stats if s['ba'] is not None]
                    avg_ba = sum(s['ba'] for s in valid_stats) / len(valid_stats)
                    game_report['key_matchups'].append({
                        'batter': batter_name,
                        'team': matchup['home_team'],
                        'vs_pitcher': away_pitcher,
                        'avg_ba': avg_ba,
                        'pitch_stats': stats
                    })
                    print(f"      ✓ Found data: {avg_ba:.3f} AVG")
                else:
                    game_report['missing_data'].append(f"{batter_name} vs {away_pitcher}")
        else:
            print(f"  ⚠️  No arsenal for {away_pitcher}, skipping {matchup['home_team']} batters")
        
        all_reports.append(game_report)
    
    # Create final payload
    final_data = {
        'timestamp': timestamp,
        'date': datetime.now().strftime("%Y-%m-%d"),
        'games_processed': len(all_reports),
        'reports': all_reports
    }
    
    # Save locally for backup
    output_filename = f"mlb_matchups_{timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(final_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Scraping complete! Processed {len(all_reports)} games")
    print(f"Report saved to: {output_filename}")
    
    # Send to webhook if configured
    if WEBHOOK_URL:
        print(f"\nWebhook URL configured: {WEBHOOK_URL}")
        success = send_to_webhook(final_data, WEBHOOK_URL)
        if success:
            print("Data successfully sent to webhook!")
        else:
            print("Failed to send data to webhook")
    else:
        print("\nNo webhook URL configured - data only saved locally")
        print("Set WEBHOOK_URL environment variable to enable webhook")
    
    print(f"{'='*60}")
    
    # Print summary
    print("\nSummary:")
    total_matchups = sum(len(r['key_matchups']) for r in all_reports)
    total_missing = sum(len(r['missing_data']) for r in all_reports)
    print(f"  Found {total_matchups} batter vs pitcher matchups")
    print(f"  Missing data for {total_missing} potential matchups")
    
    # Show games with no data
    for report in all_reports:
        if not report['key_matchups']:
            print(f"\n  ⚠️  No matchups found for {report['matchup']}")
            if report['missing_data']:
                print(f"     Missing: {', '.join(report['missing_data'][:3])}")
