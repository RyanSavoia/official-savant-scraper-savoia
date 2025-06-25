import pybaseballstats.statcast_leaderboards as sc
import inspect

# Check the function signature for pitch arsenals
print("statcast_pitch_arsenals_leaderboard signature:")
print(inspect.signature(sc.statcast_pitch_arsenals_leaderboard))

print("\n\nstatcast_pitch_arsenal_stats_leaderboard signature:")
print(inspect.signature(sc.statcast_pitch_arsenal_stats_leaderboard))

# Try calling with just the year
print("\n\nTrying with just year parameter:")
pitcher_data = sc.statcast_pitch_arsenals_leaderboard(2024)
print(f"Got {len(pitcher_data)} pitchers")
print(f"Columns: {list(pitcher_data.columns[:20])}")

# Check for handedness columns
hand_cols = [col for col in pitcher_data.columns if any(x in col.lower() for x in ['rhb', 'lhb', 'vs_r', 'vs_l', 'hand'])]
print(f"\nHandedness-related columns: {hand_cols if hand_cols else 'NONE'}")
