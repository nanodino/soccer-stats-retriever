import http
import requests
import json
import pandas as pd

base_url = "v3.football.api-sports.io"
conn = http.client.HTTPSConnection(base_url)


def get_leagues(api_key):
    conn.request("GET", "/leagues", headers={"x-apisports-key": api_key})

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    return json.loads(all_data)["response"]


def get_league_seasons(api_key):
    conn.request(
        "GET",
        f"/leagues/seasons",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    return json.loads(all_data)["response"]


def get_teams(api_key, league_id, season):
    conn.request(
        "GET",
        f"/teams?league={league_id}&season={season}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    return json.loads(all_data)["response"]


def get_team_players(api_key, team_id, season):
    conn.request(
        "GET",
        f"/players?team={team_id}&season={season}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    return json.loads(all_data)["response"]


def get_player_stats(api_key, player_id, team_id, season):
    conn.request(
        "GET",
        f"/players?id={player_id}&season={season}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")

    response_data = json.loads(all_data)["response"]
    if not response_data:
        return None

    player_data = response_data[0]
    statistics = player_data["statistics"]

    team_stats = next(
        (stat for stat in statistics if stat["team"]["id"] == team_id),
        None,
    )

    return team_stats


def get_rounds(api_key, league_id, season):
    conn.request(
        "GET",
        f"/fixtures/rounds?league={league_id}&season={season}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    return json.loads(all_data)["response"]


def get_fixtures(api_key, league_id, season):
    conn.request(
        "GET",
        f"/fixtures?league={league_id}&season={season}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    return json.loads(all_data)["response"]


def get_fixture_stats(api_key, fixture_id):
    conn.request(
        "GET",
        f"/fixtures/statistics?fixture={fixture_id}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    response_data = json.loads(all_data)["response"]

    if not response_data:
        return None

    stats_data = {}

    for team_data in response_data:
        team_name = team_data["team"]["name"]
        statistics = team_data["statistics"]

        team_stats = {}
        for stat in statistics:
            stat_type = stat["type"]
            stat_value = stat["value"]
            team_stats[stat_type] = stat_value

        stats_data[team_name] = team_stats

    df = pd.DataFrame(stats_data)

    return df


def get_fixture_player_stats(api_key, fixture_id):
    print(f"fixture_id: {fixture_id}")
    conn.request(
        "GET",
        f"/fixtures/players?fixture={fixture_id}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    response_data = json.loads(all_data)["response"]

    if not response_data:
        return None

    all_players = []

    for team_data in response_data:
        team_name = team_data["team"]["name"]

        for player_data in team_data["players"]:
            player_info = player_data["player"]
            stats = player_data["statistics"][0]

            player_row = {
                "team": team_name,
                "player_id": player_info["id"],
                "player_name": player_info["name"],
                "position": player_info.get("pos", "N/A"),
                "number": player_info.get("number", "N/A"),
                "minutes": stats["games"]["minutes"],
                "rating": stats["games"]["rating"],
                "goals": stats["goals"]["total"],
                "assists": stats["goals"]["assists"],
                "passes_total": stats["passes"]["total"],
                "passes_accuracy": stats["passes"]["accuracy"],
                "tackles": stats["tackles"]["total"],
                "fouls_committed": stats["fouls"]["committed"],
                "cards_yellow": stats["cards"]["yellow"],
                "cards_red": stats["cards"]["red"],
            }

            all_players.append(player_row)

    return pd.DataFrame(all_players)
