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
    
    # Remove position abbreviations
    position_pattern = r'\b(C|1B|2B|3B|SS|LF|CF|RF|DH)\b'
    cleaned = re.sub(position_pattern, '', cleaned)
    
    # Clean up extra spaces
    name = ' '.join(cleaned.split()).strip()
    
    # Split name parts
    parts = name.split()
    
    if len(parts) >= 2:
        if parts[-1].lower() in ['jr', 'jr.', 'sr', 'sr.', 'ii', 'iii']:
            last_name = f"{parts[-2]} {parts[-1]}"
            first_name = ' '.join(parts[:-2])
        else:
            last_name = parts[-1]
            first_name = ' '.join(parts[:-1])
        
        return f"{last_name}, {first_name}"
    
    return name

def get_pitcher_arsenal_with_usage(pitcher_name, all_arsenals):
    """Get pitcher's arsenal with usage rates"""
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
        'st': 'Sweeper', 'fs': 'Splitter', 'kn': 'Knuckleball',
        'sv': 'Slurve'
    }
    
    arsenal = {}
    total_usage = 0.0
    
    # First pass: collect all pitches with usage > 0
    for abbr, full_name in pitch_types.items():
        speed_col = f'{abbr}_avg_speed'
        usage_col = f'{abbr}_usage_rate'
        
        if speed_col in pitcher_row and pitcher_row[speed_col] is not None:
            usage = pitcher_row.get(usage_col, 0.0) or 0.0
            if usage > 0:
                arsenal[abbr.upper()] = {
                    'name': full_name,
                    'avg_speed': pitcher_row[speed_col],
                    'usage_rate': usage / 100.0  # Convert to decimal
                }
                total_usage += usage
    
    # Normalize usage rates to ensure they sum to 1.0
    if total_usage > 0:
        for pitch in arsenal.values():
            pitch['usage_rate'] = pitch['usage_rate'] * (100.0 / total_usage)
    
    return arsenal

def calculate_weighted_metrics(batter_stats, pitcher_arsenal):
    """Calculate weighted batting metrics based on pitch usage"""
    if not batter_stats or not pitcher_arsenal:
        return None
    
    # Initialize weighted sums
    weighted_ba = 0.0
    weighted_whiff = 0.0
    weighted_k_rate = 0.0
    weighted_hard_hit = 0.0
    total_weight = 0.0
    pitch_performances = []
    
    for stat in batter_stats:
        pitch_type = stat['pitch_type']
        
        if pitch_type in pitcher_arsenal:
            usage_rate = pitcher_arsenal[pitch_type]['usage_rate']
            
            # Get metrics (handle None values)
            ba = stat.get('ba', 0) if stat.get('ba') is not None else 0
            whiff = stat.get('whiff_percent', 0) if stat.get('whiff_percent') is not None else 0
            k_rate = stat.get('k_percent', 0) if stat.get('k_percent') is not None else 0
            hard_hit = stat.get('hard_hit_percent', 0) if stat.get('hard_hit_percent') is not None else 0
            
            # Calculate weighted values
            weighted_ba += ba * usage_rate
            weighted_whiff += whiff * usage_rate
            weighted_k_rate += k_rate * usage_rate
            weighted_hard_hit += hard_hit * usage_rate
            total_weight += usage_rate
            
            pitch_performances.append({
                'pitch_type': pitch_type,
                'pitch_name': pitcher_arsenal[pitch_type]['name'],
                'ba': ba,
                'whiff_percent': whiff,
                'k_percent': k_rate,
                'hard_hit_percent': hard_hit,
                'usage_rate': usage_rate,
                'weighted_contribution': ba * usage_rate
            })
    
    if total_weight > 0:
        # Calculate final weighted averages
        result = {
            'weighted_ba': weighted_ba / total_weight,
            'weighted_whiff': weighted_whiff / total_weight,
            'weighted_k_rate': weighted_k_rate / total_weight,
            'weighted_hard_hit': weighted_hard_hit / total_weight,
            'pitch_performances': pitch_performances,
            'coverage': total_weight
        }
        
        # Calculate a composite matchup score
        matchup_score = calculate_matchup_score(result)
        result['matchup_score'] = matchup_score
        
        return result
    
    return None

def calculate_matchup_score(metrics):
    """Calculate a composite matchup score (0-100, higher is better for batter)"""
    ba = metrics['weighted_ba']
    whiff = metrics['weighted_whiff'] / 100
    k_rate = metrics['weighted_k_rate'] / 100
    hard_hit = metrics['weighted_hard_hit'] / 100
    
    # Normalize each component to 0-100 scale
    ba_score = max(0, min(100, (ba - 0.200) / 0.150 * 100))
    whiff_score = max(0, min(100, (0.40 - whiff) / 0.30 * 100))
    k_score = max(0, min(100, (0.35 - k_rate) / 0.25 * 100))
    hard_hit_score = max(0, min(100, (hard_hit - 0.25) / 0.25 * 100))
    
    # Calculate weighted composite
    composite = (
        ba_score * 0.35 +
        whiff_score * 0.25 +
        k_score * 0.25 +
        hard_hit_score * 0.15
    )
    
    return round(composite, 1)

def get_batter_vs_pitches(batter_name, pitch_types, all_batter_stats):
    """Get batter's stats against specific pitch types"""
    last_name = batter_name.split(',')[0].lower()
    
    # First try exact last name match
    batter_data = all_batter_stats.filter(
        pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name)
    )
    
    if len(batter_data) == 0:
        # Try without accents
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
                                           'hard_hit_percent', 'whiff_percent', 'k_percent']).to_dicts()
    
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
    print(f"Loaded {len(all_arsenals)} pitchers")
    
    # Use min_pa=1 to get all batters
    all_batter_stats = statcast_pitch_arsenal_stats_leaderboard(SEASON_YEAR, min_pa=1)
    print(f"Loaded {len(all_batter_stats)} batter records")
    
    # Process matchups
    all_reports = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, matchup in enumerate(api_data):
        print(f"\nProcessing Game {i+1}: {matchup['away_team']} @ {matchup['home_team']}")
        
        # Parse pitcher names
        away_pitcher = parse_pitcher_name(matchup['away_pitcher'])
        home_pitcher = parse_pitcher_name(matchup['home_pitcher'])
        
        # Get arsenals with usage rates
        away_arsenal = get_pitcher_arsenal_with_usage(away_pitcher, all_arsenals)
        home_arsenal = get_pitcher_arsenal_with_usage(home_pitcher, all_arsenals)
        
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
            'batters_found': 0,
            'batters_missing': 0
        }
        
        # Process away team batters vs home pitcher
        if home_arsenal:
            for batter_string in matchup['away_lineup']:
                batter_name = parse_batter_name(batter_string)
                stats = get_batter_vs_pitches(batter_name, list(home_arsenal.keys()), all_batter_stats)
                
                if stats:
                    # Calculate weighted metrics
                    weighted_result = calculate_weighted_metrics(stats, home_arsenal)
                    
                    if weighted_result:
                        game_report['key_matchups'].append({
                            'batter': batter_name,
                            'team': matchup['away_team'],
                            'vs_pitcher': home_pitcher,
                            'weighted_avg_ba': round(weighted_result['weighted_ba'], 3),
                            'weighted_whiff': round(weighted_result['weighted_whiff'], 1),
                            'weighted_k_rate': round(weighted_result['weighted_k_rate'], 1),
                            'weighted_hard_hit': round(weighted_result['weighted_hard_hit'], 1),
                            'matchup_score': weighted_result['matchup_score'],
                            'arsenal_coverage': round(weighted_result['coverage'], 2),
                            'pitch_breakdown': weighted_result['pitch_performances'],
                            'pitch_stats': stats
                        })
                        game_report['batters_found'] += 1
                    else:
                        game_report['batters_missing'] += 1
                else:
                    game_report['batters_missing'] += 1
        
        # Process home team batters vs away pitcher
        if away_arsenal:
            for batter_string in matchup['home_lineup']:
                batter_name = parse_batter_name(batter_string)
                stats = get_batter_vs_pitches(batter_name, list(away_arsenal.keys()), all_batter_stats)
                
                if stats:
                    # Calculate weighted metrics
                    weighted_result = calculate_weighted_metrics(stats, away_arsenal)
                    
                    if weighted_result:
                        game_report['key_matchups'].append({
                            'batter': batter_name,
                            'team': matchup['home_team'],
                            'vs_pitcher': away_pitcher,
                            'weighted_avg_ba': round(weighted_result['weighted_ba'], 3),
                            'weighted_whiff': round(weighted_result['weighted_whiff'], 1),
                            'weighted_k_rate': round(weighted_result['weighted_k_rate'], 1),
                            'weighted_hard_hit': round(weighted_result['weighted_hard_hit'], 1),
                            'matchup_score': weighted_result['matchup_score'],
                            'arsenal_coverage': round(weighted_result['coverage'], 2),
                            'pitch_breakdown': weighted_result['pitch_performances'],
                            'pitch_stats': stats
                        })
                        game_report['batters_found'] += 1
                    else:
                        game_report['batters_missing'] += 1
                else:
                    game_report['batters_missing'] += 1
        
        print(f"  Found: {game_report['batters_found']}/18 batters")
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
    
    # Send to webhook if configured
    if WEBHOOK_URL:
        success = send_to_webhook(final_data, WEBHOOK_URL)
        if success:
            print("Data successfully sent to webhook!")
    else:
        print("No webhook URL configured - data only saved locally")
    
    print(f"{'='*60}")
    
    # Print summary with new metrics
    total_found = sum(r['batters_found'] for r in all_reports)
    total_possible = len(all_reports) * 18
    print(f"\nOverall Coverage: {total_found}/{total_possible} batters ({(total_found/total_possible)*100:.1f}%)")
    
    # Show best/worst matchups
    if all_reports:
        all_matchups = []
        for report in all_reports:
            all_matchups.extend(report['key_matchups'])
        
        if all_matchups:
            sorted_matchups = sorted(all_matchups, key=lambda x: x['matchup_score'], reverse=True)
            
            print("\n=== TOP 5 MATCHUPS FOR BATTERS ===")
            for m in sorted_matchups[:5]:
                print(f"{m['batter']} vs {m['vs_pitcher']}: {m['matchup_score']} score")
                print(f"  BA: {m['weighted_avg_ba']:.3f}, Whiff: {m['weighted_whiff']:.1f}%, K: {m['weighted_k_rate']:.1f}%")
            
            print("\n=== WORST 5 MATCHUPS FOR BATTERS ===")
            for m in sorted_matchups[-5:]:
                print(f"{m['batter']} vs {m['vs_pitcher']}: {m['matchup_score']} score")
                print(f"  BA: {m['weighted_avg_ba']:.3f}, Whiff: {m['weighted_whiff']:.1f}%, K: {m['weighted_k_rate']:.1f}%")
