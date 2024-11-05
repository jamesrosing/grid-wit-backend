from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from grid_wit.config.database import Base

class Puzzle(Base):
    __tablename__ = 'puzzles'
    
    id = Column(Integer, primary_key=True)
    date_published = Column(String, index=True)
    author = Column(String)
    grid = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add relationship to clues
    clues = relationship("Clue", back_populates="puzzle", cascade="all, delete-orphan")

class Clue(Base):
    __tablename__ = 'clues'
    
    id = Column(Integer, primary_key=True)
    puzzle_id = Column(Integer, ForeignKey('puzzles.id', ondelete='CASCADE'))
    number = Column(Integer)
    direction = Column(String)
    text = Column(Text)
    answer = Column(String)
    row = Column(Integer)
    column = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add relationship to puzzle
    puzzle = relationship("Puzzle", back_populates="clues")
    
    # Indexes
    __table_args__ = (
        Index('idx_puzzle_direction', 'puzzle_id', 'direction'),
    )

def init_db():
    """Initialize the database schema"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database and tables created successfully!")