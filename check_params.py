import pybaseballstats
from pybaseballstats.statcast_leaderboards import statcast_pitch_arsenal_stats_leaderboard
import inspect

# Check function parameters
print("Function signature:")
print(inspect.signature(statcast_pitch_arsenal_stats_leaderboard))

# Try with different parameters
print("\nTrying with min_pa=1:")
try:
    data = statcast_pitch_arsenal_stats_leaderboard(2025, min_pa=1)
    print(f"Records with min_pa=1: {len(data)}")
except Exception as e:
    print(f"min_pa parameter not supported: {e}")

print("\nChecking docstring:")
print(statcast_pitch_arsenal_stats_leaderboard.__doc__)

# Let's also check what other functions are available
print("\nOther statcast functions available:")
import pybaseballstats.statcast as statcast
funcs = [f for f in dir(statcast) if not f.startswith('_')]
for func in funcs:
    print(f"  - {func}")
