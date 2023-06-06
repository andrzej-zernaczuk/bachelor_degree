from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import time
import os


options = Options()
options.add_extension("./chrome/ublock.crx")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# options.add_argument("--headless")
driver = webdriver.Chrome(executable_path="./chrome/chromedriver.exe", options=options)
driver.set_page_load_timeout(15)
driver.set_window_position(3000,0)
driver.maximize_window()

actions = ActionChains(driver)

def accept_cookies():
    print("Accepting policy")
    driver.get("https://www.basketball-reference.com")
    policy_button = driver.find_element(By.ID, "qc-cmp2-ui").find_element(By.CSS_SELECTOR, "button.css-47sehv")
    driver.execute_script("arguments[0].click()", policy_button)


def get_players_stats(years):

    accept_cookies()
    for year in years:
        if not os.path.exists('./stats/players_stats_{year}.csv'):
            players_stats_url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
            driver.get(players_stats_url)

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

            with open(f'players_stats_{year}.csv', 'w', encoding="utf-8") as file:
                print(f"Saving player stats from {year}")
                file.write(stats_csv)
