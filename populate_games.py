from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
import requests
from datetime import datetime
import traceback


API_GAMES_URL = "https://aoe4world.com/api/v0/players/{player_id}/games?leaderboard=rm_solo"
API_GAME_DETAIL_URL = "https://aoe4world.com/api/v0/players/{player_id}/games/{game_id}?leaderboard=rm_solo"

PLAYER_IDS = [
    "22969958",
    "23054027",
    "24033333",
    "76561198092584942",
]

STATE_FILE = Path("latest_games.json")
TEMPLATE_FILE = Path("game-template.md")
OUTPUT_DIR = Path("docs/Video Games/AOE4/Game History/Chinese")

REQUEST_TIMEOUT = 20


def extract_year_month(date_str: str) -> tuple[str, str]:
    """
    Converts:
    2026-03-11 -> ("2026", "03")
    """
    parts = date_str.split("-")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return "", ""


def extract_date(started_at: str) -> str:
    """
    Converts:
    2026-03-11T13:20:40.000Z
    -> 2026-03-11
    """
    try:
        dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except Exception:
        return ""

def load_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {player_id: "" for player_id in PLAYER_IDS}

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    for player_id in PLAYER_IDS:
        data.setdefault(player_id, "")

    return data


def save_state(path: Path, state: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)
        f.write("\n")


def fetch_games(player_id: str) -> list[dict[str, Any]]:
    url = API_GAMES_URL.format(player_id=player_id)
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict):
        games = data.get("games", [])
    elif isinstance(data, list):
        games = data
    else:
        raise ValueError(f"Unexpected response type for player {player_id}: {type(data)}")

    if not isinstance(games, list):
        raise ValueError(f"'games' is not a list for player {player_id}")

    return games


def fetch_game_detail(player_id: str, game_id: str) -> dict[str, Any]:
    url = API_GAME_DETAIL_URL.format(player_id=player_id, game_id=game_id)
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(f"Unexpected detail response for player {player_id}, game {game_id}")

    return data


def get_new_games(games: list[dict[str, Any]], last_seen_game_id: str) -> list[dict[str, Any]]:
    new_games: list[dict[str, Any]] = []

    for game in games:
        game_id = str(game.get("game_id", "")).strip()
        if not game_id:
            continue

        if game_id == last_seen_game_id:
            break

        new_games.append(game)

    return new_games


def sanitize_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[^\w.-]+", "_", value)
    return value[:200] if value else "unnamed"


def normalize_civ(civ: str) -> str:
    return civ.lower().replace(" ", "-")


def render_template(template_text: str, variables: dict[str, str]) -> str:
    pattern = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return variables.get(key, "")

    return pattern.sub(replace, template_text)


def format_duration(seconds: Any) -> str:
    try:
        total_seconds = int(seconds)
    except (TypeError, ValueError):
        return ""

    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


def find_player_and_enemy_teams(game_detail: dict[str, Any], our_profile_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    teams = game_detail.get("teams", [])
    if not isinstance(teams, list) or len(teams) < 2:
        raise ValueError("Expected at least 2 teams in game detail")

    team0 = teams[0][0]
    team1 = teams[1][0]

    print(team0)
    print(team1)

    team0_profile_id = str(team0.get("profile_id", ""))
    team1_profile_id = str(team1.get("profile_id", ""))

    if team0_profile_id == our_profile_id:
        return team0, team1
    if team1_profile_id == our_profile_id:
        return team1, team0

    raise ValueError(
        f"Could not find our profile_id {our_profile_id} in teams[0]/teams[1].profile_id"
    )


def build_template_variables(
    player_id: str,
    game_id: str,
    game_detail: dict[str, Any],
) -> dict[str, str]:
    player_team, enemy_team = find_player_and_enemy_teams(game_detail, player_id)

    aoe4_url = API_GAME_DETAIL_URL.format(player_id=player_id, game_id=game_id)

    date = extract_date(game_detail.get("started_at", ""))

    variables = {
        "player_id": player_id,
        "game_id": game_id,
        "aoe4_url": aoe4_url,
        "date": date,
        "map_name": str(game_detail.get("map", "")),
        "username": str(player_team.get("name", "")),
        "enemy_account": str(enemy_team.get("name", "")),
        "civilization": str(normalize_civ(player_team.get("civilization", ""))),
        "opponent_civ": str(normalize_civ(enemy_team.get("civilization", ""))),
        "match_result": str(player_team.get("result", "")),
        "duration": format_duration(game_detail.get("duration")),
    }

    return variables


def write_game_file(
    output_dir: Path,
    template_text: str,
    player_id: str,
    game_id: str,
    game_detail: dict[str, Any],
) -> None:
    variables = build_template_variables(
        player_id=player_id,
        game_id=game_id,
        game_detail=game_detail,
    )

    rendered = template_text.format(**variables)

    year, month = extract_year_month(variables["date"])

    civ_dir = sanitize_filename(variables["civilization"].lower())
    target_dir = output_dir / civ_dir / year / month
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(f"{variables['date']}-vs-{variables['opponent_civ']}-{game_id}.md")
    output_path = target_dir / filename
    output_path.write_text(rendered, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template file not found: {TEMPLATE_FILE}")

    template_text = TEMPLATE_FILE.read_text(encoding="utf-8")
    state = load_state(STATE_FILE)

    for player_id in PLAYER_IDS:
        print(f"Checking player {player_id}...")

        try:
            games = fetch_games(player_id)
        except Exception as exc:
            print(f"  Failed to fetch games list: {exc}")
            traceback.print_exc()
            continue

        if not games:
            print("  No games returned.")
            continue

        last_seen_game_id = str(state.get(player_id, "")).strip()
        new_games = get_new_games(games, last_seen_game_id)

        if not new_games:
            print("  No new games found.")
            continue

        # oldest -> newest
        for game in reversed(new_games):
            game_id = str(game.get("game_id", "")).strip()
            if not game_id:
                continue

            try:
                game_detail = fetch_game_detail(player_id, game_id)
                write_game_file(
                    output_dir=OUTPUT_DIR,
                    template_text=template_text,
                    player_id=player_id,
                    game_id=game_id,
                    game_detail=game_detail,
                )
                print(f"  Wrote game file for {game_id}")
            except Exception as exc:
                print(f"  Failed processing game {game_id}: {exc}")
                traceback.print_exc()

        newest_game_id = str(games[0].get("game_id", "")).strip()
        if newest_game_id:
            state[player_id] = newest_game_id
            print(f"  Updated latest game ID to {newest_game_id}")

    save_state(STATE_FILE, state)
    print("Done.")


if __name__ == "__main__":
    main()