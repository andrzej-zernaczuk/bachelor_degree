import pandas as pd


def clean_stats(year: int, game_type: str, stats_category: str, drop_cols: list):
    """Get rid ofunnecessary data"""

    with open(f'./data/{stats_category}/{game_type}/{stats_category}_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    df_dropped = df.drop(drop_cols, axis=1)

    if stats_category in ["players_stats", "players_advanced_stats"]:
        df_dropped.rename(columns = {'Player-additional':'ID'}, inplace = True)
        filtered_df = df_dropped.drop_duplicates(subset='ID', keep="first")
        filtered_df.reset_index(drop=True, inplace=True)
    if stats_category == "teams_stats":
        filtered_df = df_dropped[df_dropped.Team != "League Average"]
        filtered_df['Team'] = filtered_df['Team'].str.replace('*', '')

    return filtered_df


def unique_players(year: int):
    """Get players"""

    with open(f'./data/players_stats/leagues/players_stats_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    players = df["Player-additional"].values.tolist()
    distinct_players = set(players)

    return distinct_players


def consolidate_personal_awards():
    """Consolidate personal awards into one df"""

    # read all awards
    def_awards = pd.read_csv("./data/league_awards/defensive_player_awards.csv")
    improv_awards = pd.read_csv("./data/league_awards/most_improved_awards.csv")
    mvp_awards = pd.read_csv("./data/league_awards/most_valuable_player_awards.csv")
    rookie_awards = pd.read_csv("./data/league_awards/rookie_awards.csv")
    sixth_man_awards = pd.read_csv("./data/league_awards/sixth_man_awards.csv")

    # create dataframe
    df_columns = ["season", "defensive", "most_improved", "most_valuable", "rookie", "sixth_man"]
    awards_conso = pd.DataFrame(columns=df_columns)
    awards_conso["season"] = def_awards["Season"]

    # add awards to dataframe by season
    awards_conso["defensive"] = def_awards["ID"]
    awards_conso["most_improved"] = improv_awards["ID"]
    awards_conso["most_valuable"] = mvp_awards["ID"]
    awards_conso["rookie"] = rookie_awards["ID"]
    awards_conso["sixth_man"] = sixth_man_awards["ID"]

    return awards_conso