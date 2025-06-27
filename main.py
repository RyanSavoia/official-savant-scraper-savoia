import tweepy
import json
import requests
from datetime import datetime
import os
import time
import schedule

# Twitter API credentials from environment variables
TWITTER_API_KEY = os.getenv('API_KEY')
TWITTER_API_SECRET = os.getenv('API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('ACCESS_SECRET')

# Your API endpoint
API_URL = "https://mlb-matchup-api-savant.onrender.com/latest"

def setup_twitter_api():
    """Setup Twitter API v2 client"""
    try:
        print("🐦 Setting up Twitter API...")
        
        # Check if all required keys are present
        required_keys = ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_SECRET']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            print(f"❌ Missing environment variables: {missing_keys}")
            return None
        
        print("🔑 All API keys found")
        
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        print("✅ Twitter API client created successfully")
        return client
    except Exception as e:
        print(f"❌ Error setting up Twitter API: {e}")
        return None

def describe_arsenal(pitcher_arsenal):
    """Describe pitcher's arsenal mix"""
    if not pitcher_arsenal:
        return "mixed arsenal", "⚾"
    
    # Get top 2 pitch types by usage
    sorted_pitches = sorted(pitcher_arsenal.items(), key=lambda x: x[1]['usage_rate'], reverse=True)
    
    if len(sorted_pitches) >= 2:
        pitch1 = sorted_pitches[0][1]['name']
        pitch2 = sorted_pitches[1][1]['name']
        
        # Categorize mix
        fastballs = ['Four-Seam', 'Sinker', 'Cutter']
        breaking = ['Slider', 'Curveball', 'Sweeper']
        offspeed = ['Changeup', 'Splitter']
        
        p1_type = 'fastball' if pitch1 in fastballs else 'breaking' if pitch1 in breaking else 'offspeed'
        p2_type = 'fastball' if pitch2 in fastballs else 'breaking' if pitch2 in breaking else 'offspeed'
        
        if p1_type == 'fastball' and p2_type == 'fastball':
            return "fastball-heavy mix", "🔥"
        elif p1_type == 'breaking' or p2_type == 'breaking':
            return "breaking-heavy mix", "🌀"
        elif p1_type == 'offspeed' or p2_type == 'offspeed':
            return "changeup-heavy mix", "🔄"
        else:
            return "mixed arsenal", "⚾"
    
    return "mixed arsenal", "⚾"

def calculate_lineup_season_k_rate(key_matchups, pitcher_name):
    """Calculate lineup's collective season K-rate"""
    pitcher_matchups = [m for m in key_matchups if m.get('vs_pitcher') == pitcher_name]
    if not pitcher_matchups:
        return 22.5
    
    # Get each batter's season K% from baseline_stats
    season_k_rates = []
    for matchup in pitcher_matchups:
        baseline = matchup.get('baseline_stats')
        if baseline and baseline.get('season_k_pct'):
            season_k_rates.append(baseline['season_k_pct'])
        else:
            season_k_rates.append(22.5)  # MLB average fallback
    
    return sum(season_k_rates) / len(season_k_rates) if season_k_rates else 22.5

def calculate_lineup_arsenal_k_rate(key_matchups, pitcher_name):
    """Calculate lineup's K-rate vs pitcher's specific arsenal"""
    pitcher_matchups = [m for m in key_matchups if m.get('vs_pitcher') == pitcher_name]
    if not pitcher_matchups:
        return 22.5
    
    # Use weighted K-rates from your API (already calculated vs pitcher's arsenal)
    arsenal_k_rates = [m.get('weighted_k_rate', 22.5) for m in pitcher_matchups]
    return sum(arsenal_k_rates) / len(arsenal_k_rates)

def get_strikeout_boost_rankings(reports, min_boost=5.0):
    """Get pitchers with K-rate boosts of 5% or more"""
    pitcher_boosts = []
    
    for game_report in reports:
        matchup = game_report.get('matchup', 'Unknown')
        key_matchups = game_report['key_matchups']
        
        for pitcher_side in ['away', 'home']:
            try:
                pitcher_data = game_report['pitchers'][pitcher_side]
                pitcher_name = pitcher_data['name']
                arsenal = pitcher_data.get('arsenal', {})
                
                if not arsenal:
                    continue
                
                # Calculate LINEUP season K% vs LINEUP arsenal K%
                lineup_season_k = calculate_lineup_season_k_rate(key_matchups, pitcher_name)
                lineup_arsenal_k = calculate_lineup_arsenal_k_rate(key_matchups, pitcher_name)
                
                # Calculate boost (how much worse the lineup performs vs this arsenal)
                k_boost = lineup_arsenal_k - lineup_season_k
                
                # Only include if boost is >= 5%
                if k_boost < min_boost:
                    continue
                
                # Get opponent team
                opponent_team = matchup.split(' @ ')[1] if pitcher_side == 'away' else matchup.split(' @ ')[0]
                
                # Format name
                display_name = pitcher_name.replace(', ', ' ').split()
                display_name = f"{display_name[1]} {display_name[0]}" if len(display_name) >= 2 else pitcher_name
                
                arsenal_desc, arsenal_emoji = describe_arsenal(arsenal)
                
                pitcher_boosts.append({
                    'pitcher': display_name,
                    'opponent': opponent_team,
                    'lineup_season_k': lineup_season_k,
                    'lineup_arsenal_k': lineup_arsenal_k,
                    'k_boost': k_boost,
                    'arsenal_desc': arsenal_desc,
                    'arsenal_emoji': arsenal_emoji
                })
                
            except Exception as e:
                print(f"Error processing pitcher: {e}")
                continue
    
    # Sort by biggest boost (positive)
    pitcher_boosts.sort(key=lambda x: x['k_boost'], reverse=True)
    return pitcher_boosts[:3]

def get_strikeout_worst_rankings(reports, min_drop=5.0):
    """Get pitchers with K-rate drops of 5% or more"""
    pitcher_boosts = []
    
    for game_report in reports:
        matchup = game_report.get('matchup', 'Unknown')
        key_matchups = game_report['key_matchups']
        
        for pitcher_side in ['away', 'home']:
            try:
                pitcher_data = game_report['pitchers'][pitcher_side]
                pitcher_name = pitcher_data['name']
                arsenal = pitcher_data.get('arsenal', {})
                
                if not arsenal:
                    continue
                
                lineup_season_k = calculate_lineup_season_k_rate(key_matchups, pitcher_name)
                lineup_arsenal_k = calculate_lineup_arsenal_k_rate(key_matchups, pitcher_name)
                k_boost = lineup_arsenal_k - lineup_season_k
                
                # Only include if drop is >= 5% (negative boost)
                if k_boost > -min_drop:
                    continue
                
                opponent_team = matchup.split(' @ ')[1] if pitcher_side == 'away' else matchup.split(' @ ')[0]
                display_name = pitcher_name.replace(', ', ' ').split()
                display_name = f"{display_name[1]} {display_name[0]}" if len(display_name) >= 2 else pitcher_name
                
                arsenal_desc, arsenal_emoji = describe_arsenal(arsenal)
                
                pitcher_boosts.append({
                    'pitcher': display_name,
                    'opponent': opponent_team,
                    'lineup_season_k': lineup_season_k,
                    'lineup_arsenal_k': lineup_arsenal_k,
                    'k_boost': k_boost,
                    'arsenal_desc': arsenal_desc,
                    'arsenal_emoji': arsenal_emoji
                })
                
            except Exception as e:
                continue
    
    # Sort by biggest drop (most negative)
    pitcher_boosts.sort(key=lambda x: x['k_boost'])
    return pitcher_boosts[:3]

def get_batting_boost_rankings(reports):
    """Get top 5 batters with best matchup scores using (boost * 0.6) + (expected_ba * 100 * 0.4)"""
    batter_boosts = []
    
    for game_report in reports:
        key_matchups = game_report['key_matchups']
        
        for matchup in key_matchups:
            try:
                baseline_stats = matchup.get('baseline_stats')
                if not baseline_stats:
                    continue
                
                batter_name = matchup.get('batter', 'Unknown')
                pitcher_name = matchup.get('vs_pitcher', 'Unknown')
                
                # Use expected BA (weighted_est_ba) instead of actual BA
                expected_ba = matchup.get('weighted_est_ba', 0.250)
                season_ba = baseline_stats.get('season_avg', 0.250)
                
                ba_boost = expected_ba - season_ba
                ba_points = int(ba_boost * 1000)  # Convert to points
                
                # Calculate matchup score: (boost * 0.6) + (expected_ba * 100 * 0.4)
                matchup_score = (ba_boost * 0.6) + (expected_ba * 100 * 0.4)
                
                # Format names
                batter_display = batter_name.replace(', ', ' ').split()
                batter_display = f"{batter_display[1]} {batter_display[0]}" if len(batter_display) >= 2 else batter_name
                
                pitcher_display = pitcher_name.replace(', ', ' ').split()
                pitcher_display = f"{pitcher_display[1]} {pitcher_display[0]}" if len(pitcher_display) >= 2 else pitcher_name
                
                # Get pitcher arsenal description
                pitcher_data = None
                for report in reports:
                    for side in ['away', 'home']:
                        if report['pitchers'][side]['name'] == pitcher_name:
                            pitcher_data = report['pitchers'][side]
                            break
                
                arsenal_desc, arsenal_emoji = "mixed arsenal", "⚾"
                if pitcher_data and pitcher_data.get('arsenal'):
                    arsenal_desc, arsenal_emoji = describe_arsenal(pitcher_data['arsenal'])
                
                batter_boosts.append({
                    'batter': batter_display,
                    'pitcher': pitcher_display,
                    'season_ba': season_ba,
                    'expected_ba': expected_ba,
                    'ba_boost': ba_boost,
                    'ba_points': ba_points,
                    'matchup_score': matchup_score,
                    'arsenal_desc': arsenal_desc,
                    'arsenal_emoji': arsenal_emoji
                })
                
            except Exception as e:
                continue
    
    # Sort by matchup score (highest first)
    batter_boosts.sort(key=lambda x: x['matchup_score'], reverse=True)
    return batter_boosts[:5]

def create_strikeout_boost_tweet(top_boosts):
    """Create strikeout watch tweet"""
    if not top_boosts:
        return None  # Don't post if no significant boosts
    
    lines = []
    lines.append("🔥 Strikeout Watch:")
    lines.append("")
    
    medals = ['🥇', '🥈', '🥉']
    
    for i, boost in enumerate(top_boosts):
        medal = medals[i] if i < len(medals) else '🏆'
        pitcher = boost['pitcher']
        arsenal = boost['arsenal_desc']
        emoji = boost['arsenal_emoji']
        opponent = boost['opponent']
        lineup_season_k = boost['lineup_season_k']
        lineup_arsenal_k = boost['lineup_arsenal_k']
        boost_val = boost['k_boost']
        
        lines.append(f"{medal} {pitcher}'s {arsenal} {emoji} {opponent}'s lineup averages {lineup_season_k:.1f}% K-rate → but vs {pitcher.split()[1].lower()}'s arsenal? {lineup_arsenal_k:.1f}% ({boost_val:+.1f}%)")
    
    lines.append("")
    lines.append("Built using pitch-type usage, swing metrics, and matchup-specific expected stats.")
    lines.append("#MLB #Strikeouts #FantasyBaseball")
    
    return '\n'.join(lines)

def create_strikeout_worst_tweet(worst_matchups):
    """Create don't chase K's tweet"""
    if not worst_matchups:
        return None  # Don't post if no significant drops
    
    lines = []
    lines.append("⚠️ Don't Chase K's Here:")
    lines.append("")
    
    for i, matchup in enumerate(worst_matchups, 1):
        pitcher = matchup['pitcher']
        arsenal = matchup['arsenal_desc']
        emoji = matchup['arsenal_emoji']
        opponent = matchup['opponent']
        lineup_season_k = matchup['lineup_season_k']
        lineup_arsenal_k = matchup['lineup_arsenal_k']
        drop_val = matchup['k_boost']
        
        lines.append(f"💩 {pitcher}'s {arsenal} {emoji} {opponent}'s lineup averages {lineup_season_k:.1f}% K-rate → but vs {pitcher.split()[1].lower()}'s arsenal? {lineup_arsenal_k:.1f}% ({drop_val:.1f}%)")
    
    lines.append("")
    lines.append("Built using pitch-type usage, swing metrics, and matchup-specific expected stats.")
    lines.append("#MLB #FantasyBaseball #DFS")
    
    return '\n'.join(lines)

def create_batting_boost_tweet(top_boosts):
    """Create hitters to target tweet"""
    if not top_boosts:
        return "🎯 No standout hitting targets today"
    
    lines = []
    lines.append("🎯 Hitters to Target:")
    lines.append("")
    
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    
    for i, boost in enumerate(top_boosts):
        medal = medals[i] if i < len(medals) else '🏆'
        batter = boost['batter']
        pitcher = boost['pitcher']
        arsenal = boost['arsenal_desc']
        emoji = boost['arsenal_emoji']
        season_ba = boost['season_ba']
        expected_ba = boost['expected_ba']
        points = boost['ba_points']
        
        lines.append(f"{medal} {batter} vs {pitcher}'s {arsenal} {emoji}")
        lines.append(f"why? --> his season average is {season_ba:.3f} → but xBA vs {pitcher.split()[1].lower()}'s arsenal? {expected_ba:.3f} ({points:+d} points)")
        lines.append("")
    
    lines.append("Built using pitch-type usage, swing metrics, and matchup-specific expected stats.")
    lines.append("#MLB #Batting #DFS #FantasyBaseball")
    
    return '\n'.join(lines)

def get_matchup_data():
    """Fetch data from your API"""
    try:
        print("🌐 Fetching matchup data from API...")
        print(f"📡 URL: {API_URL}")
        response = requests.get(API_URL, timeout=30)
        print(f"✅ Response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"📊 Data received: {len(data) if isinstance(data, list) else 'dict with keys: ' + str(list(data.keys()))}")
        return data
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def post_to_twitter(client, text, tweet_type):
    """Post tweet to Twitter"""
    try:
        if len(text) > 280:
            print(f"Tweet too long for {tweet_type} ({len(text)} chars), truncating...")
            text = text[:276] + "..."
        
        response = client.create_tweet(text=text)
        print(f"✅ Posted {tweet_type}: {response.data['id']}")
        return True
    except Exception as e:
        print(f"❌ Error posting {tweet_type}: {e}")
        return False

def run_daily_tweets():
    """Main function to generate and post daily tweets"""
    print(f"\n{'='*50}")
    print(f"Starting daily MLB tweets at {datetime.now()}")
    print(f"{'='*50}")
    
    # Setup Twitter
    client = setup_twitter_api()
    if not client:
        print("❌ Failed to setup Twitter API")
        return
    
    # Get matchup data
    data = get_matchup_data()
    if not data:
        print("❌ Failed to get matchup data")
        return
    
    # Handle both webhook format (list) and file format (dict with 'reports')
    if isinstance(data, list):
        reports = data  # Webhook sends the reports directly as a list
    else:
        reports = data.get('reports', [])  # File format has 'reports' key
        
    print(f"📊 Processing {len(reports)} games...")
    
    # Generate rankings
    print("🔥 Calculating strikeout watch rankings (5%+ boosts only)...")
    top_k_boosts = get_strikeout_boost_rankings(reports, min_boost=5.0)
    
    print("💩 Calculating don't chase K's rankings (5%+ drops only)...")
    worst_k_matchups = get_strikeout_worst_rankings(reports, min_drop=5.0)
    
    print("⚾ Calculating hitters to target (ranked by matchup score)...")
    top_ba_boosts = get_batting_boost_rankings(reports)
    
    # Create tweets
    strikeout_boost_tweet = create_strikeout_boost_tweet(top_k_boosts)
    strikeout_worst_tweet = create_strikeout_worst_tweet(worst_k_matchups)
    batting_boost_tweet = create_batting_boost_tweet(top_ba_boosts)
    
    # Post tweets with delays
    successful_posts = 0
    total_possible = 3
    
    if strikeout_boost_tweet:
        if post_to_twitter(client, strikeout_boost_tweet, "Strikeout Watch"):
            successful_posts += 1
        time.sleep(60)  # 1 minute delay between tweets
    else:
        print("🔥 No strikeout watch tweet (no 5%+ boosts found)")
        total_possible -= 1
    
    if strikeout_worst_tweet:
        if post_to_twitter(client, strikeout_worst_tweet, "Don't Chase K's"):
            successful_posts += 1
        time.sleep(60)  # 1 minute delay between tweets
    else:
        print("⚠️ No don't chase K's tweet (no 5%+ drops found)")
        total_possible -= 1
    
    if batting_boost_tweet:
        if post_to_twitter(client, batting_boost_tweet, "Hitters to Target"):
            successful_posts += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Completed: {successful_posts}/{total_possible} tweets posted")
    print(f"{'='*50}")

def keep_alive():
    """Keep the service alive on Render"""
    print(f"🤖 Bot is alive at {datetime.now()}")

if __name__ == "__main__":
    print("🚀 Starting MLB Daily Rankings Bot")
    print("⏰ Scheduling daily runs at 10:00 AM ET")
    
    # Schedule the main analysis
    schedule.every().day.at("15:00").do(run_daily_tweets)  # 15:00 UTC = 10:00 AM ET
    
    # Keep alive every hour
    schedule.every().hour.do(keep_alive)
    
    # Run once on startup for testing - COMMENTED OUT FOR PRODUCTION
    # print("🧪 Running initial test...")
    # run_daily_tweets()
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
