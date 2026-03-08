"""
Unit tests for publishers API endpoints
Tests the publishers routes for retrieving publisher information
"""

import unittest
import json
from typing import Dict, Any, List
from flask import Flask
from models import Publisher, db
from routes.publishers import publishers_bp

class TestPublishersRoutes(unittest.TestCase):
    """Test cases for publishers API endpoints"""
    
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc", "description": "Creating games for developers"},
            {"name": "Scrum Masters", "description": "Agile game development studio"},
            {"name": "Code Publishers", "description": "Publishing coding games since 2020"}
        ]
    }
    
    # API paths
    PUBLISHERS_API_PATH: str = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the publishers blueprint
        self.app.register_blueprint(publishers_bp)
        
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
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        db.session.commit()

    def _get_response_data(self, response) -> List[Dict[str, Any]]:
        """Helper method to parse JSON response data"""
        return json.loads(response.data)

    def test_get_all_publishers_success(self) -> None:
        """Test retrieving all publishers returns correct data with id and name"""
        # Act
        response = self.client.get(self.PUBLISHERS_API_PATH)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        publishers = self._get_response_data(response)
        
        # Verify we got all publishers
        self.assertEqual(len(publishers), len(self.TEST_DATA["publishers"]))
        
        # Verify each publisher has only id and name (not description)
        for publisher in publishers:
            self.assertIn('id', publisher)
            self.assertIn('name', publisher)
            self.assertNotIn('description', publisher)
            self.assertNotIn('game_count', publisher)
            
            # Verify types
            self.assertIsInstance(publisher['id'], int)
            self.assertIsInstance(publisher['name'], str)
    
    def test_get_all_publishers_returns_correct_names(self) -> None:
        """Test that all publisher names are returned correctly"""
        # Act
        response = self.client.get(self.PUBLISHERS_API_PATH)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        publishers = self._get_response_data(response)
        
        # Extract names from response
        publisher_names = [pub['name'] for pub in publishers]
        expected_names = [pub['name'] for pub in self.TEST_DATA["publishers"]]
        
        # Verify all expected names are present
        for expected_name in expected_names:
            self.assertIn(expected_name, publisher_names)
    
    def test_get_all_publishers_empty_database(self) -> None:
        """Test retrieving publishers when database is empty returns empty list"""
        # Arrange - clear all publishers
        with self.app.app_context():
            Publisher.query.delete()
            db.session.commit()
        
        # Act
        response = self.client.get(self.PUBLISHERS_API_PATH)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        publishers = self._get_response_data(response)
        self.assertEqual(len(publishers), 0)
        self.assertIsInstance(publishers, list)

if __name__ == '__main__':
    unittest.main()
