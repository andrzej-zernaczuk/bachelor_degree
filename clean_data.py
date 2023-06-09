import pandas as pd


def clean_stats(year: int, drop_cols: list):
    """Get rid of unnecessary data"""

    with open(f'./stats/player_stats/players_stats_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    df_dropped = df.drop(drop_cols, axis=1)

    filtered_df = df_dropped.drop_duplicates(subset='Player-additional', keep="first")
    filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df


def unique_players(year: int):
    """Get players"""

    with open(f'./stats/player_stats/players_stats_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    players = df["Player-additional"].values.tolist()
    distinct_players = set(players)

    return distinct_players


def consolidate_personal_awards():
    """Consolidate personal awards into one df"""

    # read all awards
    def_awards = pd.read_csv("./stats/league_awards/defensive_player_awards.csv")
    improv_awards = pd.read_csv("./stats/league_awards/most_improved_awards.csv")
    mvp_awards = pd.read_csv("./stats/league_awards/most_valuable_player_awards.csv")
    rookie_awards = pd.read_csv("./stats/league_awards/rookie_awards.csv")
    sixth_man_awards = pd.read_csv("./stats/league_awards/sixth_man_awards.csv")

    # create dataframe
    df_columns = ["season", "defensive", "most_improved", "most_valuable", "rookie", "sixth_man"]
    awards_conso = pd.DataFrame(columns=df_columns)
    awards_conso["season"] = def_awards["Season"]

    # add awards to dataframe by season
    awards_conso["defensive"] = def_awards["Player-additional"]
    awards_conso["most_improved"] = improv_awards["Player-additional"]
    awards_conso["most_valuable"] = mvp_awards["Player-additional"]
    awards_conso["rookie"] = rookie_awards["Player-additional"]
    awards_conso["sixth_man"] = sixth_man_awards["Player-additional"]

    return awards_conso