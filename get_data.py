from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import pandas as pd
import time
import os


options = Options()
options.add_extension("./chrome/ublock.crx")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# options.add_argument("--headless")
driver = webdriver.Chrome(executable_path="./chrome/chromedriver.exe", options=options)
driver.set_page_load_timeout(30)
driver.set_window_position(3000,0)
driver.maximize_window()

actions = ActionChains(driver)

cookies_accepted_br = False
cookies_accepted_spotrac = False

def accept_cookies_spotrac():
    """Accept cookies and newsletter popup"""
    print("Accepting Spotrac policy")
    driver.get("https://www.spotrac.com")

    driver.switch_to.frame('gdpr-consent-notice')
    driver.find_element(By.XPATH, "//button[@id='save']").click()

    driver.switch_to.default_content()
    newsletter_button = driver.find_element(By.ID, "PopupSignupForm_0").find_element(By.CLASS_NAME, "mc-closeModal")
    driver.execute_script("arguments[0].click()", newsletter_button)

def accept_cookies_br():
    """Accept cookies popup"""
    print("Accepting b-r policy")
    driver.get("https://www.basketball-reference.com")
    policy_button = driver.find_element(By.ID, "qc-cmp2-ui").find_element(By.CSS_SELECTOR, "button.css-47sehv")
    driver.execute_script("arguments[0].click()", policy_button)

def close_popup():
    """Close popup which appears during scrapping"""
    print("Closing b-r popup")
    close_button = driver.find_element(By.ID, "modal-container").find_element(By.ID, "modal-close")
    driver.execute_script("arguments[0].click()", close_button)

def get_players_stats(years: list, game_types: list):
    """Get player stats per season"""
    global cookies_accepted_br

    if cookies_accepted_br == False:
        accept_cookies_br()
        cookies_accepted_br = True
    for year in years:
        for game_type in game_types:
            if not os.path.exists(f'./data/raw_data/players_stats/{game_type}/players_stats_{year}.csv'):
                players_stats_url = f"https://www.basketball-reference.com/{game_type}/NBA_{year}_per_game.html"
                driver.get(players_stats_url)

                #in case of popup appearance, it stays hidden on site most of the time, closing it doesn't break the site
                close_popup()

                stats_table = driver.find_element(By.ID, "per_game_stats_link")
                driver.execute_script("arguments[0].scrollIntoView();", stats_table)

                share_export_menu = driver.find_element(By.CLASS_NAME, "section_heading_text").find_element(By.CSS_SELECTOR, "li.hasmore")
                time.sleep(2)
                actions.move_to_element(share_export_menu).perform()

                csv_option = driver.find_element(By.XPATH, "//button[text()='Get table as CSV (for Excel)']")
                time.sleep(2)
                actions.move_to_element(csv_option).click().perform()

                stats_copied = driver.find_element(By.ID, "div_per_game_stats").find_element(By.ID, "csv_per_game_stats").text
                partition_tuple = stats_copied.partition("Rk,Player,")
                stats_csv = partition_tuple[1] + partition_tuple[2]

                with open(f'./data/raw_data/players_stats/{game_type}/players_stats_{year}.csv', 'w', encoding="utf-8") as file:
                    print(f"Saving {game_type} player stats from {year}")
                    file.write(stats_csv)

def get_players_advanced_stats(years: list, game_types: list):
    """Get player advanced stats per season"""
    global cookies_accepted_br

    if cookies_accepted_br == False:
        accept_cookies_br()
        cookies_accepted_br = True
    for year in years:
        for game_type in game_types:
            if not os.path.exists(f'./data/raw_data/players_advanced_stats/{game_type}/players_advanced_stats_{year}.csv'):
                players_advanced_stats_url = f"https://www.basketball-reference.com/{game_type}/NBA_{year}_advanced.html"
                driver.get(players_advanced_stats_url)

                #in case of popup appearance, it stays hidden on site most of the time, closing it doesn't break the site
                close_popup()

                stats_table = driver.find_element(By.ID, "all_advanced_stats")
                driver.execute_script("arguments[0].scrollIntoView();", stats_table)

                share_export_menu = driver.find_element(By.CLASS_NAME, "section_heading_text").find_element(By.CSS_SELECTOR, "li.hasmore")
                time.sleep(2)
                actions.move_to_element(share_export_menu).perform()

                csv_option = driver.find_element(By.XPATH, "//button[text()='Get table as CSV (for Excel)']")
                time.sleep(2)
                actions.move_to_element(csv_option).click().perform()

                stats_copied = driver.find_element(By.ID, "all_advanced_stats").find_element(By.ID, "csv_advanced_stats").text
                partition_tuple = stats_copied.partition("Rk,Player,")
                stats_csv = partition_tuple[1] + partition_tuple[2]

                with open(f'./data/raw_data/players_advanced_stats/{game_type}/players_advanced_stats_{year}.csv', 'w', encoding="utf-8") as file:
                    print(f"Saving {game_type} player advanced stats from {year}")
                    file.write(stats_csv)

def get_teams_stats(years: list, game_types: list):
    """Get team stats per season"""
    global cookies_accepted_br

    if cookies_accepted_br == False:
        accept_cookies_br()
        cookies_accepted_br = True
    for year in years:
        for game_type in game_types:
            if not os.path.exists(f'./data/raw_data/teams_stats/{game_type}/teams_stats_{year}.csv'):
                teams_stats_url = f"https://www.basketball-reference.com/{game_type}/NBA_{year}.html"
                driver.get(teams_stats_url)

                #in case of popup appearance, it stays hidden on site most of the time, closing it doesn't break the site
                close_popup()

                stats_table = driver.find_element(By.ID, "totals-team_link")
                driver.execute_script("arguments[0].scrollIntoView();", stats_table)

                share_export_menu = driver.find_element(By.ID, "content").find_element(By.ID, "all_totals_team-opponent").find_element(By.CLASS_NAME, "section_heading_text").find_element(By.CSS_SELECTOR, "li.hasmore")
                time.sleep(2)
                actions.move_to_element(share_export_menu).perform()

                csv_option = driver.find_element(By.ID, "content").find_element(By.ID, "all_totals_team-opponent").find_element(By.CLASS_NAME, "section_heading_text").find_element(By.CSS_SELECTOR, "li.hasmore").find_element(By.XPATH, '//*[@id="totals-team_sh"]/div/ul/li[2]/div/ul/li[3]/button')
                time.sleep(2)
                actions.move_to_element(csv_option).click().perform()

                stats_copied = driver.find_element(By.ID, "div_totals-team").find_element(By.ID, "csv_totals-team").text
                if "Rk,Tm," in stats_copied:
                    stats_copied = stats_copied.replace("Rk,Tm,", "Rk,Team,")
                partition_tuple = stats_copied.partition("Rk,Team,")
                stats_csv = partition_tuple[1] + partition_tuple[2]

                with open(f'./data/raw_data/teams_stats/{game_type}/teams_stats_{year}.csv', 'w', encoding="utf-8") as file:
                    print(f"Saving {game_type} teams stats from {year}")
                    file.write(stats_csv)

def get_rookies_contracts(years: list):
    """Get info if players is a rookie"""
    global accept_cookies_spotrac

    if accept_cookies_spotrac == False:
        accept_cookies_spotrac()
        accept_cookies_spotrac = True

    for year in years:
        if not os.path.exists(f'./data/raw_data/rookies/rookies_{year}.csv'):

            rookies = pd.DataFrame(columns=["player", "debut_season", "contract_length"])

            rookies_url = f"https://www.spotrac.com/nba/contracts/sort-value/type-entry-level/all-time/start-{year-1}/limit-2000/"
            driver.get(rookies_url)

            stats_table = driver.find_element(By.CLASS_NAME, "teams").find_element(By.TAG_NAME, "tbody")

            rows = stats_table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                name = row.find_elements(By.TAG_NAME, "td")[1].find_element(By.CLASS_NAME, "team-name").text
                contract = row.find_elements(By.TAG_NAME, "td")[3].text

                new_df_row = [name, year, contract]
                rookies.loc[len(rookies)] = new_df_row

            rookies.to_csv(f'./data/raw_data/rookies/rookies_{year}.csv', index=False, encoding='utf-8')

def get_contracts_lengths(years: list):
    """get contract lengths and year of signing"""
    global accept_cookies_spotrac

    if accept_cookies_spotrac == False:
        accept_cookies_spotrac()
        accept_cookies_spotrac = True

    for year in years:
        if not os.path.exists(f'./data/raw_data/contracts/lengths_/lengths_{year}.csv'):

            contracts = pd.DataFrame(columns=["player", "season", "contract_length"])

            contracts_url = f"https://www.spotrac.com/nba/contracts/sort-value/all-time/start-{year-1}/limit-2000/"
            driver.get(contracts_url)

            stats_table = driver.find_element(By.CLASS_NAME, "teams").find_element(By.TAG_NAME, "tbody")

            rows = stats_table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                name = row.find_elements(By.TAG_NAME, "td")[1].find_element(By.CLASS_NAME, "team-name").text
                contract = row.find_elements(By.TAG_NAME, "td")[3].text

                new_df_row = [name, year, contract]
                contracts.loc[len(contracts)] = new_df_row

            contracts.to_csv(f'./data/raw_data/contracts/lengths/lengths_{year}.csv', index=False, encoding='utf-8')