import json
import os
from pathlib import Path

def create_sample_puzzle():
    """Create a sample puzzle with clues"""
    sample_puzzle = {
        "date": "11/6/2004",
        "author": "Kyle Mahowald",
        "grid": ["X", "A", "M", "O", "U", "N", "T", ".", "W", "H", "I", "Z", "K", "I", "D"],  # ... rest of grid
        "clues": {
            "across": [
                "1. Sum of money",
                "5. Smart youngster",
                "10. Wrestling move",
                # ... more across clues
            ],
            "down": [
                "1. Downward direction",
                "2. Opposite of subtract",
                "3. Climbing plant",
                # ... more down clues
            ]
        },
        "answers": {
            "across": [
                "XAMOUNT",
                "WHIZKID",
                "GRAPPLE",
                # ... more across answers
            ],
            "down": [
                "XAG",
                "ARC",
                "MIC",
                # ... more down answers
            ]
        }
    }
    return sample_puzzle

def setup_sample_data():
    """Create sample puzzle data files"""
    base_dir = Path("nyt_crosswords")
    year_dir = base_dir / "2004" / "11"
    year_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample puzzle file
    puzzle_file = year_dir / "2004-11-06.json"
    with open(puzzle_file, "w") as f:
        json.dump(create_sample_puzzle(), f, indent=2)
    
    print(f"Created sample puzzle at {puzzle_file}")

if __name__ == "__main__":
    setup_sample_data() 