from pybaseballstats.statcast_leaderboards import statcast_pitch_arsenal_stats_leaderboard

print('=== TESTING PITCH ARSENAL STATS (BA AGAINST) ===')
pitch_data = statcast_pitch_arsenal_stats_leaderboard(2025, min_pa=20)

print(f'Total records: {len(pitch_data)}')
print('All columns:')
for col in pitch_data.columns:
    print(f'  {col}')

print('\n=== SAMPLE DATA FOR A PITCHER ===')
# Find a pitcher with multiple pitch types
sample_pitcher = pitch_data.filter(
    (pitch_data['last_name, first_name'].str.contains('Misiorowski')) |
    (pitch_data['last_name, first_name'].str.contains('Skenes'))
).head(5)

if len(sample_pitcher) > 0:
    print('Sample pitcher data:')
    sample_dict = sample_pitcher.to_dict()
    for key, value in sample_dict.items():
        print(f'  {key}: {value}')
else:
    print('No sample pitcher found, showing first pitcher:')
    first_pitcher = pitch_data.head(3).to_dict()
    for key, value in first_pitcher.items():
        print(f'  {key}: {value}')
