import http
import requests
import json

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


def get_player_stats(api_key, player_id, season):
    conn.request(
        "GET",
        f"/players?id={player_id}&season={season}",
        headers={"x-apisports-key": api_key},
    )

    res = conn.getresponse()
    data = res.read()
    all_data = data.decode("utf-8")
    print(all_data)

    if not json.loads(all_data)["response"]:
        return None

    # TODO: handle cases where statistics don't have the right team in first position
    # see Portland Thorns 2025 J. Fleming for an example that came up as soon as I thought about it
    return json.loads(all_data)["response"][0]["statistics"][0]
