import pandas as pd


def clean_stats(year: int, game_type: str, stats_category: str, drop_cols: list):
    """Get rid ofunnecessary data"""

    with open(f'./data/{stats_category}/{game_type}/{stats_category}_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    df_dropped = df.drop(drop_cols, axis=1)

    if stats_category in ["players_stats", "players_advanced_stats"]:
        df_dropped.rename(columns = {'Player-additional':'ID'}, inplace = True)
        # find duplicates
        duplicates_df = df_dropped[df_dropped.duplicated(['ID'], keep=False)]
        # store the last team
        dropped_duplicates_df = duplicates_df.drop_duplicates(subset='ID', keep="last")
        # drop duplicates
        filtered_df = df_dropped.drop_duplicates(subset='ID', keep="first")
        filtered_df = filtered_df.set_index("ID")
        # swap TOT for last team ID
        for index, row in dropped_duplicates_df.iterrows():
            filtered_df.loc[[f"{row['ID']}"], ['Tm']] = dropped_duplicates_df.query(f"ID == '{row['ID']}'")["Tm"].iloc[0]
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
    df_columns = ["year", "defensive", "most_improved", "most_valuable", "rookie", "sixth_man"]
    awards_conso = pd.DataFrame(columns=df_columns)
    awards_conso["year"] = def_awards["Season"]
    awards_conso['year'] = awards_conso['year'].apply(lambda x: int("20" + str(x)[-2:]))

    # add awards to dataframe by year
    awards_conso["defensive"] = def_awards["ID"]
    awards_conso["most_improved"] = improv_awards["ID"]
    awards_conso["most_valuable"] = mvp_awards["ID"]
    awards_conso["rookie"] = rookie_awards["ID"]
    awards_conso["sixth_man"] = sixth_man_awards["ID"]

    return awards_conso

def consolidate_salary_cap():
    """Consolidate salary cap"""

    # read csv
    salary_cap_read = pd.read_csv("./data/teams_stats/salary_cap_history.csv")

    salary_cap = salary_cap_read.drop("2022 Dollars", axis=1)
    salary_cap.rename(columns = {'Year': 'year', 'Salary Cap': 'salary_cap'}, inplace = True)
    salary_cap['year'] = salary_cap['year'].apply(lambda x: int("20" + str(x)[-2:]))
    salary_cap['salary_cap'] = salary_cap['salary_cap'].apply(lambda x: int(str(x)[1:].replace(",", "")))

    return salary_cap