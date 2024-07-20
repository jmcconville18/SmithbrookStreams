import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

PGA_API_KEY = 'e6bc2a9333msh2c319566291e932p1ded96jsn259d04576919'
PGA_API_HOST = 'golf-leaderboard-data.p.rapidapi.com'
PGA_FIXTURES_URL = 'https://golf-leaderboard-data.p.rapidapi.com/fixtures/2/2024'
PGA_LEADERBOARD_URL = 'https://golf-leaderboard-data.p.rapidapi.com/leaderboard/'

def fetch_pga_data():
    try:
        headers = {
            'X-RapidAPI-Key': PGA_API_KEY,
            'X-RapidAPI-Host': PGA_API_HOST
        }

        # Fetch fixtures
        logging.debug(f"Fetching fixtures from {PGA_FIXTURES_URL}")
        fixtures_response = requests.get(PGA_FIXTURES_URL, headers=headers)
        fixtures_response.raise_for_status()
        fixtures_data = fixtures_response.json()

        if 'results' not in fixtures_data:
            logging.error("Failed to fetch fixtures data: 'results' not in response")
            return {"error": "Failed to fetch fixtures data"}

        current_date = datetime.now().date()
        previous_tournament = None
        current_tournament = None
        next_tournament = None

        for tournament in fixtures_data['results']:
            start_date = datetime.strptime(tournament['start_date'], "%Y-%m-%d %H:%M:%S").date()
            end_date = datetime.strptime(tournament['end_date'], "%Y-%m-%d %H:%M:%S").date()

            if end_date < current_date:
                previous_tournament = tournament
            elif start_date <= current_date <= end_date:
                current_tournament = tournament
            elif start_date > current_date and next_tournament is None:
                next_tournament = tournament

        if not current_tournament and not previous_tournament:
            logging.error("No current or previous tournament found")
            return {"error": "No current or previous tournament found"}

        # Determine the tournament for the leaderboard
        leaderboard_tournament = current_tournament or previous_tournament
        leaderboard_url = f"{PGA_LEADERBOARD_URL}{leaderboard_tournament['id']}"

        # Fetch leaderboard
        logging.debug(f"Fetching leaderboard from {leaderboard_url}")
        leaderboard_response = requests.get(leaderboard_url, headers=headers)
        leaderboard_response.raise_for_status()
        leaderboard_data = leaderboard_response.json()

        league_json = {
            "league": "PGA Tour",
            "tournaments": {
                "previous": previous_tournament,
                "current": current_tournament,
                "next": next_tournament
            },
            "games": [],
        }

        if 'results' in leaderboard_data and 'leaderboard' in leaderboard_data['results']:
            for player in leaderboard_data['results']['leaderboard'][:10]:
                holes_played = player['holes_played'] if current_tournament else 'F'
                league_json["games"].append({
                    "player": f"{player['first_name']} {player['last_name']}",
                    "score": player['total_to_par'],
                    "holes": holes_played
                })

        return league_json

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": "Failed to fetch PGA scores"}
    except Exception as e:
        logging.error(f"Error fetching PGA scores: {e}")
        return {"error": "Failed to fetch PGA scores"}

