import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
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
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))
            
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        # Verify all games using loop instead of manual testing
        for i, game_data in enumerate(data):
            test_game = self.TEST_DATA["games"][i]
            test_publisher = self.TEST_DATA["publishers"][test_game["publisher_index"]]
            test_category = self.TEST_DATA["categories"][test_game["category_index"]]
            
            self.assertEqual(game_data['title'], test_game["title"])
            self.assertEqual(game_data['publisher']['name'], test_publisher["name"])
            self.assertEqual(game_data['category']['name'], test_category["name"])
            self.assertEqual(game_data['starRating'], test_game["star_rating"])

    def test_get_games_structure(self) -> None:
        """Test the response structure for games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        # Get the first game's ID from the list endpoint
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        first_game = self.TEST_DATA["games"][0]
        first_publisher = self.TEST_DATA["publishers"][first_game["publisher_index"]]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], first_game["title"])
        self.assertEqual(data['publisher']['name'], first_publisher["name"])
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_get_games_empty_database(self) -> None:
        """Test retrieval of games when database is empty"""
        # Clear all games from the database
        with self.app.app_context():
            db.session.query(Game).delete()
            db.session.commit()
        
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_get_game_by_invalid_id_type(self) -> None:
        """Test retrieval of a game with invalid ID type"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/invalid-id')
        
        # Assert
        # Flask should return 404 for routes that don't match the <int:id> pattern
        self.assertEqual(response.status_code, 404)

    def test_filter_games_by_category(self) -> None:
        """Test filtering games by category ID"""
        # Get all games to find a category ID
        response = self.client.get(self.GAMES_API_PATH)
        all_games = self._get_response_data(response)
        
        # Get the first game's category ID
        category_id = all_games[0]['category']['id']
        
        # Act - filter by that category
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={category_id}')
        filtered_games = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(filtered_games, list)
        self.assertGreater(len(filtered_games), 0)
        
        # Verify all returned games have the requested category
        for game in filtered_games:
            self.assertEqual(game['category']['id'], category_id)

    def test_filter_games_by_publisher(self) -> None:
        """Test filtering games by publisher ID"""
        # Get all games to find a publisher ID
        response = self.client.get(self.GAMES_API_PATH)
        all_games = self._get_response_data(response)
        
        # Get the first game's publisher ID
        publisher_id = all_games[0]['publisher']['id']
        
        # Act - filter by that publisher
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id={publisher_id}')
        filtered_games = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(filtered_games, list)
        self.assertGreater(len(filtered_games), 0)
        
        # Verify all returned games have the requested publisher
        for game in filtered_games:
            self.assertEqual(game['publisher']['id'], publisher_id)

    def test_filter_games_by_category_and_publisher(self) -> None:
        """Test filtering games by both category and publisher ID"""
        # Get all games to find IDs
        response = self.client.get(self.GAMES_API_PATH)
        all_games = self._get_response_data(response)
        
        # Get the first game's category and publisher IDs
        category_id = all_games[0]['category']['id']
        publisher_id = all_games[0]['publisher']['id']
        
        # Act - filter by both category and publisher
        response = self.client.get(
            f'{self.GAMES_API_PATH}?category_id={category_id}&publisher_id={publisher_id}'
        )
        filtered_games = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(filtered_games, list)
        self.assertGreater(len(filtered_games), 0)
        
        # Verify all returned games have both the requested category and publisher
        for game in filtered_games:
            self.assertEqual(game['category']['id'], category_id)
            self.assertEqual(game['publisher']['id'], publisher_id)

    def test_filter_games_by_nonexistent_category(self) -> None:
        """Test filtering games by a category ID that doesn't exist returns empty list"""
        # Act - use a category ID that doesn't exist
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id=999')
        filtered_games = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(filtered_games, list)
        self.assertEqual(len(filtered_games), 0)

    def test_filter_games_by_nonexistent_publisher(self) -> None:
        """Test filtering games by a publisher ID that doesn't exist returns empty list"""
        # Act - use a publisher ID that doesn't exist
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id=999')
        filtered_games = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(filtered_games, list)
        self.assertEqual(len(filtered_games), 0)

    # --- CREATE (POST) tests ---

    def test_create_game_success(self) -> None:
        """Test successful creation of a new game"""
        # Arrange - get valid category and publisher IDs
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        category_id = games[0]['category']['id']
        publisher_id = games[0]['publisher']['id']

        new_game = {
            "title": "Sprint Simulator",
            "description": "Plan, execute, and review sprints in this agile board game",
            "category_id": category_id,
            "publisher_id": publisher_id,
            "star_rating": 4.8
        }

        # Act
        response = self.client.post(
            self.GAMES_API_PATH,
            data=json.dumps(new_game),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', data)
        self.assertEqual(data['title'], new_game['title'])
        self.assertEqual(data['description'], new_game['description'])
        self.assertEqual(data['starRating'], new_game['star_rating'])

    def test_create_game_missing_required_field(self) -> None:
        """Test that creating a game without a required field returns 400"""
        # Arrange - missing 'description'
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        category_id = games[0]['category']['id']
        publisher_id = games[0]['publisher']['id']

        new_game = {
            "title": "Sprint Simulator",
            "category_id": category_id,
            "publisher_id": publisher_id
        }

        # Act
        response = self.client.post(
            self.GAMES_API_PATH,
            data=json.dumps(new_game),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_create_game_invalid_category(self) -> None:
        """Test that creating a game with a non-existent category returns 400"""
        # Arrange
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        publisher_id = games[0]['publisher']['id']

        new_game = {
            "title": "Sprint Simulator",
            "description": "Plan, execute, and review sprints in this agile board game",
            "category_id": 999,
            "publisher_id": publisher_id
        }

        # Act
        response = self.client.post(
            self.GAMES_API_PATH,
            data=json.dumps(new_game),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_create_game_invalid_publisher(self) -> None:
        """Test that creating a game with a non-existent publisher returns 400"""
        # Arrange
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        category_id = games[0]['category']['id']

        new_game = {
            "title": "Sprint Simulator",
            "description": "Plan, execute, and review sprints in this agile board game",
            "category_id": category_id,
            "publisher_id": 999
        }

        # Act
        response = self.client.post(
            self.GAMES_API_PATH,
            data=json.dumps(new_game),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_create_game_validation_error(self) -> None:
        """Test that creating a game with an invalid title returns 400"""
        # Arrange - title too short (less than 2 characters)
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        category_id = games[0]['category']['id']
        publisher_id = games[0]['publisher']['id']

        new_game = {
            "title": "X",
            "description": "Plan, execute, and review sprints in this agile board game",
            "category_id": category_id,
            "publisher_id": publisher_id
        }

        # Act
        response = self.client.post(
            self.GAMES_API_PATH,
            data=json.dumps(new_game),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_create_game_no_body(self) -> None:
        """Test that creating a game without a request body returns 400"""
        # Act - no body, no content type
        response = self.client.post(self.GAMES_API_PATH)
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # --- UPDATE (PUT) tests ---

    def test_update_game_success(self) -> None:
        """Test successful update of an existing game"""
        # Arrange - get an existing game ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']

        update_data = {
            "title": "Pipeline Panic Updated",
            "star_rating": 5.0
        }

        # Act
        response = self.client.put(
            f'{self.GAMES_API_PATH}/{game_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], update_data['title'])
        self.assertEqual(data['starRating'], update_data['star_rating'])

    def test_update_game_not_found(self) -> None:
        """Test updating a game that does not exist returns 404"""
        # Act
        response = self.client.put(
            f'{self.GAMES_API_PATH}/999',
            data=json.dumps({"title": "Doesn't Matter"}),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_update_game_invalid_category(self) -> None:
        """Test updating a game with a non-existent category returns 400"""
        # Arrange
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']

        # Act
        response = self.client.put(
            f'{self.GAMES_API_PATH}/{game_id}',
            data=json.dumps({"category_id": 999}),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_update_game_invalid_publisher(self) -> None:
        """Test updating a game with a non-existent publisher returns 400"""
        # Arrange
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']

        # Act
        response = self.client.put(
            f'{self.GAMES_API_PATH}/{game_id}',
            data=json.dumps({"publisher_id": 999}),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_update_game_validation_error(self) -> None:
        """Test updating a game with an invalid title returns 400"""
        # Arrange
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']

        # Act
        response = self.client.put(
            f'{self.GAMES_API_PATH}/{game_id}',
            data=json.dumps({"title": "X"}),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_update_game_no_body(self) -> None:
        """Test updating a game without a request body returns 400"""
        # Arrange
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']

        # Act - no body, no content type
        response = self.client.put(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # --- DELETE tests ---

    def test_delete_game_success(self) -> None:
        """Test successful deletion of a game"""
        # Arrange - get an existing game ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        game_title = games[0]['title']

        # Act
        response = self.client.delete(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertIn(game_title, data['message'])

        # Verify the game no longer exists
        get_response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        self.assertEqual(get_response.status_code, 404)

    def test_delete_game_not_found(self) -> None:
        """Test deleting a game that does not exist returns 404"""
        # Act
        response = self.client.delete(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_delete_game_reduces_count(self) -> None:
        """Test that deleting a game reduces the total game count"""
        # Arrange - get initial count
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        initial_count = len(games)
        game_id = games[0]['id']

        # Act
        self.client.delete(f'{self.GAMES_API_PATH}/{game_id}')

        # Assert - count should be reduced by 1
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        self.assertEqual(len(games), initial_count - 1)

if __name__ == '__main__':
    unittest.main()