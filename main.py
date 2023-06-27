from get_data import get_players_stats, get_team_stats
from clean_data import clean_stats, unique_players, consolidate_personal_awards

years = list(range(2001, 2023))
game_types = ["playoffs", "leagues"]
# stats that aren't need for model
players_columns_to_drop = ['Rk', 'Pos', 'FG', 'FGA', 'FG%', '3P',
                   '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%',
                   'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB',
                   'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
teams_columns_to_drop = ['Rk', 'FG', 'FGA', 'FG%', '3P',
                   '3PA', '3P%', '2P', '2PA', '2P%',
                   'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB',
                   'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
distinct_players = []
players_stats = {}
teams_stats = {}

# get_players_stats(years, game_types)
# get_team_stats(years, game_types)
personal_awards = consolidate_personal_awards()
for year in years:
    distinct_players.extend(unique_players(year))
    players_stats[year] = {}
    teams_stats[year] = {}
    for game_type in game_types:
        players_stats[year][game_type] = clean_stats(year, game_type, "players_stats", players_columns_to_drop)
        teams_stats[year][game_type] = clean_stats(year, game_type, "teams_stats", teams_columns_to_drop)

distinct_players = set(distinct_players)