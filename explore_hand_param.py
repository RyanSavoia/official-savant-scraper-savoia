import pybaseballstats.statcast_leaderboards as sc

print("=== EXPLORING PITCHER HANDEDNESS OPTIONS ===\n")

# 1. Try getting left-handed pitchers only
print("1. Left-handed pitchers:")
lhp_data = sc.statcast_pitch_arsenals_leaderboard(2024, hand='L')
print(f"   Got {len(lhp_data)} left-handed pitchers")

# 2. Try getting right-handed pitchers only
print("\n2. Right-handed pitchers:")
rhp_data = sc.statcast_pitch_arsenals_leaderboard(2024, hand='R')
print(f"   Got {len(rhp_data)} right-handed pitchers")

# 3. Check if there are columns showing usage vs different batter handedness
print("\n3. Checking all columns in pitcher arsenal data:")
all_cols = list(lhp_data.columns)
print(f"   Total columns: {len(all_cols)}")

# Look for any vs_rhb, vs_lhb type columns
print("\n4. Looking for handedness-specific usage columns:")
for col in all_cols:
    if any(x in col.lower() for x in ['rhb', 'lhb', 'vs_r', 'vs_l', '_r_', '_l_']):
        print(f"   - {col}")

# 5. Check batter perspective data for handedness info
print("\n5. Checking batter vs pitch type data:")
batter_data = sc.statcast_pitch_arsenal_stats_leaderboard(2024, perspective='batter', min_pa=50)
print(f"   Columns: {list(batter_data.columns[:20])}")

# Check for pitcher handedness in batter data
hand_cols = [col for col in batter_data.columns if 'hand' in col.lower() or 'throw' in col.lower()]
print(f"   Handedness columns: {hand_cols if hand_cols else 'NONE'}")
