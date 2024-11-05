from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from grid_wit.config.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    saved_puzzles = relationship("SavedPuzzle", back_populates="user")

class SavedPuzzle(Base):
    __tablename__ = 'saved_puzzles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    puzzle_id = Column(Integer, ForeignKey('puzzles.id', ondelete='CASCADE'))
    progress = Column(JSON)  # Store user's progress as JSON
    completed = Column(Boolean, default=False)
    last_played = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_puzzles")
    puzzle = relationship("Puzzle")

class DailyPuzzleHistory(Base):
    __tablename__ = 'daily_puzzle_history'
    
    id = Column(Integer, primary_key=True)
    puzzle_id = Column(Integer, ForeignKey('puzzles.id', ondelete='CASCADE'))
    served_date = Column(DateTime(timezone=True), server_default=func.now())
    cycle_number = Column(Integer, default=1)  # Track which cycle this puzzle was served in 