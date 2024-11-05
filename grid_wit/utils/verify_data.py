# verify_data.py

from grid_wit.config.database import get_db_session
from grid_wit.models.puzzle import Puzzle, Clue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_data():
    """Verify puzzle and clue data in the database"""
    with get_db_session() as session:
        try:
            # Query some puzzles
            logger.info("\n** Sample Puzzles **")
            puzzles = session.query(Puzzle).limit(5).all()
            for puzzle in puzzles:
                logger.info(f"Puzzle ID: {puzzle.id}")
                logger.info(f"Date Published: {puzzle.date_published}")
                logger.info(f"Author: {puzzle.author}")
                logger.info(f"Grid: {puzzle.grid[:50]}...")  # Show first 50 chars
                logger.info("---")

            # Query clues for first puzzle
            if puzzles:
                sample_puzzle = puzzles[0]
                logger.info(f"\n** Clues for Puzzle ID {sample_puzzle.id} **")
                
                # Query across clues with explicit join
                across_clues = session.query(Clue).filter(
                    Clue.puzzle_id == sample_puzzle.id,
                    Clue.direction == 'across'
                ).order_by(Clue.number).limit(10).all()
                
                logger.info("\nACROSS CLUES:")
                for clue in across_clues:
                    logger.info(f"{clue.number}. {clue.text}")
                    logger.info(f"   Answer: {clue.answer}")
                    logger.info(f"   Position: ({clue.row}, {clue.column})")
                
                # Query down clues with explicit join
                down_clues = session.query(Clue).filter(
                    Clue.puzzle_id == sample_puzzle.id,
                    Clue.direction == 'down'
                ).order_by(Clue.number).limit(10).all()
                
                logger.info("\nDOWN CLUES:")
                for clue in down_clues:
                    logger.info(f"{clue.number}. {clue.text}")
                    logger.info(f"   Answer: {clue.answer}")
                    logger.info(f"   Position: ({clue.row}, {clue.column})")

            # Get some statistics
            puzzle_count = session.query(Puzzle).count()
            clue_count = session.query(Clue).count()
            
            # Get sample clue counts for a few puzzles
            for puzzle in puzzles[:3]:
                across_count = session.query(Clue).filter(
                    Clue.puzzle_id == puzzle.id,
                    Clue.direction == 'across'
                ).count()
                down_count = session.query(Clue).filter(
                    Clue.puzzle_id == puzzle.id,
                    Clue.direction == 'down'
                ).count()
                logger.info(f"\nPuzzle {puzzle.id} clue counts:")
                logger.info(f"Across clues: {across_count}")
                logger.info(f"Down clues: {down_count}")
                logger.info(f"Total clues: {across_count + down_count}")

            logger.info(f"\nTotal Puzzles: {puzzle_count}")
            logger.info(f"Total Clues: {clue_count}")
            logger.info(f"Average Clues per Puzzle: {clue_count/puzzle_count if puzzle_count else 0:.1f}")

        except Exception as e:
            logger.error(f"Error verifying data: {e}")
            raise

if __name__ == "__main__":
    verify_data()
