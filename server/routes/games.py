"""
Games API routes
Provides endpoints for retrieving, creating, updating, and deleting game information.
"""
from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    """Build the base SQLAlchemy query for games, joining Publisher and Category.

    Returns:
        Query: SQLAlchemy query object for the Game model with Publisher and Category joined.
    """
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    """
    Get all games with optional filtering by category and publisher.
    
    Query Parameters:
        category_id (int, optional): Filter games by category ID
        publisher_id (int, optional): Filter games by publisher ID
    
    Returns:
        Response: JSON response containing list of games
    """
    # Start with the base query
    games_query = get_games_base_query()
    
    # Apply filters based on query parameters
    category_id = request.args.get('category_id', type=int)
    publisher_id = request.args.get('publisher_id', type=int)
    
    if category_id is not None:
        games_query = games_query.filter(Game.category_id == category_id)
    
    if publisher_id is not None:
        games_query = games_query.filter(Game.publisher_id == publisher_id)
    
    # Execute the query
    games = games_query.all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    """Get a single game by its ID.

    Args:
        id (int): The unique identifier of the game.

    Returns:
        Response: JSON response containing the game data, or a 404 error if not found.
    """
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    """Create a new game.

    Expected JSON body:
        title (str): The game title (min 2 characters, required).
        description (str): The game description (min 10 characters, required).
        category_id (int): The ID of the category (required).
        publisher_id (int): The ID of the publisher (required).
        star_rating (float, optional): The star rating for the game.

    Returns:
        tuple[Response, int]: JSON response with the created game and HTTP 201 status,
            or a 400 error response if validation fails.
    """
    data = request.get_json(force=True, silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate required fields
    required_fields = ['title', 'description', 'category_id', 'publisher_id']
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({"error": f"'{field}' is required"}), 400

    # Verify category and publisher exist
    category = db.session.get(Category, data['category_id'])
    if not category:
        return jsonify({"error": "Category not found"}), 400

    publisher = db.session.get(Publisher, data['publisher_id'])
    if not publisher:
        return jsonify({"error": "Publisher not found"}), 400

    try:
        game = Game(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            publisher_id=data['publisher_id'],
            star_rating=data.get('star_rating')
        )
        db.session.add(game)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify(game.to_dict()), 201

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int] | Response:
    """Update an existing game by its ID.

    Args:
        id (int): The unique identifier of the game to update.

    Expected JSON body (all fields optional):
        title (str): The updated game title (min 2 characters).
        description (str): The updated game description (min 10 characters).
        category_id (int): The updated category ID.
        publisher_id (int): The updated publisher ID.
        star_rating (float): The updated star rating.

    Returns:
        tuple[Response, int] | Response: JSON response with the updated game,
            or a 400/404 error response if validation fails or game not found.
    """
    game = get_games_base_query().filter(Game.id == id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json(force=True, silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Verify category exists if provided
    if 'category_id' in data:
        category = db.session.get(Category, data['category_id'])
        if not category:
            return jsonify({"error": "Category not found"}), 400

    # Verify publisher exists if provided
    if 'publisher_id' in data:
        publisher = db.session.get(Publisher, data['publisher_id'])
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 400

    try:
        updatable_fields = ['title', 'description', 'category_id', 'publisher_id', 'star_rating']
        for field in updatable_fields:
            if field in data:
                setattr(game, field, data[field])

        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify(game.to_dict())

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    """Delete a game by its ID.

    Args:
        id (int): The unique identifier of the game to delete.

    Returns:
        tuple[Response, int]: JSON response confirming deletion,
            or a 404 error if the game is not found.
    """
    game = db.session.get(Game, id)

    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Store title before deletion so it can be used in the response message
    game_title = game.title
    db.session.delete(game)
    db.session.commit()

    return jsonify({"message": f"Game '{game_title}' deleted successfully"}), 200
