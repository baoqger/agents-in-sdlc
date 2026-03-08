"""
Categories API routes
Provides endpoints for retrieving category information
"""

from flask import jsonify, Response, Blueprint
from models import db, Category
from sqlalchemy.orm import Query

# Create a Blueprint for categories routes
categories_bp = Blueprint('categories', __name__)

def get_categories_base_query() -> Query:
    """
    Returns the base query for categories.
    
    Returns:
        Query: SQLAlchemy query object for Category model
    """
    return db.session.query(Category)

@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    """
    Get all categories with their id and name.
    
    Returns:
        Response: JSON response containing list of categories with id and name
    """
    # Use the base query for all categories
    categories_query = get_categories_base_query().all()
    
    # Convert the results to dict and return only id and name
    categories_list = [{'id': cat.id, 'name': cat.name} for cat in categories_query]
    
    return jsonify(categories_list)
