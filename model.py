from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    games = relationship("Game", back_populates="genre")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)

    genre = relationship("Genre", back_populates="games")
    reviews = relationship("PlayerGame", back_populates="game")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    reviews = relationship("PlayerGame", back_populates="player")

class PlayerGame(Base):
    __tablename__ = "player_games"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    review = Column(Text)
    datetime = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="reviews")
    game = relationship("Game", back_populates="reviews")

