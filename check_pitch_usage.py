import pybaseballstats
from pybaseballstats.statcast_leaderboards import statcast_pitch_arsenals_leaderboard

print("Checking what pitch usage data is available...")
arsenals = statcast_pitch_arsenals_leaderboard(2025)

# Get column names
print("\nAvailable columns:")
for col in arsenals.columns:
    print(f"  {col}")

# Check first pitcher's data
if len(arsenals) > 0:
    first_pitcher = arsenals.row(0, named=True)
    print(f"\nSample pitcher data for {first_pitcher.get('last_name, first_name')}:")
    
    # Look for percentage/usage columns
    for key, value in first_pitcher.items():
        if 'pct' in key.lower() or 'percent' in key.lower() or 'usage' in key.lower():
            print(f"  {key}: {value}")
        elif key.startswith(('ff_', 'si_', 'fc_', 'sl_', 'ch_', 'cu_', 'st_')):
            if not key.endswith(('_avg_speed', '_avg_spin')):
                print(f"  {key}: {value}")
