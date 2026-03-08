"""
Publishers API routes
Provides endpoints for retrieving publisher information
"""

from flask import jsonify, Response, Blueprint
from models import db, Publisher
from sqlalchemy.orm import Query

# Create a Blueprint for publishers routes
publishers_bp = Blueprint('publishers', __name__)

def get_publishers_base_query() -> Query:
    """
    Returns the base query for publishers.
    
    Returns:
        Query: SQLAlchemy query object for Publisher model
    """
    return db.session.query(Publisher)

@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    """
    Get all publishers with their id and name.
    
    Returns:
        Response: JSON response containing list of publishers with id and name
    """
    # Use the base query for all publishers
    publishers_query = get_publishers_base_query().all()
    
    # Convert the results to dict and return only id and name
    publishers_list = [{'id': pub.id, 'name': pub.name} for pub in publishers_query]
    
    return jsonify(publishers_list)
