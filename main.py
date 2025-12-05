import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Game, Genre, Player, PlayerGame


console = Console()
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
    console.print("[green]Games imported successfully![/green]")

from rich.table import Table
from rich.console import Console

console = Console()

def list_players(session):
    players = session.query(Player).all()

    table = Table(title="Players List")
    table.add_column("ID", justify="center", style="bold cyan")
    table.add_column("Username", style="bold white")
    table.add_column("Email", style="white")

    if not players:
        console.print("[yellow]No players found.[/yellow]")
        return

    for player in players:
        table.add_row(str(player.id), player.name, player.email)

    console.print(table)

def create_account(session):
    name = Prompt.ask("Enter a username")
    email = Prompt.ask("Enter your email (optional)", default="")
    existing = session.query(Player).filter_by(name=name).first()
    if existing:
        console.print("[red]Username already exists.[/red]")
        return None

    player = Player(name=name,email=email)
    session.add(player)
    session.commit()

    console.print(f"[green]Account created! Your ID: {player.id}[/green]")
    return player


def login(session):
    name = Prompt.ask("Enter username")
    player = session.query(Player).filter_by(name=name).first()
    if not player:
        console.print("[red]No such user. Create an account first.[/red]")
        return None
    console.print(f"[green]Logged in as {player.name}![/green]")
    return player

def list_games(session):
    games = session.query(Game).all()

    table = Table(title="Games List")

    table.add_column("ID", justify="center", style="bold cyan")
    table.add_column("Title", style="bold white")

    for game in games:
        table.add_row(str(game.id), game.title)

    console.print(table)


def view_game_details(session, game_id):
    game = session.query(Game).get(game_id)
    if not game:
        console.print("[red]Game not found.[/red]")
        return None

    console.print(f"[bold]{game.title}[/bold]")
    console.print(f"Genre: [cyan]{game.genre.name}[/cyan]")
    console.print(f"Description: {game.description}")

    reviews = session.query(PlayerGame).filter_by(game_id=game_id).all()
    if reviews:
        table = Table(title="Reviews")
        table.add_column("Player")
        table.add_column("Review")
        table.add_column("Date")

        for r in reviews:
            table.add_row(r.player.name, r.review or "", str(r.datetime))

        console.print(table)
    else:
        console.print("[yellow]No reviews yet.[/yellow]")

    return game

def leave_review(session, player, game):
    console.print("Write your review (leave blank to cancel):")
    review = Prompt.ask("Review")
    if not review.strip():
        console.print("[yellow]Review cancelled.[/yellow]")
        return

    entry = PlayerGame(player_id=player.id, game_id=game.id, review=review)
    session.add(entry)
    session.commit()
    console.print("[green]Review submitted![/green]")
    
def main():
    session = get_session()

    console.print("[bold cyan]Welcome to the Game CLI![/bold cyan]")

    while True:
        print("""
=== MAIN MENU ===
1. Login
2. Create Account
3. Import Games
4. Exit
""")

        choice_map = {
            "1": "login",
            "2": "create",
            "3": "import",
            "4": "exit"
        }

        num_choice = input("Choose option: ").strip()
        choice = choice_map.get(num_choice, None)

        if choice is None:
            console.print("[red]Invalid option. Try again.[/red]")
            continue

        if choice == "create":
            user = create_account(session)
        elif choice == "login":
            user = login(session)
        elif choice == "import":
            fetch_and_store_games()
            continue
        elif choice == "exit":
            console.print("Goodbye!")
            return

        if not user:
            continue
        while True:
            print(f"""
=== USER MENU ===
1. View Games
2. View Players
3. Logout
4. Exit
""")

            user_choice_map = {
                "1": "games",
                "2": "players",
                "3": "logout",
                "4": "exit"
            }

            num_action = input("Choose option: ").strip()
            action = user_choice_map.get(num_action, None)

            if action is None:
                console.print("[red]Invalid option. Try again.[/red]")
                continue

            if action == "games":
                list_games(session)
                game_id = IntPrompt.ask("Enter game ID to view or 0 to cancel", default=0)
                if game_id == 0:
                    continue
                game = view_game_details(session, game_id)
                if game:
                    sub = Prompt.ask("Leave a review?", choices=["yes", "no"], default="no")
                    if sub == "yes":
                        leave_review(session, user, game)

            elif action == "players":
                list_players(session)

            elif action == "logout":
                break

            elif action == "exit":
                console.print("Goodbye!")
                return
            
if __name__ == "__main__":
    main()