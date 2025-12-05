import fire
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Game, Genre
import requests

DATABASE_URL = "sqlite:///games.db"

def get_session():
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def fetch_and_store_games():
    session = get_session()
    url = "https://www.freetogame.com/api/games?platform=pc"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    for item in data:
        genre_name = item.get("genre", "Unknown")
        genre = session.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            session.add(genre)
            session.commit()

        game = Game(
            title=item.get("title"),
            description=item.get("short_description"),
            genre_id=genre.id
        )

        session.add(game)

    session.commit()
    return "Games imported from API."


def create_game(title: str, description: str, genre_name: str):
    session = get_session()

    genre = session.query(Genre).filter_by(name=genre_name).first()
    if not genre:
        genre = Genre(name=genre_name)
        session.add(genre)
        session.commit()

    game = Game(title=title, description=description, genre_id=genre.id)
    session.add(game)
    session.commit()

    return f"Game '{title}' created with ID {game.id}"

def list_games():
    session = get_session()
    games = session.query(Game).all()

    return [
        {"id": g.id, "title": g.title, "description": g.description, "genre": g.genre.name}
        for g in games
    ]


def get_game(game_id: int):
    session = get_session()
    game = session.query(Game).get(game_id)
    if not game:
        return f"No game found with ID {game_id}"

    return {
        "id": game.id,
        "title": game.title,
        "description": game.description,
        "genre": game.genre.name,
    }

def update_game(game_id: int, title=None, description=None, genre_name=None):
    session = get_session()
    game = session.query(Game).get(game_id)
    if not game:
        return f"No game found with ID {game_id}"

    if title:
        game.title = title

    if description:
        game.description = description

    if genre_name:
        genre = session.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            session.add(genre)
            session.commit()
        game.genre_id = genre.id

    session.commit()
    return f"Game {game_id} updated."


def delete_game(game_id: int):
    session = get_session()
    game = session.query(Game).get(game_id)
    if not game:
        return f"No game found with ID {game_id}"

    session.delete(game)
    session.commit()

    return f"Game {game_id} deleted."


if __name__ == "__main__":
    fire.Fire({
        "fetch_and_store_games": fetch_and_store_games,
        "create": create_game,
        "list": list_games,
        "get": get_game,
        "update": update_game,
        "delete": delete_game
    })
    
