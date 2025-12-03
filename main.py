import fire
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Game, Genre
import requests

DATABASE_URL = "sqlite:///games.db"   

def init_db():
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    Session = SessionLocal()
    return Session

def fetch_and_store_games(session):
    url = "https://www.freetogame.com/api/games?platform=pc"   
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def save_to_database(data):
    session = requests.Session()

    for item in data:
        genre_name = item.get("genre", "Unknown")
        genre = session.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            session.add(genre)
            session.commit()

        
        game = Game(
            title=item.get("title"),
            rating=item.get("rating")
        )
        session.add(game)

    session.commit()
    print("Games added from API.")

if __name__ == "__main__":
    fire.Fire({
        "init_db": init_db,
        "fetch_and_store_games": fetch_and_store_games,
        "save_to_database": save_to_database
    })

    # session = init_db()
    # fetch_and_store_games(session)
    # print("Database Initialized.")

    
