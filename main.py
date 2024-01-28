# from get_data import get_players_stats, get_teams_stats, get_players_advanced_stats, get_rookies_contracts, get_contracts_lengths
from clean_data import (
    clean_stats,
    unique_players,
    consolidate_personal_awards,
    consolidate_salary_cap,
    clean_personal_awards,
    clean_playoffs,
    clean_salaries,
    clean_contracts,
)
from transform_data import (
    games_played_perc,
    games_started_perc,
    total_minutes_played,
    average_minutes_played,
    winshares_per48,
    player_efficiency,
    player_age,
    # team_success,
    # team_scores,
    team_stage,
    team_playoffs_stage,
    salary_as_perc_of_cap,
    contract_status,
)
import pickle
import pandas as pd

from datetime import datetime

start = datetime.now()

years = list(range(2001, 2024))
years_contracts = list(range(1996, 2024))
game_types = ["playoffs", "leagues"]

# objects to hold stats
players_stats = {}
players_advanced_stats = {}
players_salaries = {}
players_contracts = {}
teams_stats = {}
playoffs = {}
distinct_players = pd.DataFrame(columns=["ID", "player"])

# stats that aren't need for model
players_columns_to_drop = [
    "Rk",
    "Pos",
    "MP",
    "FG",
    "FGA",
    "FG%",
    "3P",
    "3PA",
    "3P%",
    "2P",
    "2PA",
    "2P%",
    "eFG%",
    "FT",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
]
players_advanced_columns_to_drop = [
    "Rk",
    "Pos",
    "Age",
    "TS%",
    "3PAr",
    "FTr",
    "ORB%",
    "DRB%",
    "TRB%",
    "AST%",
    "STL%",
    "BLK%",
    "TOV%",
    "USG%",
    "OWS",
    "DWS",
    "WS/48",
    "BPM",
    "OBPM",
    "DBPM",
    "VORP",
]
teams_columns_to_drop = [
    "Rk",
    "FG",
    "FGA",
    "FG%",
    "3P",
    "3PA",
    "3P%",
    "2P",
    "2PA",
    "2P%",
    "FT",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
]

# scrap_start = datetime.now()
# print(f"########## Started data scrapping at {scrap_start} ##########")

# scrap necessary data
# get_players_stats(years, game_types)
# get_teams_stats(years, game_types)
# get_players_advanced_stats(years, game_types)
# get_rookies_contracts(years)
# get_contracts_lengths(years)

# scrap_finish = datetime.now()
# print(f"########## Finished data scrapping after {((scrap_finish - scrap_start).total_seconds())} seconds ##########")

cleanup_start = datetime.now()
print(f"########## Started data cleanup at: {cleanup_start} ##########")

# clean data
personal_awards_raw = consolidate_personal_awards()
salary_cap = consolidate_salary_cap()
for year in years:
    distinct_players = (
        pd.concat([distinct_players, unique_players(year)], ignore_index=True)
        .drop_duplicates(subset="ID", keep="first")
        .reset_index(drop=True)
    )
    teams_stats[year] = {}
    players_stats[year] = {}
    players_advanced_stats[year] = {}
    players_salaries[year] = {}
    players_salaries[year] = clean_salaries(year, distinct_players)
    playoffs[year] = {}
    playoffs[year] = clean_playoffs(year)
    for game_type in game_types:
        players_stats[year][game_type] = clean_stats(year, game_type, "players_stats", players_columns_to_drop)
        players_advanced_stats[year][game_type] = clean_stats(
            year, game_type, "players_advanced_stats", players_advanced_columns_to_drop
        )
        teams_stats[year][game_type] = clean_stats(year, game_type, "teams_stats", teams_columns_to_drop)
for year_contracts in years_contracts:
    players_contracts[year_contracts] = {}
    players_contracts[year_contracts] = clean_contracts(year_contracts, distinct_players)

personal_awards = clean_personal_awards(personal_awards_raw, distinct_players)

cleanup_finish = datetime.now()
print(
    f"########## Finished data cleanup after {((cleanup_finish - cleanup_start).total_seconds())} seconds ##########"
)

# store processed data in case of failure or for further data exploring
personal_awards.to_csv("./data/cleaned_data/personal_awards.csv", index=False, encoding="utf-8")
salary_cap.to_csv("./data/cleaned_data/salary_cap.csv", index=False, encoding="utf-8")
distinct_players.to_csv("./data/cleaned_data/distinct_players.csv", index=False, encoding="utf-8")

print(f"########## Finished storing data at: {datetime.now()} ##########")

transform_start = datetime.now()
print(f"########## Started data transformation at: {transform_start} ##########")

# transform data
stats = {}
stats_columns = [
    "ID",
    "salary_cap_perc",
    "last_year_of_contract",
    "age",
    "games_played_perc",
    "games_started_perc",
    "minutes_played",
    "avg_minutes_played",
    "WS48",
    "PER",
    "team_won_finals",
    "team_lost_finals",
    "team_lost_semifinals",
    "team_lost_first_match",
    "defensive",
    "most_improved",
    "most_valuable",
    "most_valuable_finals",
    "sixth_man",
    "all_league",
    "all_def",
]
playoffs_scores = {}
awards_columns = list(personal_awards.columns)
awards_columns.remove("year")
for year in years:
    print(f"########## Transformation of year {year} started at {datetime.now()} ##########")
    player_list = set(
        players_stats[year]["playoffs"]["ID"].values.tolist() + players_stats[year]["leagues"]["ID"].values.tolist()
    )
    stats[year] = pd.DataFrame(columns=stats_columns)
    playoffs_scores[year] = {}
    stats[year]["ID"] = [player for player in player_list]
    stats[year] = stats[year].set_index("ID")
    stats[year]["last_year_of_contract"] = "noinfo"
    stats[year] = stats[year].fillna(0)
    playoffs_scores[year] = team_playoffs_stage(playoffs[year])
    for player_id in player_list:
        stats[year]["games_played_perc"] = stats[year]["games_played_perc"].astype("float64")
        stats[year].loc[[f"{player_id}"], ["games_played_perc"]] = games_played_perc(
            player_id, game_types, players_stats[year], teams_stats[year]
        )
        stats[year]["games_started_perc"] = stats[year]["games_started_perc"].astype("float64")
        stats[year].loc[[f"{player_id}"], ["games_started_perc"]] = games_started_perc(
            player_id, game_types, players_stats[year], teams_stats[year]
        )
        stats[year].loc[[f"{player_id}"], ["minutes_played"]] = total_minutes_played(
            player_id, game_types, players_advanced_stats[year]
        )
        stats[year]["avg_minutes_played"] = stats[year]["avg_minutes_played"].astype("float64")
        stats[year].loc[[f"{player_id}"], ["avg_minutes_played"]] = average_minutes_played(
            player_id, game_types, players_advanced_stats[year]
        )
        stats[year].loc[[f"{player_id}"], ["team_won_finals"]] = team_stage(
            player_id, players_stats[year], playoffs_scores[year], stage="team_won_finals"
        )
        stats[year].loc[[f"{player_id}"], ["team_lost_finals"]] = team_stage(
            player_id, players_stats[year], playoffs_scores[year], stage="team_lost_finals"
        )
        stats[year].loc[[f"{player_id}"], ["team_lost_semifinals"]] = team_stage(
            player_id, players_stats[year], playoffs_scores[year], stage="team_lost_semifinals"
        )
        stats[year].loc[[f"{player_id}"], ["team_lost_first_match"]] = team_stage(
            player_id, players_stats[year], playoffs_scores[year], stage="team_lost_first_match"
        )
        stats[year]["WS48"] = stats[year]["WS48"].astype("float64")
        stats[year].loc[[f"{player_id}"], ["WS48"]] = winshares_per48(
            player_id, game_types, players_advanced_stats[year]
        )
        stats[year]["PER"] = stats[year]["PER"].astype("float64")
        stats[year].loc[[f"{player_id}"], ["PER"]] = player_efficiency(
            player_id, game_types, players_advanced_stats[year]
        )
        stats[year].loc[[f"{player_id}"], ["age"]] = player_age(player_id, players_stats[year])
        stats[year]["salary_cap_perc"] = stats[year]["salary_cap_perc"].astype("float64")
        stats[year].loc[[f"{player_id}"], ["salary_cap_perc"]] = salary_as_perc_of_cap(
            player_id, players_salaries[year], salary_cap, year
        )
    for column in awards_columns:
        player = personal_awards.query(f"year == {year}")[f"{column}"].iloc[0]
        if not pd.isna(player):
            if "all_" in column:
                stats_column = column.rsplit("_", 1)[0]
                stats[year].loc[player, [f"{stats_column}"]] = 1
            else:
                stats[year].loc[player, [f"{column}"]] = 1
for year_contracts in years_contracts:
    contract_status(players_contracts[year_contracts], stats)

# clean final stats from incomplete data
final_stats = {}
for year in years:
    final_stats[year] = pd.DataFrame()
    final_stats[year] = stats[year][
        (stats[year]["last_year_of_contract"] != "noinfo") & (stats[year]["salary_cap_perc"] != 0)
    ]

transform_finish = datetime.now()
print(
    f"########## Finished data transformation after {((transform_finish - transform_start).total_seconds())} seconds ##########"
)

# store final data
with open("./data/cleaned_data/final_stats.pickle", "wb") as final_statistics:
    pickle.dump(final_stats, final_statistics)

end = datetime.now()
print(f"########## The time of execution was {(end - start).total_seconds()} seconds ##########")
