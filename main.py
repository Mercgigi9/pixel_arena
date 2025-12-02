import requests
from model import SessionLocal, Game, Genre

def fetch_games_from_api():
    url = "https://www.freetogame.com/api/games?platform=pc"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def save_to_database(data):
    session = SessionLocal()

    for item in data:
        genre_name = item.get("genre", "Unknown")
        genre = session.query(Genre).filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            session.add(genre)
            session.commit()

        
        game = Game(
            title=item["title"],
            rating=item["rating"],
            genre_id=genre.id,
        )
        session.add(game)

    session.commit()
    session.close()

def main():
    data = fetch_games_from_api()
    save_to_database(data)
    print("Data saved successfully!")

