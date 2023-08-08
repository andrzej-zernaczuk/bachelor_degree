from get_data import get_players_stats, get_team_stats, get_players_advanced_stats, get_rookies_contracts
from clean_data import clean_stats, unique_players, consolidate_personal_awards, consolidate_salary_cap, clean_personal_awards, clean_playoffs, clean_salaries
from transform_data import games_played_perc, games_started_perc, average_minutes_played, winshares_per48, player_age, team_success, team_scores, salary_as_perc_of_cap
import pickle
import pandas as pd

from datetime import datetime
start = datetime.now()

years = list(range(2001, 2024))
game_types = ["playoffs", "leagues"]

# objects to hold stats
players_stats = {}
players_advanced_stats = {}
players_salaries = {}
teams_stats = {}
playoffs = {}
distinct_players = pd.DataFrame(columns=["ID", "player"])

# stats that aren't need for model
players_columns_to_drop = ['Rk', 'Pos', 'FG', 'FGA', 'FG%', '3P',
                    '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%',
                    'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB',
                    'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
players_advanced_columns_to_drop = ['Rk', 'Pos', 'Age', 'MP', 'PER',
                    'TS%', '3PAr', 'FTr', 'ORB%', 'DRB%', 'TRB%',
                    'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS',
                    'DWS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']
teams_columns_to_drop = ['Rk', 'FG', 'FGA', 'FG%', '3P',
                    '3PA', '3P%', '2P', '2PA', '2P%',
                    'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB',
                    'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

scrap_start = datetime.now()
print(f"########## Started data scrapping at {scrap_start} ##########")

# scrap necessary data
# get_players_stats(years, game_types)
# get_team_stats(years, game_types)
# get_players_advanced_stats(years, game_types)
# get_rookies_contracts(years)

scrap_finish = datetime.now()
print(f"########## Finished data scrapping after {((scrap_finish - scrap_start).total_seconds())} seconds ##########")

cleanup_start = datetime.now()
print(f"########## Started data cleanup at: {cleanup_start} ##########")

# clean data
personal_awards_raw = consolidate_personal_awards()
salary_cap = consolidate_salary_cap()
for year in years:
    distinct_players = (
        pd.concat([distinct_players, unique_players(year)], ignore_index=True)
        .drop_duplicates(subset='ID', keep="first")
        .reset_index(drop=True)
    )
    players_stats[year] = {}
    players_advanced_stats[year] = {}
    players_salaries[year] = {}
    players_salaries[year] = clean_salaries(year, distinct_players)
    teams_stats[year] = {}
    playoffs[year] = {}
    playoffs[year] = clean_playoffs(year)
    for game_type in game_types:
        players_stats[year][game_type] = clean_stats(year, game_type, "players_stats", players_columns_to_drop)
        players_advanced_stats[year][game_type] = clean_stats(year, game_type, "players_advanced_stats", players_advanced_columns_to_drop)
        teams_stats[year][game_type] = clean_stats(year, game_type, "teams_stats", teams_columns_to_drop)

personal_awards = clean_personal_awards(personal_awards_raw, distinct_players)

cleanup_finish = datetime.now()
print(f"########## Finished data cleanup after {((cleanup_finish - cleanup_start).total_seconds())} seconds ##########")

# store processed data in case of failure or for further data exploring
personal_awards.to_csv('./data/cleaned_data/personal_awards.csv', index=False, encoding='utf-8')
salary_cap.to_csv('./data/cleaned_data/salary_cap.csv', index=False, encoding='utf-8')
distinct_players.to_csv('./data/cleaned_data/distinct_players.csv', index=False, encoding='utf-8')
with open('./data/cleaned_data/players_stats.pickle', 'wb') as play_stats:
    pickle.dump(players_stats, play_stats)
with open('./data/cleaned_data/players_advanced_stats.pickle', 'wb') as play_adv_stats:
    pickle.dump(players_advanced_stats, play_adv_stats)
with open('./data/cleaned_data/players_salaries.pickle', 'wb') as play_salaries:
    pickle.dump(players_salaries, play_salaries)
with open('./data/cleaned_data/teams_stats.pickle', 'wb') as team_stats:
    pickle.dump(teams_stats, team_stats)
with open('./data/cleaned_data/playoffs.pickle', 'wb') as playoff:
    pickle.dump(playoffs, playoff)

print(f"########## Finished storing data at: {datetime.now()} ##########")

transform_start = datetime.now()
print(f"########## Started data transformation at: {transform_start} ##########")

# transform data
stats = {}
stats_columns = ["ID", "salary_perc", "age", "games_played_perc", "games_started_perc", "avg_minutes_played", "WS48", "team_successes",
              "defensive", "most_improved", "most_valuable", "most_valuable_finals", "sixth_man", "all_league", "all_def"]
playoffs_scores = {}
awards_columns = list(personal_awards.columns)
awards_columns.remove('year')
for year in years:
    print(f"########## Transformation of year {year} started at {datetime.now()} ##########")
    player_list = set(players_stats[year]["playoffs"]["ID"].values.tolist() + players_stats[year]["leagues"]["ID"].values.tolist())
    stats[year] = pd.DataFrame(columns=stats_columns)
    playoffs_scores[year] = {}
    stats[year]['ID'] = [player for player in player_list]
    stats[year] = stats[year].set_index("ID")
    stats[year] = stats[year].fillna(0)
    playoffs_scores[year] = team_scores(playoffs[year])
    for player_id in player_list:
        stats[year].loc[[f'{player_id}'], ['games_played_perc']] = games_played_perc(player_id, game_types, players_stats[year], teams_stats[year])
        stats[year].loc[[f'{player_id}'], ['games_started_perc']] = games_started_perc(player_id, game_types, players_stats[year], teams_stats[year])
        stats[year].loc[[f'{player_id}'], ['avg_minutes_played']] = average_minutes_played(player_id, game_types, players_stats[year])
        stats[year].loc[[f'{player_id}'], ['team_successes']] = team_success(player_id, players_stats[year], playoffs_scores[year])
        stats[year].loc[[f'{player_id}'], ['WS48']] = winshares_per48(player_id, game_types, players_stats[year], players_advanced_stats[year])
        stats[year].loc[[f'{player_id}'], ['age']] = player_age(player_id, players_stats[year])
        stats[year].loc[[f'{player_id}'], ['salary_perc']] = salary_as_perc_of_cap(player_id, players_salaries[year], salary_cap, year)
    for column in awards_columns:
        player = personal_awards.query(f"year == {year}")[f"{column}"].iloc[0]
        if not pd.isna(player):
            if "all_" in column:
                stats_column = column.rsplit("_", 1)[0]
                stats[year].loc[player, [f"{stats_column}"]] = 1
            else:
                stats[year].loc[player, [f"{column}"]] = 1

transform_finish = datetime.now()
print(f"########## Finished data transformation after {((transform_finish - transform_start).total_seconds())} seconds ##########")

# store transformed data
with open('./data/final_stats.pickle', 'wb') as final_stats:
    pickle.dump(stats, final_stats)

end = datetime.now()
print(f"########## The time of execution was {(end - start).total_seconds()} seconds ##########")