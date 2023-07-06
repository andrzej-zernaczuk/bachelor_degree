from get_data import get_players_stats, get_team_stats, get_players_advanced_stats
from clean_data import clean_stats, unique_players, consolidate_personal_awards
import csv
import pickle

years = list(range(2001, 2023))
game_types = ["playoffs", "leagues"]
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
distinct_players = []
players_stats = {}
players_advanced_stats = {}
teams_stats = {}

# get_players_stats(years, game_types)
# get_team_stats(years, game_types)
# get_players_advanced_stats(years, game_types)
personal_awards = consolidate_personal_awards()
for year in years:
    distinct_players.extend(unique_players(year))
    players_stats[year] = {}
    players_advanced_stats[year] = {}
    teams_stats[year] = {}
    for game_type in game_types:
        players_stats[year][game_type] = clean_stats(year, game_type, "players_stats", players_columns_to_drop)
        players_advanced_stats[year][game_type] = clean_stats(year, game_type, "players_advanced_stats", players_advanced_columns_to_drop)
        teams_stats[year][game_type] = clean_stats(year, game_type, "teams_stats", teams_columns_to_drop)

distinct_players = set(distinct_players)

# store processed data
personal_awards.to_csv('./data/transformed_data/personal_awards.csv', index=False, encoding='utf-8')

with open('./data/transformed_data/distinct_players.csv', 'w') as dist_play:
    write = csv.writer(dist_play)
    write.writerow(distinct_players)

with open('./data/transformed_data/players_stats.pickle', 'wb') as play_stats:
    pickle.dump(players_stats, play_stats)

with open('./data/transformed_data/players_advanced_stats.pickle', 'wb') as play_adv_stats:
    pickle.dump(players_advanced_stats, play_adv_stats)

with open('./data/transformed_data/teams_stats.pickle', 'wb') as team_stats:
    pickle.dump(teams_stats, team_stats)