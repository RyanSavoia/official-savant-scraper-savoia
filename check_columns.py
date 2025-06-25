from pybaseballstats.statcast_leaderboards import statcast_pitch_arsenals_leaderboard
import polars as pl

arsenals = statcast_pitch_arsenals_leaderboard(2025)

print('Available columns:')
for col in arsenals.columns:
    print(f'  {col}')

print('\nColumns containing "ba" or "avg":')
for col in arsenals.columns:
    if 'ba' in col.lower() or 'avg' in col.lower():
        print(f'  {col}')

print('\nFirst pitcher sample:')
print(arsenals.head(1).to_dict())
