import ndjson
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)


def get_text(by, value):
    return wait.until(EC.visibility_of_element_located((by, value))).text


def parse_card(card):
    # click on the first card then scrape all text from it
    card.click()

    modals = driver.find_elements(by=By.CLASS_NAME, value="modal")
    assert len(modals) == 1
    modal = modals[0]

    # on the first element, pause just enough for content to load
    category = get_text(By.XPATH, "//div[@class='category']//span")
    resource_theme = get_text(By.XPATH, "//div[@class='resource-theme-id']//span[1]")
    # resource_theme_id = get_text(By.XPATH,"//div[@class='resource-theme-id']//span[3]")
    title = get_text(By.CLASS_NAME, "headline")
    content = get_text(By.CLASS_NAME, "libReadMore_content")
    # speakers = modal.find_elements(by=By.CLASS_NAME, value="speaker")
    # speaker_objects = []
    # for speaker in speakers:
    #     speaker_objects.append({
    #         'name': speaker.find_element(by=By.CLASS_NAME, value="speaker-link").text,
    #         'job_title': speaker.find_element(by=By.CLASS_NAME, value="speaker-title").text,
    #         'company': speaker.find_element(by=By.CLASS_NAME, value="speaker-company").text,
    #     })
    #
    # session_tracks = [s.text for s in modal.find_elements(by=By.XPATH, value="//div[@class='sessionTracks']//span")]

    # close modal dialog
    modal.find_element(by=By.XPATH, value="//button[@action='close']").click()

    # return {
    #     'category': category,
    #     'resource_theme': resource_theme,
    #     'resource_theme_id': resource_theme_id,
    #     'title': title,
    #     'content': content,
    #     'speakers': speaker_objects,
    #     'session_tracks': session_tracks,
    # }

    # cut down the number of characters
    return {
        'type': category,
        'theme': resource_theme,
        'title': title,
        'content': content,
    }


def run():
    driver.get("https://cloud.withgoogle.com/next/session-library")
    driver.implicitly_wait(5)

    cards = driver.find_elements(by=By.CLASS_NAME, value="session-library-session-card")
    print(len(cards))

    # Display all cards by clicking on every "View More" button
    has_more_to_view = True
    while has_more_to_view:
        buttons = driver.find_elements(by=By.XPATH, value="//div[@class='view-more-button-container']//button")
        if buttons:
            print('Viewing more...')
            buttons[0].click()
            driver.implicitly_wait(0.5)
        else:
            has_more_to_view = False

    cards = driver.find_elements(by=By.CLASS_NAME, value="session-library-session-card")
    print(f'Total cards: {len(cards)}')

    all_sessions = []

    for i in range(len(cards)):
        print(f'Parsing card {i + 1} of {len(cards)}...')
        all_sessions.append(parse_card(cards[i]))

    ndjson.dump(all_sessions, open(f"abstracts/abstracts-all.txt", "w"))

    # chunk all_sessions in size of 100, and dump to a file suffix by number
    chunk_size = 100
    for i in range(0, len(all_sessions), chunk_size):
        ndjson.dump(all_sessions[i:i + chunk_size], open(f"abstracts/abstracts-{(i // chunk_size) + 1}.txt", "w"))


    driver.quit()


if __name__ == "__main__":
    run()
