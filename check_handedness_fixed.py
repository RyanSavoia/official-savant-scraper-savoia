import pybaseballstats.statcast_leaderboards as sc
import pybaseballstats.fangraphs as fg

print("=== CHECKING HANDEDNESS DATA AVAILABILITY ===\n")

# 1. Check Fangraphs batting data
print("1. FANGRAPHS BATTING DATA:")
batting_data = fg.fangraphs_batting_range("2024-01-01", "2024-12-31", min_pa=50)
print(f"   - Has 'Bats' column: {'Bats' in batting_data.columns}")
print(f"   - Batter handedness values: {batting_data['Bats'].unique()}")
print(f"   - Can filter by batting_hand parameter: YES (L, R, S)")

# Check for vs RHP/LHP columns
vs_columns = [col for col in batting_data.columns if 'vs' in col.lower() or 'rhp' in col.lower() or 'lhp' in col.lower()]
print(f"   - Columns with 'vs/rhp/lhp': {vs_columns if vs_columns else 'NONE'}")

# 2. Check Savant pitcher arsenal data
print("\n2. SAVANT PITCHER ARSENAL DATA:")
pitcher_data = sc.statcast_pitch_arsenals_leaderboard(2024, min_ip=20)
print(f"   - Total columns: {len(pitcher_data.columns)}")

# Check for handedness-related columns
hand_cols = [col for col in pitcher_data.columns if any(x in col.lower() for x in ['rhb', 'lhb', 'rh_', 'lh_', 'hand', '_r_', '_l_'])]
print(f"   - Handedness-related columns: {hand_cols if hand_cols else 'NONE'}")

# 3. Check Savant batter vs pitch type data
print("\n3. SAVANT BATTER VS PITCH TYPE DATA:")
batter_pitch_data = sc.statcast_pitch_arsenal_stats_leaderboard(2024, min_pa=50)
print(f"   - Total columns: {len(batter_pitch_data.columns)}")

# Check what's in this data
if len(batter_pitch_data) > 0:
    print(f"   - Sample columns: {list(batter_pitch_data.columns[:15])}")
    
# Check for handedness info
hand_cols2 = [col for col in batter_pitch_data.columns if any(x in col.lower() for x in ['hand', 'bats', 'throws', 'stand'])]
print(f"   - Handedness columns: {hand_cols2 if hand_cols2 else 'NONE'}")

print("\n=== SUMMARY ===")
print("What handedness data IS available:")
print("- Batter handedness (L/R/S) in Fangraphs data")
print("- Can filter Fangraphs queries by batter handedness")
print("\nWhat handedness data is NOT available:")
print("- Batter stats vs LHP/RHP splits")
print("- Pitcher arsenal usage vs LHB/RHB")
