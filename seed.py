import requests
from database import SessionLocal
from model import Game, Genre

session = SessionLocal()

url = "https://www.freetogame.com/api/games?platform=pc"
api_games = requests.get(url).json()

for g in api_games:
    genre_name = g["genre"]
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if not genre:
        genre = Genre(name=genre_name)
        session.add(genre)
        session.commit()

    existing = session.query(Game).filter_by(title=g["title"]).first()
    if existing:
        continue

    new_game = Game(
        title=g["title"],
        description=g["short_description"],
        genre_id=genre.id
    )

    session.add(new_game)

session.commit()
session.close()

print("Games imported successfully!")