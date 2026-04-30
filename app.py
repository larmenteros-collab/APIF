import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("APISPORTS_KEY")

URL = "https://v3.football.api-sports.io/fixtures"

LEAGUES = {
    39: "Premier League",
    140: "LaLiga",
    78: "Bundesliga",
    135: "Serie A",
    61: "Ligue 1",
    88: "Eredivisie",
    94: "Primeira Liga",
    144: "Belgian Pro League",
    207: "Swiss Super League",
    179: "Scottish Premiership"
}


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Recolector de partidos funcionando",
        "endpoint": "/fixtures?date=YYYY-MM-DD"
    })


@app.route("/fixtures", methods=["GET"])
def fixtures():
    date = request.args.get("date")

    if not date:
        return jsonify({
            "date": None,
            "count": 0,
            "fixtures": [],
            "error": "Falta el parámetro date. Usa /fixtures?date=YYYY-MM-DD"
        }), 400

    if not API_KEY:
        return jsonify({
            "date": date,
            "count": 0,
            "fixtures": [],
            "error": "Falta la variable de entorno APISPORTS_KEY en Render"
        }), 500

    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        response = requests.get(
            URL,
            headers=headers,
            params={"date": date},
            timeout=20
        )
    except requests.RequestException as e:
        return jsonify({
            "date": date,
            "count": 0,
            "fixtures": [],
            "error": f"Error conectando con API-Football: {str(e)}"
        }), 500

    if response.status_code != 200:
        return jsonify({
            "date": date,
            "count": 0,
            "fixtures": [],
            "error": f"API-Football devolvió status {response.status_code}"
        }), 200

    data = response.json()
    games = data.get("response", [])

    filtered = []

    for game in games:
        league_id = game.get("league", {}).get("id")

        if league_id in LEAGUES:
            filtered.append({
                "league_id": league_id,
                "league": LEAGUES[league_id],
                "home": game.get("teams", {}).get("home", {}).get("name"),
                "away": game.get("teams", {}).get("away", {}).get("name"),
                "kickoff": game.get("fixture", {}).get("date"),
                "status": game.get("fixture", {}).get("status", {}).get("short")
            })

    return jsonify({
        "date": date,
        "count": len(filtered),
        "fixtures": filtered
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
