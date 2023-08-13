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


def total_minutes_played(player_id: str, game_types: list, players_advanced_stats: pd.DataFrame):
    """Return minutes played for each player"""
    minutes_played = 0
    for game_type in game_types:
        try:
            minutes_played += players_advanced_stats[game_type].query(f"ID == '{player_id}'")["MP"].iloc[0]
        except:
            pass

    return minutes_played


def average_minutes_played(player_id: str, game_types: list, players_advanced_stats: pd.DataFrame):
    """Return average minutes played for each player"""
    avg_minutes_played = 0
    minutes_played = 0
    total_games = 0
    for game_type in game_types:
        try:
            minutes_played += players_advanced_stats[game_type].query(f"ID == '{player_id}'")["MP"].iloc[0]
            total_games += players_advanced_stats[game_type].query(f"ID == '{player_id}'")["G"].iloc[0]
        except:
            pass

    if total_games != 0:
        avg_minutes_played = round(minutes_played/total_games, 3)

    return avg_minutes_played


def winshares_per48(player_id: str, game_types: list, players_advanced_stats: pd.DataFrame):
    """Return win shares per 48 minutes for each player"""
    minutes_played = 0
    win_shares = 0
    win_share_48 = 0
    for game_type in game_types:
        try:
            minutes_played = players_advanced_stats[game_type].query(f"ID == '{player_id}'")["MP"].iloc[0]
            win_shares = players_advanced_stats[game_type].query(f"ID == '{player_id}'")["WS"].iloc[0]
        except:
            pass

    if minutes_played != 0:
        win_share_48 = round((win_shares/minutes_played) * 48, 3)

    return win_share_48


def player_efficiency(player_id: str, game_types: list, players_advanced_stats: pd.DataFrame):
    """Return Player Efficiency Rating for each player"""
    minutes_played = 0
    efficiency = 0
    efficiency_x_minutes = 0
    efficiency_total = 0
    for game_type in game_types:
        try:
            minutes_played = players_advanced_stats[game_type].query(f"ID == '{player_id}'")["MP"].iloc[0]
            efficiency = players_advanced_stats[game_type].query(f"ID == '{player_id}'")["PER"].iloc[0]

            efficiency_x_minutes += efficiency * minutes_played
        except:
            pass

    if minutes_played != 0:
        efficiency_total = round((efficiency_x_minutes/minutes_played), 3)
    else:
        efficiency_total = 0

    return efficiency_total


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


def salary_as_perc_of_cap(player_id: str, players_salaries: pd.DataFrame, salary_cap: pd.DataFrame, year: int):
    """Returns player earnigns as percent of salary cap"""

    try:
        salary = int(players_salaries.query(f"ID == '{player_id}'")["salary"].iloc[0])
        salary_cap = int(salary_cap.query(f"year == {year}")["salary_cap"].iloc[0])

        salary_perc = round(salary / salary_cap, 3)
    except:
        salary_perc = 0

    return salary_perc


def contract_status(players_contracts: pd.DataFrame, stats):
    """Fills stats with contract info"""

    for index, row in players_contracts.iterrows():
        player_id = players_contracts.loc[index, 'player']
        previous_contract_end = players_contracts.loc[index, "season"] - 1
        contract_end = players_contracts.loc[index, "season"] + players_contracts.loc[index, "contract_length"]
        contract_seasons = list(range(previous_contract_end, contract_end))
        for con_season in contract_seasons:
            if con_season != contract_seasons[0] and con_season != contract_seasons[-1]:
                try:
                    stats[con_season].loc[[f'{player_id}'], ['last_year_of_contract']] = False
                except:
                    pass
            else:
                try:
                    stats[con_season].loc[[f'{player_id}'], ['last_year_of_contract']] = True
                except:
                    pass