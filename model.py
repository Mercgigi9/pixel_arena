from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.orm import relationship,declarative_base
from datetime import datetime

Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    game= relationship("Game", back_populates="players")


class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    players_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    created_at = Column(DateTime, default=datetime)
    
    players = relationship("Player", back_populates="game")

    genres= relationship("Genre", back_populates="games")


    class Genre(Base):
        __tablename__ = 'genres'
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        games_id = Column(Integer, ForeignKey('games.id'), nullable=False)

        game= relationship("Game", back_populates="genres")