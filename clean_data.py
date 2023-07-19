import pandas as pd


def clean_stats(year: int, game_type: str, stats_category: str, drop_cols: list):
    """Get rid ofunnecessary data"""

    with open(f'./data/raw_data/{stats_category}/{game_type}/{stats_category}_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    df_dropped = df.drop(drop_cols, axis=1)

    if stats_category == "players_advanced_stats":
        # drops 2 unnamed columns
        df_dropped = df_dropped.loc[:, ~df_dropped.columns.str.contains('^Unnamed')]

    if stats_category in ["players_stats", "players_advanced_stats"]:
        df_dropped.rename(columns = {'Player-additional': 'ID'}, inplace = True)
        # find duplicates
        duplicates_df = df_dropped[df_dropped.duplicated(['ID'], keep=False)]
        # store the last team
        dropped_duplicates_df = duplicates_df.drop_duplicates(subset='ID', keep="last")
        # drop duplicates
        filtered_df = df_dropped.drop_duplicates(subset='ID', keep="first")
        # swap TOT for last team ID
        for index, row in dropped_duplicates_df.iterrows():
            idx = filtered_df.query(f"ID == '{dropped_duplicates_df.loc[index, 'ID']}'").index
            filtered_df.loc[idx, 'Tm'] = dropped_duplicates_df.query(f"ID == '{row['ID']}'")["Tm"].iloc[0]

        # change legacy names of teams to current ones
        if 'NJN' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('NJN', 'BRK')
        if 'CHH' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('CHH', 'CHO')
        if 'CHA' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('CHA', 'CHO')
        if 'NOH' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('NOH', 'NOP')
        if 'NOK' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('NOK', 'NOP')
        if 'SEA' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('SEA', 'OKC')
        if 'VAN' in filtered_df['Tm'].values:
            filtered_df['Tm'] = filtered_df['Tm'].replace('VAN', 'MEM')

    if stats_category == "teams_stats":
        filtered_df = df_dropped[df_dropped.Team != "League Average"]
        filtered_df['Team'] = filtered_df['Team'].str.replace('*', '')

        with open(f'./data/raw_data/teams_stats/teams.csv', 'r', encoding="utf-8") as file:
            dist_teams = pd.read_csv(file)

        for index, row in filtered_df.iterrows():
            # data inconsistency fix
            if filtered_df.loc[index, 'Team'] == 'Seattle Supersonics':
                row['Team'] = 'Seattle SuperSonics'
            if filtered_df.loc[index, 'Team'] == 'New Orleans/Oklahoma City Hornets':
                row['Team'] = 'New Orleans Hornets'

            # change team name to id
            filtered_df.loc[index, 'Team'] = dist_teams.query(f"team == '{row['Team']}'")["ID"].iloc[0]

    return filtered_df


def clean_playoffs(year: int):
    """Change team name to ID"""
    with open(f'./data/raw_data/playoffs_tree/playoffs_{year}.csv', 'r', encoding="utf-8") as file:
        playoffs = pd.read_csv(file)

    with open(f'./data/raw_data/teams_stats/teams.csv', 'r', encoding="utf-8") as file:
        dist_teams = pd.read_csv(file)

    for index, row in playoffs.iterrows():
        # change team name to id
        playoffs.loc[index, 'winner'] = dist_teams.query(f"team == '{row['winner']}'")["ID"].iloc[0]
        playoffs.loc[index, 'loser'] = dist_teams.query(f"team == '{row['loser']}'")["ID"].iloc[0]

    return playoffs


def unique_players(year: int):
    """Get players"""

    with open(f'./data/raw_data/players_stats/leagues/players_stats_{year}.csv', 'r', encoding="utf-8") as file:
        df = pd.read_csv(file)

    players = pd.DataFrame(columns=["ID", "player"])

    players["ID"] = df["Player-additional"].values.tolist()
    players["player"] = df["Player"].values.tolist()
    players["player"] = players["player"].str.replace("*","")

    return players


def consolidate_salary_cap():
    """Consolidate salary cap"""

    # read csv
    salary_cap_read = pd.read_csv("./data/raw_data/teams_stats/salary_cap_history.csv")

    salary_cap = salary_cap_read.drop("2022 Dollars", axis=1)
    salary_cap.rename(columns = {'Year': 'year', 'Salary Cap': 'salary_cap'}, inplace = True)
    salary_cap['year'] = salary_cap['year'].apply(lambda x: int("20" + str(x)[-2:]))
    salary_cap['salary_cap'] = salary_cap['salary_cap'].apply(lambda x: int(str(x)[1:].replace(",", "")))

    return salary_cap


def consolidate_personal_awards():
    """Consolidate personal awards into one df"""

    # read all awards
    def_awards = pd.read_csv("./data/raw_data/league_awards/defensive_player_awards.csv")
    improv_awards = pd.read_csv("./data/raw_data/league_awards/most_improved_awards.csv")
    mvp_awards = pd.read_csv("./data/raw_data/league_awards/most_valuable_player_awards.csv")
    mvp_finals_awards = pd.read_csv("./data/raw_data/league_awards/most_valuable_player_finals_awards.csv")
    sixth_man_awards = pd.read_csv("./data/raw_data/league_awards/sixth_man_awards.csv")
    all_league = pd.read_csv("./data/raw_data/league_awards/all_league_awards.csv")
    all_def = pd.read_csv("./data/raw_data/league_awards/all_defensive_awards.csv")

    all_league_cleaned = clean_all_league_awards(all_league)
    all_def_cleaned = clean_all_def_awards(all_def)

    # create dataframe
    df_columns = ["year", "defensive", "most_improved", "most_valuable", "most_valuable_finals", "sixth_man"]
    awards_conso = pd.DataFrame(columns=df_columns)
    awards_conso["year"] = def_awards["Season"]
    # Change Season notation to simple Years
    awards_conso['year'] = awards_conso['year'].apply(lambda x: int("20" + str(x)[-2:]))

    # add awards to dataframe by year
    awards_conso["defensive"] = def_awards["ID"]
    awards_conso["most_improved"] = improv_awards["ID"]
    awards_conso["most_valuable"] = mvp_awards["ID"]
    awards_conso["most_valuable_finals"] = mvp_finals_awards["ID"]
    awards_conso["sixth_man"] = sixth_man_awards["ID"]

    awards_conso = pd.concat([awards_conso, all_league_cleaned], axis=1)
    awards_conso = pd.concat([awards_conso, all_def_cleaned], axis=1)

    return awards_conso

def clean_all_def_awards(df: pd.DataFrame):
    """Clean all deffensive awards and transform into DF ready to be concatenated to personal awards"""
    all_def = df

    # In case of draw split players into 2 separate columns
    for index, row in all_def.iterrows():
        if "(T)" in row["Player5"]:
            val = str(row["Player5"]).replace(" (T)", "")
            names = val.split(" ")
            all_def.loc[index, 'Player5'] = " ".join(names[:2])
            all_def.loc[index, 'Player6'] = " ".join(names[2:])

    # Change Season notation to simple Years
    all_def['Season'] = all_def['Season'].apply(lambda x: int("20" + str(x)[-2:]))

    # Create cleaned df to hold data
    all_def_rows = ["Year", "all_def_1", "all_def_2", "all_def_3", "all_def_4", "all_def_5", "all_def_6", "all_def_7", "all_def_8", "all_def_9", "all_def_10", "all_def_11"]
    all_def_cleaned = pd.DataFrame(columns=all_def_rows)
    all_def_cleaned["Year"] = list(reversed(range(2001, 2024)))

    # Flatten all_def into new df
    for index, row in all_def_cleaned.iterrows():
        for i in range(1,12):
            if i <= 5:
                all_def_cleaned.loc[index, f'all_def_{i}'] = all_def.query(f"Season == {row['Year']} and Tm == '1st'")[f"Player{i}"].iloc[0]
            elif 5 < i <= 10:
                all_def_cleaned.loc[index, f'all_def_{i}'] = all_def.query(f"Season == {row['Year']} and Tm == '2nd'")[f"Player{i - 5}"].iloc[0]
            else:
                if pd.isna(all_def.query(f"Season == {row['Year']} and Tm == '1st'")[f"Player{ i- 5}"].iloc[0]):
                    all_def_cleaned.loc[index, f'all_def_{i}'] = all_def.query(f"Season == {row['Year']} and Tm == '2nd'")[f"Player{6}"].iloc[0]
                else:
                    all_def_cleaned.loc[index, f'all_def_{i}'] = all_def.query(f"Season == {row['Year']} and Tm == '1st'")[f"Player{6}"].iloc[0]

    # Not needed in final df
    all_def_cleaned = all_def_cleaned.drop(columns=['Year'])

    return all_def_cleaned


def clean_all_league_awards(df: pd.DataFrame):
    """clean all league awards and transform into DF ready to be concatenated to personal awards"""
    all_league = df

    # Remove single letter and whitespace at end of columns
    columns_to_edit = ["Player1", "Player2", "Player3", "Player4", "Player5"]
    for column in columns_to_edit:
        all_league[f'{column}'] = all_league[f'{column}'].apply(lambda x: str(x)[:-2])

    # Change Season notation to simple Years
    all_league['Season'] = all_league['Season'].apply(lambda x: int("20" + str(x)[-2:]))

    # Create cleaned df to hold data
    all_league_rows = ["Year", "all_league_1", "all_league_2", "all_league_3", "all_league_4", "all_league_5",
                   "all_league_6", "all_league_7", "all_league_8", "all_league_9", "all_league_10",
                   "all_league_11", "all_league_12", "all_league_13", "all_league_14", "all_league_15"]
    all_league_cleaned = pd.DataFrame(columns=all_league_rows)
    all_league_cleaned["Year"] = list(reversed(range(2001, 2024)))

    # Flatten all_league into new df
    for index, row in all_league_cleaned.iterrows():
        for i in range(1,16):
            if i <= 5:
                all_league_cleaned.loc[index, f'all_league_{i}'] = all_league.query(f"Season == {row['Year']} and Tm == '1st'")[f"Player{i}"].iloc[0]
            elif 5 < i <= 10:
                all_league_cleaned.loc[index, f'all_league_{i}'] = all_league.query(f"Season == {row['Year']} and Tm == '2nd'")[f"Player{i - 5}"].iloc[0]
            elif 10 < i <= 15:
                all_league_cleaned.loc[index, f'all_league_{i}'] = all_league.query(f"Season == {row['Year']} and Tm == '3rd'")[f"Player{i - 10}"].iloc[0]

    # Not needed in final df
    all_league_cleaned = all_league_cleaned.drop(columns=['Year'])

    return all_league_cleaned


def clean_personal_awards(pers_awards, dist_players: pd.DataFrame):
    """Change player names to IDs"""

    distinct_players = dist_players

    player_names = list(pd.unique(pers_awards[["all_league_1", "all_league_2", "all_league_3", "all_league_4", "all_league_5", "all_league_6",
                                                    "all_league_7", "all_league_8", "all_league_9", "all_league_10", "all_league_11", "all_league_12",
                                                    "all_league_13", "all_league_14", "all_league_15", "all_def_1", "all_def_2", "all_def_3", "all_def_4",
                                                    "all_def_5", "all_def_6", "all_def_7", "all_def_8", "all_def_9", "all_def_10", "all_def_11"]].values.ravel()))

    player_names_cleaned = [x for x in player_names if x == x]

    for name in player_names_cleaned:
        name_id = distinct_players.query(f'player == "{name}"')['ID'].iloc[0]
        pers_awards = pers_awards.replace(f"{name}", f"{name_id}")

    return pers_awards