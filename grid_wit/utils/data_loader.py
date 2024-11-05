import os
from pathlib import Path
from grid_wit.config.database import get_db_session
from grid_wit.models.puzzle import Puzzle, Clue
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_word_positions(grid_data, size=15):
    """Calculate starting positions for words in the grid"""
    positions = {'across': {}, 'down': {}}
    number = 1
    
    for row in range(size):
        for col in range(size):
            index = row * size + col
            if grid_data[index] == '.':
                continue
                
            is_across_start = (col == 0 or grid_data[index - 1] == '.') and \
                             (col < size - 1 and grid_data[index + 1] != '.')
                             
            is_down_start = (row == 0 or grid_data[index - size] == '.') and \
                           (row < size - 1 and grid_data[index + size] != '.')
            
            if is_across_start or is_down_start:
                if is_across_start:
                    positions['across'][number] = {'row': row, 'column': col}
                if is_down_start:
                    positions['down'][number] = {'row': row, 'column': col}
                number += 1
                
    return positions

def parse_puzzle_json(puzzle_data):
    """Parse puzzle JSON and verify grid numbers match clues"""
    
    grid = puzzle_data['grid']  # Already a list
    gridnums = puzzle_data['gridnums']
    
    # Get clues and answers
    across_clues = puzzle_data['clues']['across']
    down_clues = puzzle_data['clues']['down']
    across_answers = puzzle_data['answers']['across']
    down_answers = puzzle_data['answers']['down']
    
    # Map positions to clue numbers
    clue_positions = {}
    for row in range(15):
        for col in range(15):
            idx = row * 15 + col
            number = gridnums[idx]
            
            if number > 0:
                # Check if this position starts an across word
                if col == 0 or (col > 0 and grid[idx-1] == '.'):
                    if col < 14 and grid[idx+1] != '.':  # Make sure it's not a single square
                        clue_positions[f"across-{number}"] = (row, col)
                
                # Check if this position starts a down word
                if row == 0 or (row > 0 and grid[idx-15] == '.'):
                    if row < 14 and grid[idx+15] != '.':  # Make sure it's not a single square
                        clue_positions[f"down-{number}"] = (row, col)
    
    return {
        'grid': grid,
        'gridnums': gridnums,
        'across_clues': across_clues,
        'down_clues': down_clues,
        'across_answers': across_answers,
        'down_answers': down_answers,
        'clue_positions': clue_positions
    }

def load_puzzles_from_json():
    """Load puzzles directly from JSON files into PostgreSQL"""
    logger.info("Starting direct JSON to PostgreSQL import...")
    
    puzzles_path = os.path.join(os.getcwd(), 'nyt_crosswords')
    
    if not os.path.exists(puzzles_path):
        raise FileNotFoundError(f"Crosswords directory not found at {puzzles_path}")
    
    with get_db_session() as session:
        # First, clear existing data
        logger.info("Clearing existing data...")
        session.query(Clue).delete()
        session.query(Puzzle).delete()
        session.commit()
        
        for year_folder in sorted(os.listdir(puzzles_path)):
            year_path = os.path.join(puzzles_path, year_folder)
            
            if os.path.isdir(year_path):
                logger.info(f"Processing year: {year_folder}")
                
                for month_folder in sorted(os.listdir(year_path)):
                    month_path = os.path.join(year_path, month_folder)
                    
                    if os.path.isdir(month_path):
                        for filename in sorted(os.listdir(month_path)):
                            if filename.endswith('.json'):
                                file_path = os.path.join(month_path, filename)
                                
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        puzzle_data = json.load(f)
                                    
                                    logger.info(f"Processing puzzle from {file_path}")
                                    parsed_data = parse_puzzle_json(puzzle_data)
                                    
                                    # Create puzzle record
                                    puzzle = Puzzle(
                                        date_published=puzzle_data['date'],
                                        author=puzzle_data['author'],
                                        grid=json.dumps(parsed_data['grid'])
                                    )
                                    session.add(puzzle)
                                    session.flush()  # Get puzzle ID
                                    
                                    # Add across clues
                                    for idx, (clue_text, answer) in enumerate(zip(parsed_data['across_clues'], parsed_data['across_answers'])):
                                        number = int(clue_text.split('.')[0])
                                        text = clue_text.split('.', 1)[1].strip()
                                        pos = parsed_data['clue_positions'].get(f"across-{number}")
                                        
                                        if pos:
                                            row, col = pos
                                            clue = Clue(
                                                puzzle_id=puzzle.id,
                                                number=number,
                                                direction='across',
                                                text=text,
                                                answer=answer,
                                                row=row,
                                                column=col
                                            )
                                            session.add(clue)
                                    
                                    # Add down clues
                                    for idx, (clue_text, answer) in enumerate(zip(parsed_data['down_clues'], parsed_data['down_answers'])):
                                        number = int(clue_text.split('.')[0])
                                        text = clue_text.split('.', 1)[1].strip()
                                        pos = parsed_data['clue_positions'].get(f"down-{number}")
                                        
                                        if pos:
                                            row, col = pos
                                            clue = Clue(
                                                puzzle_id=puzzle.id,
                                                number=number,
                                                direction='down',
                                                text=text,
                                                answer=answer,
                                                row=row,
                                                column=col
                                            )
                                            session.add(clue)
                                    
                                    session.commit()
                                    logger.info(f"Successfully processed puzzle from {file_path}")
                                    
                                except Exception as e:
                                    logger.error(f"Error processing {file_path}: {e}")
                                    session.rollback()
                                    continue
    
    logger.info("Import completed successfully!")

if __name__ == "__main__":
    load_puzzles_from_json()