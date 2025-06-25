import re

def parse_batter_name(lineup_string):
    """Extract batter name from various lineup formats"""
    # Remove numbers from start/end
    cleaned = re.sub(r'^\d+\s+', '', lineup_string)
    cleaned = re.sub(r'\s+\d+$', '', cleaned)
    
    # Remove handedness indicators (L), (R), (S)
    cleaned = re.sub(r'\([LRS]\)', '', cleaned)
    
    # Remove position abbreviations (must be 1-2 uppercase letters at word boundaries)
    # Common positions: C, 1B, 2B, 3B, SS, LF, CF, RF, DH
    position_pattern = r'\b(C|1B|2B|3B|SS|LF|CF|RF|DH)\b'
    cleaned = re.sub(position_pattern, '', cleaned)
    
    # Clean up extra spaces
    name = ' '.join(cleaned.split()).strip()
    
    # Split name parts
    parts = name.split()
    
    # Handle names properly
    if len(parts) >= 2:
        # Handle cases like "Ronald Acuña Jr." - Jr. is part of last name
        if parts[-1].lower() in ['jr', 'jr.', 'sr', 'sr.', 'ii', 'iii']:
            last_name = f"{parts[-2]} {parts[-1]}"
            first_name = ' '.join(parts[:-2])
        else:
            last_name = parts[-1]
            first_name = ' '.join(parts[:-1])
        
        return f"{last_name}, {first_name}"
    
    return name

# Test it
test_names = [
    "3   Cal Raleigh (S) C",
    "SS (L) Gunnar Henderson   3",
    "1   Ronald Acuña Jr. (R) RF",
    "CF (L) Cedric Mullins   6"
]

print("Testing name parser:")
for name in test_names:
    parsed = parse_batter_name(name)
    print(f"{name} → {parsed}")
