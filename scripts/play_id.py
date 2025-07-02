import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ------------------- CONFIGURABLE VARIABLES -------------------
PITCHER_NAME = "Jacob deGrom"
BATTER_HANDEDNESS = "L"  # 'L' for left, 'R' for right
VENUE_INDEX = 16  # 1-based index for venue in dropdown
OUTPUT_CSV = "pitches.csv"
WAIT_TIME = 10

# Pitch type to category mapping
PITCH_TYPE_CATEGORIES = {
    'Fastball': {'FF', 'SI', 'FC'},
    'Offspeed': {'CH', 'FS', 'FO', 'SC'},
    'Breaking': {'CU', 'KC', 'CS', 'SL', 'ST', 'SV', 'KN'},
    'Other': {'EP', 'FA', 'IN', 'PO'}
}

# ------------------- UTILITY FUNCTIONS -------------------
def get_category(ptype):
    for category, types in PITCH_TYPE_CATEGORIES.items():
        if ptype in types:
            return category
    return 'Other'

# ------------------- SELENIUM SCRAPER FUNCTIONS -------------------
def setup_driver():
    """Initialize and return a Chrome WebDriver instance."""
    driver = webdriver.Chrome()
    driver.get("https://baseballsavant.mlb.com/statcast_search")
    return driver

def apply_filters(driver, pitcher_name, batter_handedness, venue_index):
    """Apply pitcher name, batter handedness, and venue filters."""
    wait = WebDriverWait(driver, WAIT_TIME)
    # Pitcher name
    pitcher_name_box = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/form/div[1]/div[11]/div[3]/span/span[1]/span/span/textarea')))
    pitcher_name_box.send_keys(pitcher_name)
    pitcher_name_box.send_keys(Keys.ENTER)
    # Batter handedness
    batter_handedness_select = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/form/div[1]/div[6]/div[2]/select')
    batter_handedness_select.send_keys(batter_handedness)
    # Venue
    venue_dropdown = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/form/div[1]/div[2]/div[3]/div/div/div/div[1]')
    venue_dropdown.click()
    venue_input = driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/div[1]/div[2]/div[3]/div/div/div/div[2]/div/div/div[2]/div[{venue_index}]/input')
    venue_input.click()
    time.sleep(2)
    venue_input.send_keys(Keys.ENTER)
    time.sleep(2)

def select_first_player_result(driver):
    """Click the first player result after filters are applied."""
    player_result = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div[3]/table/tbody/tr[1]')
    player_result.click()
    time.sleep(2)

def extract_pitch_data(driver):
    """Extract pitch type and video link from the results table."""
    wait = WebDriverWait(driver, WAIT_TIME)
    results_table = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div/div/div[3]/table/tbody/tr[2]/td/div/table')))
    rows = results_table.find_elements(By.CSS_SELECTOR, 'tbody tr')
    pitch_types = []
    hrefs = []
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, 'td')
        if tds:
            # Get pitch type from the first td with the correct span class
            pitch_type_td = tds[1]
            span = pitch_type_td.find_elements(By.CSS_SELECTOR, 'span.search-pitch-label')
            pitch_type = span[0].text if span else 'none'
            pitch_types.append(pitch_type)
            # Get video link from the last td
            last_td = tds[-1]
            a_tag = last_td.find_elements(By.TAG_NAME, 'a')
            href = a_tag[0].get_attribute('href') if a_tag else ''
            hrefs.append(href)
    return pitch_types, hrefs

def save_to_csv(pitch_types, hrefs, output_file):
    """Save pitch types, video links, and categories to a CSV file. Print summary info after saving."""
    df = pd.DataFrame({
        'pitch_type': pitch_types,
        'video_link': hrefs
    })
    df['category'] = df['pitch_type'].apply(get_category)
    df.to_csv(output_file, index=False)

    # Print summary info
    print(f"\nCSV successfully written!")
    print(f"Pitcher Name: {PITCHER_NAME}")
    print(f"Venue Index: {VENUE_INDEX}")
    print(f"Batter Handedness: {BATTER_HANDEDNESS}")
    print(f"Output File: {output_file}")
    print(f"Total Pitches: {len(df)}")
    print("Pitch Category Counts:")
    print(df['category'].value_counts().to_string())

# ------------------- MAIN SCRIPT -------------------
def main():
    driver = setup_driver()
    try:
        apply_filters(driver, PITCHER_NAME, BATTER_HANDEDNESS, VENUE_INDEX)
        select_first_player_result(driver)
        pitch_types, hrefs = extract_pitch_data(driver)
        save_to_csv(pitch_types, hrefs, OUTPUT_CSV)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()