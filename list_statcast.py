import pybaseballstats

# List all statcast functions to get the exact names
print("Available statcast functions:")
statcast_funcs = [f for f in dir(pybaseballstats) if 'statcast' in f.lower()]
for func in statcast_funcs:
    print(f"  - {func}")
