import pandas as pd

distinct_teams = pd.read_csv('./data/cleaned_data/distinct_teams.csv')

def games_played_perc(player_id: str, game_types: list, players_stats: pd.DataFrame, teams_stats: pd.DataFrame):
    """Return games played for each player as % of total games played by team"""
    games_played = 0
    team_games_played = 0
    for game_type in game_types:
        try:
            player_team = players_stats[game_type].query(f"ID == '{player_id}'")["Tm"].iloc[0]
        except:
            pass
        try:
            games_played += players_stats[game_type].query(f"ID == '{player_id}'")["G"].iloc[0]
        except:
            pass
        try:
            team_games_played += teams_stats[game_type].query(f"Team == '{player_team}'")["G"].iloc[0]
        except:
            pass

    perc_games_played = games_played / team_games_played

    return perc_games_played


def games_started_perc(player_id: str, game_types: list, players_stats: pd.DataFrame, teams_stats: pd.DataFrame):
    """Return games started for each player as % of total games played by team"""
    games_started = 0
    team_games_played = 0
    for game_type in game_types:
        try:
            player_team = players_stats[game_type].query(f"ID == '{player_id}'")["Tm"].iloc[0]
        except:
            pass
        try:
            games_started += players_stats[game_type].query(f"ID == '{player_id}'")["GS"].iloc[0]
        except:
            pass
        try:
            team_games_played += teams_stats[game_type].query(f"Team == '{player_team}'")["G"].iloc[0]
        except:
            pass

    perc_games_started = games_started / team_games_played

    return perc_games_started


def average_minutes_played(player_id: str, game_types: list, players_stats: pd.DataFrame):
    """Return average minutes played for each player as % of total games played by team"""
    avg_minutes_played = 0
    avg_minutes_played_x_games = 0
    total_games = 0
    minutes_played_per_game = 0
    games_played = 0
    for game_type in game_types:
        try:
            minutes_played_per_game = players_stats[game_type].query(f"ID == '{player_id}'")["MP"].iloc[0]
            games_played = players_stats[game_type].query(f"ID == '{player_id}'")["G"].iloc[0]
        except:
            minutes_played_per_game += 0
            games_played += 0

        avg_minutes_played_x_games += minutes_played_per_game * games_played
        total_games += games_played

    if total_games != 0:
        avg_minutes_played = round(avg_minutes_played_x_games/total_games, 2)
    else:
        avg_minutes_played = 0

    return avg_minutes_played


def winshares_per48(player_id: str, game_types: list, players_stats: pd.DataFrame, players_advanced_stats: pd.DataFrame):
    """Return win shares per 48 minutes for each player"""
    minutes_played = 0
    win_shares = 0
    win_share_48 = 0
    for game_type in game_types:
        try:
            minutes_played = players_stats[game_type].query(f"ID == '{player_id}'")["MP"].iloc[0]
            win_shares = players_advanced_stats[game_type].query(f"ID == '{player_id}'")["WS"].iloc[0]
        except:
            minutes_played += 0
            win_shares += 0

    if minutes_played != 0:
        win_share_48 = round((win_shares/minutes_played) * 48, 2)
    else:
        win_share_48 = 0

    return win_share_48


def player_age(player_id: str, players_stats: pd.DataFrame):
    """Return age for each player"""
    try:
        age = players_stats["leagues"].query(f"ID == '{player_id}'")["Age"].iloc[0]
    except:
        age = players_stats["playoffs"].query(f"ID == '{player_id}'")["Age"].iloc[0]

    return age


def team_scores(playoffs: pd.DataFrame):
    """Converts team playoffs games to scores"""
    scores = distinct_teams.copy()
    scores['score'] = 0
    for index, row in scores.iterrows():
        team = row["ID"]
        check_team_history = playoffs[playoffs.isin([f'{team}'])].stack()
        if check_team_history.empty:
            pass
        else:
            stage_id = check_team_history.index[0][0]
            if stage_id == 0:
                stage_outcome = check_team_history.index[0][1]
                if stage_outcome == "winner":
                    scores.loc[index, 'score'] = 5
                else:
                    scores.loc[index, 'score'] = 3
            elif stage_id in [1, 2]:
                scores.loc[index, 'score'] = 2
            elif stage_id in list(range(3, 15)):
                scores.loc[index, 'score'] = 1

    return scores


def team_success(player_id: str, players_stats: pd.DataFrame, playoffs_scores: pd.DataFrame):
    """Returns team score from playoffs"""
    try:
        player_team = players_stats["leagues"].query(f"ID == '{player_id}'")["Tm"].iloc[0]
    except:
        player_team = players_stats["playoffs"].query(f"ID == '{player_id}'")["Tm"].iloc[0]

    success = playoffs_scores.query(f"ID == '{player_team}'")["score"].iloc[0]

    return success