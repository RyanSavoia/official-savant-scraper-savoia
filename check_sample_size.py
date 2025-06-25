# Modify the return statement in get_batter_vs_pitches to include PA data:
if len(batter_pitch_data) > 0:
    return batter_pitch_data.select(['pitch_type', 'ba', 'est_ba', 'slg', 
                                   'hard_hit_percent', 'whiff_percent', 'k_percent',
                                   'pa', 'pitches']).to_dicts()  # Added pa and pitches
