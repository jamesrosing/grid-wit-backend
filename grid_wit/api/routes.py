from flask import Blueprint, jsonify, request, g
from grid_wit.config.database import get_db_session
from grid_wit.models.puzzle import Puzzle, Clue
from grid_wit.models.user import User, SavedPuzzle, DailyPuzzleHistory
from sqlalchemy import or_, func, desc
from datetime import datetime, timedelta
import random
import logging

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api.route('/')
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        "message": "Welcome to the Crossword API",
        "version": "1.0.0",
        "documentation": {
            "endpoints": {
                "GET /": "This documentation",
                "GET /api/puzzles": "List all puzzles (supports page and per_page params)",
                "GET /api/puzzles/<id>": "Get specific puzzle",
                "GET /api/puzzles/daily": "Get daily puzzle (randomly selected)",
                "GET /api/puzzles/search": "Search puzzles by author, date, or content",
                "GET /api/status": "Get API and database status",
                "POST /api/users": "Create new user",
                "GET /api/users/<id>/puzzles": "Get user's saved puzzles",
                "POST /api/users/<id>/puzzles": "Save puzzle progress",
                "PUT /api/users/<id>/puzzles/<puzzle_id>": "Update puzzle progress"
            },
            "search_params": {
                "author": "Search by author name",
                "date": "Search by date (YYYY-MM-DD)",
                "word": "Search for word in answers",
                "clue": "Search in clue text"
            }
        }
    })

@api.route('/status')
def get_status():
    """Get API status"""
    try:
        with get_db_session() as session:
            # Check database connection by making a simple query
            puzzle_count = session.query(Puzzle).count()
            
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "puzzle_count": puzzle_count,
                "clue_count": session.query(Clue).count(),
                "timestamp": datetime.utcnow().isoformat()
            })
    except Exception as e:
        logger.error(f"Error checking API status: {e}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@api.route('/puzzles/daily')
def get_daily_puzzle():
    """Get a random puzzle for today"""
    try:
        with get_db_session() as session:
            puzzle = session.query(Puzzle).order_by(func.random()).first()
            if not puzzle:
                return jsonify({"error": "No puzzles found"}), 404
            
            # Get only clues for this puzzle
            clues = session.query(Clue).filter(
                Clue.puzzle_id == puzzle.id
            ).order_by(Clue.number).all()
            
            return jsonify({
                "id": puzzle.id,
                "date_published": puzzle.date_published,
                "author": puzzle.author,
                "grid": puzzle.grid,
                "clues": [{
                    "number": clue.number,
                    "direction": clue.direction,
                    "text": clue.text,
                    "answer": clue.answer,
                    "row": clue.row,
                    "column": clue.column
                } for clue in clues]
            })
    except Exception as e:
        logger.error(f"Error getting daily puzzle: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/puzzles/search')
def search_puzzles():
    try:
        with get_db_session() as session:
            query = session.query(Puzzle)
            
            # Search by author
            if author := request.args.get('author'):
                query = query.filter(Puzzle.author.ilike(f'%{author}%'))
            
            # Search by date
            if date := request.args.get('date'):
                query = query.filter(Puzzle.date_published == date)
            
            # Search by word in answers
            if word := request.args.get('word'):
                query = query.join(Clue).filter(Clue.answer.ilike(f'%{word}%'))
            
            # Search in clue text
            if clue_text := request.args.get('clue'):
                query = query.join(Clue).filter(Clue.text.ilike(f'%{clue_text}%'))
            
            # Paginate results
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 10, type=int), 50)
            
            total = query.count()
            puzzles = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return jsonify({
                "puzzles": [{
                    "id": p.id,
                    "date_published": p.date_published,
                    "author": p.author,
                    "grid": p.grid,
                    "clues": [{
                        "number": c.number,
                        "direction": c.direction,
                        "text": c.text,
                        "answer": c.answer
                    } for c in p.clues]
                } for p in puzzles],
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            })
            
    except Exception as e:
        logger.error(f"Error searching puzzles: {e}")
        return jsonify({"error": str(e)}), 500

# User management endpoints
@api.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'email' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        with get_db_session() as session:
            user = User(
                username=data['username'],
                email=data['email']
            )
            session.add(user)
            session.commit()
            
            return jsonify({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at
            }), 201
            
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/users/<int:user_id>/puzzles', methods=['GET'])
def get_user_puzzles(user_id):
    try:
        with get_db_session() as session:
            saved_puzzles = session.query(SavedPuzzle).filter(
                SavedPuzzle.user_id == user_id
            ).all()
            
            return jsonify({
                "puzzles": [{
                    "puzzle_id": sp.puzzle_id,
                    "progress": sp.progress,
                    "completed": sp.completed,
                    "last_played": sp.last_played,
                    "puzzle": {
                        "date_published": sp.puzzle.date_published,
                        "author": sp.puzzle.author
                    }
                } for sp in saved_puzzles]
            })
            
    except Exception as e:
        logger.error(f"Error fetching user puzzles: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/users/<int:user_id>/puzzles/<int:puzzle_id>', methods=['POST', 'PUT'])
def save_puzzle_progress(user_id, puzzle_id):
    try:
        data = request.get_json()
        if not data or 'progress' not in data:
            return jsonify({"error": "Missing progress data"}), 400
            
        with get_db_session() as session:
            if request.method == 'POST':
                saved_puzzle = SavedPuzzle(
                    user_id=user_id,
                    puzzle_id=puzzle_id,
                    progress=data['progress'],
                    completed=data.get('completed', False)
                )
                session.add(saved_puzzle)
            else:
                saved_puzzle = session.query(SavedPuzzle).filter(
                    SavedPuzzle.user_id == user_id,
                    SavedPuzzle.puzzle_id == puzzle_id
                ).first()
                
                if not saved_puzzle:
                    return jsonify({"error": "Saved puzzle not found"}), 404
                    
                saved_puzzle.progress = data['progress']
                saved_puzzle.completed = data.get('completed', saved_puzzle.completed)
                
            session.commit()
            
            return jsonify({
                "puzzle_id": puzzle_id,
                "progress": saved_puzzle.progress,
                "completed": saved_puzzle.completed,
                "last_played": saved_puzzle.last_played
            })
            
    except Exception as e:
        logger.error(f"Error saving puzzle progress: {e}")
        return jsonify({"error": str(e)}), 500