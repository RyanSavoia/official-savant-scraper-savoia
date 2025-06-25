from pybaseballstats.statcast_leaderboards import statcast_pitch_arsenal_stats_leaderboard

print('=== LOOKING FOR PITCHER DATA ===')
pitch_data = statcast_pitch_arsenal_stats_leaderboard(2025, min_pa=20)

# Look for pitcher names we know
pitcher_names = ['Skenes', 'Misiorowski', 'Gallen', 'Gore', 'Pivetta', 'Kikuchi', 'Fitts']

for pitcher in pitcher_names:
    matches = pitch_data.filter(
        pitch_data['last_name, first_name'].str.contains(pitcher)
    )
    if len(matches) > 0:
        print(f'\nFound {pitcher}:')
        sample = matches.head(3).to_dict()
        for key in ['last_name, first_name', 'pitch_type', 'pitch_name', 'ba', 'slg']:
            if key in sample:
                print(f'  {key}: {sample[key]}')

# Check if this is batter vs pitch type or pitcher vs batter
print(f'\n=== CHECKING DATA TYPE ===')
print(f'Total unique players: {pitch_data["last_name, first_name"].n_unique()}')
print(f'Total unique pitch types: {pitch_data["pitch_type"].n_unique()}')

# Show unique pitch types
unique_pitches = pitch_data["pitch_type"].unique().to_list()
print(f'Pitch types: {unique_pitches}')

# Show a few more samples to understand the data structure
print(f'\n=== MORE SAMPLES ===')
samples = pitch_data.head(10)
for i in range(min(5, len(samples))):
    row = samples.row(i, named=True)
    print(f'  {row["last_name, first_name"]} vs {row["pitch_type"]}: BA {row["ba"]:.3f}')
