# Game model representing a board game available for crowdfunding on the platform.
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Game(BaseModel):
    """SQLAlchemy model representing a board game in the crowdfunding platform."""

    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    star_rating = db.Column(db.Float, nullable=True)
    
    # Foreign keys for one-to-many relationships
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)
    
    # One-to-many relationships (many games belong to one category/publisher)
    category = relationship("Category", back_populates="games")
    publisher = relationship("Publisher", back_populates="games")
    
    @validates('title')
    def validate_name(self, key: str, name: str) -> str:
        """Validate that the game title meets minimum length requirements.

        Args:
            key (str): The attribute name being validated ('title').
            name (str): The title value to validate.

        Returns:
            str: The validated title string.
        """
        return self.validate_string_length('Game title', name, min_length=2)
    
    @validates('description')
    def validate_description(self, key: str, description: str) -> str:
        """Validate that the game description meets minimum length requirements if provided.

        Args:
            key (str): The attribute name being validated ('description').
            description (str): The description value to validate.

        Returns:
            str: The validated description string, or None if None was provided.
        """
        if description is not None:
            return self.validate_string_length('Description', description, min_length=10, allow_none=True)
        return description
    
    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the Game instance.

        Returns:
            str: String containing the game title and ID.
        """
        return f'<Game {self.title}, ID: {self.id}>'

    def to_dict(self) -> dict:
        """Serialize the Game instance to a dictionary for JSON responses.

        Returns:
            dict: Dictionary containing id, title, description, publisher, category, and starRating.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publisher': {'id': self.publisher.id, 'name': self.publisher.name} if self.publisher else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'starRating': self.star_rating  # Changed from star_rating to starRating
        }