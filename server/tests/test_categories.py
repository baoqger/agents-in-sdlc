"""
Unit tests for categories API endpoints
Tests the categories routes for retrieving category information
"""

import unittest
import json
from typing import Dict, Any, List
from flask import Flask
from models import Category, db
from routes.categories import categories_bp

class TestCategoriesRoutes(unittest.TestCase):
    """Test cases for categories API endpoints"""
    
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "categories": [
            {"name": "Strategy", "description": "Strategic planning and execution games"},
            {"name": "Card Game", "description": "Card-based gameplay mechanics"},
            {"name": "Cooperative", "description": "Team-based collaborative games"}
        ]
    }
    
    # API paths
    CATEGORIES_API_PATH: str = '/api/categories'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the categories blueprint
        self.app.register_blueprint(categories_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        db.session.commit()

    def _get_response_data(self, response) -> List[Dict[str, Any]]:
        """Helper method to parse JSON response data"""
        return json.loads(response.data)

    def test_get_all_categories_success(self) -> None:
        """Test retrieving all categories returns correct data with id and name"""
        # Act
        response = self.client.get(self.CATEGORIES_API_PATH)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        categories = self._get_response_data(response)
        
        # Verify we got all categories
        self.assertEqual(len(categories), len(self.TEST_DATA["categories"]))
        
        # Verify each category has only id and name (not description)
        for category in categories:
            self.assertIn('id', category)
            self.assertIn('name', category)
            self.assertNotIn('description', category)
            self.assertNotIn('game_count', category)
            
            # Verify types
            self.assertIsInstance(category['id'], int)
            self.assertIsInstance(category['name'], str)
    
    def test_get_all_categories_returns_correct_names(self) -> None:
        """Test that all category names are returned correctly"""
        # Act
        response = self.client.get(self.CATEGORIES_API_PATH)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        categories = self._get_response_data(response)
        
        # Extract names from response
        category_names = [cat['name'] for cat in categories]
        expected_names = [cat['name'] for cat in self.TEST_DATA["categories"]]
        
        # Verify all expected names are present
        for expected_name in expected_names:
            self.assertIn(expected_name, category_names)
    
    def test_get_all_categories_empty_database(self) -> None:
        """Test retrieving categories when database is empty returns empty list"""
        # Arrange - clear all categories
        with self.app.app_context():
            Category.query.delete()
            db.session.commit()
        
        # Act
        response = self.client.get(self.CATEGORIES_API_PATH)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        categories = self._get_response_data(response)
        self.assertEqual(len(categories), 0)
        self.assertIsInstance(categories, list)

if __name__ == '__main__':
    unittest.main()
