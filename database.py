from sqlalchemy import Column, String, Integer, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from config import Base


# Table to store reviews
class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    product_id = Column(String)
    review_text = Column(String)
    review_sentiment_score = Column(Float)
    review_sentiment_magnitude = Column(Float)
    review_analyzed = Column(Boolean, default=False)

    def __init__(self, product_id, review_text, review_analyzed=None):
        self.product_id = product_id
        self.review_text = review_text
        self.review_analyzed = review_analyzed or False


# Table to store entities
# An entity can have different sentiment and salience in different reviews
# that's why Many to one relation is kept
class Entity(Base):
    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True)
    entity_name = Column(String)
    salience = Column(Float)
    sentiment_score = Column(Float)
    sentiment_magnitude = Column(Float)
    review_id = Column(Integer, ForeignKey('review.id'))
    review = relationship("Review", backref="entities")

    def __init__(self, entity_name, salience, sentiment_score, sentiment_magnitude, review_id):
        self.entity_name = entity_name
        self.salience = salience
        self.sentiment_score = sentiment_score
        self.sentiment_magnitude = sentiment_magnitude
        self.review_id = review_id
