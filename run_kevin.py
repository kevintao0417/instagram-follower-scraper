import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv


def save_credentials(username, password):
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")

def load_credentials():
    """Loads credentials from credentials.txt, returning None if file/lines don't exist."""
    if not os.path.exists('credentials.txt'):
        return None
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()
    return None

def prompt_credentials():
    """Prompts user for credentials (if none are loaded from disk)."""
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password

def login(bot, username, password):
    """Logs into Instagram with provided credentials."""
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(2)

    # Attempt to accept any cookie pop-up
    try:
        cookie_button = WebDriverWait(bot, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]"))
        )
        cookie_button.click()
    except TimeoutException:
        print("[Info] - No cookie banner this time or couldn't click it.")

    print("[Info] - Logging in...")
    username_input = WebDriverWait(bot, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))
    )
    password_input = WebDriverWait(bot, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
    )

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(bot, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_button.click()

    # Wait for login to complete (watch a specific element from homepage or post-login)
    time.sleep(8)  # adjust as needed

def scrape_followers(bot, username, num_followers_to_scrape):
    """Scrapes 'num_followers_to_scrape' followers for the given username."""
    # Go to the user's profile
    bot.get(f'https://www.instagram.com/{username}/')
    print(f"[Info] - Opening profile page for {username}...")
    print("[Debug] Current URL:", bot.current_url)
    print("[Debug] Page title:", bot.title)
    time.sleep(5)

    # Click on followers link (exact href: /<username>/followers/)
    followers_link_xpath = f"//a[@href='/{username}/followers/']"
    print("[Debug] Using XPath for followers link:", followers_link_xpath)

    followers_link = WebDriverWait(bot, 20).until(
        EC.element_to_be_clickable((By.XPATH, followers_link_xpath))
    )
    span_with_count = followers_link.find_element(By.XPATH, ".//span[@title]")
    follower_count_str = span_with_count.get_attribute("title")  
    follower_count = int(follower_count_str.replace(",", ""))
    print(f"[Info] - Follower count for {username} is: {follower_count}")


    followers_link.click()
    time.sleep(10)

    # Wait for the modal to appear
    modal = WebDriverWait(bot, 40).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
    )
    time.sleep(20)
    print(f"[Info] - Followers modal found; scraping followers for {username}...")

    try:
        scrollable_div = modal.find_element(
            By.XPATH, 
            ".//div[contains(@style, 'height: auto; overflow: hidden auto;')]"
        )
        scrollable_div = scrollable_div.find_element(By.XPATH, "./parent::div")
        print(f"[Info] - Scroll Located")
    # except NoSuchElementException:
    #     # Re-locate the modal or the scrollable container
    #     print(f"[Debug] - Re-locate the modal of the scrollable container")
    #     scrollable_div = WebDriverWait(bot, 15).until(
    #         EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[contains(@style, 'height: auto; overflow: hidden auto;')]"))
    #     ) 
    except NoSuchElementException:
        print(f"[Debug] - Can't locate the element")
    # Scroll the modal to load more followers
    SCROLL_TIMES = follower_count // 15 + 5
    bot.set_script_timeout(60)
    scroll_pos = 0
    scroll_increment = 800
    for i in range(SCROLL_TIMES):
        print(f"[Info] - Total Scrolls: {SCROLL_TIMES}, Scroll {i}")
        scroll_pos += scroll_increment
        bot.execute_script("arguments[0].scrollTop = arguments[1];", scrollable_div, scroll_pos)
        time.sleep(5)

    # Collect followers data
    followers_info = []

    # If your layout uses <li>, keep it. If your DevTools show <div> for each follower row, use that.
    # Example with <li>:
    follower_rows = modal.find_elements(
        By.XPATH, 
        ".//div[contains(@class,'x1dm5mii')]"
    )

    # Alternatively, if that yields no results, try:
    # follower_rows = modal.find_elements(By.XPATH, ".//div[contains(@class, 'x1dm5mii')]")
    # or some other <div> that each follower occupies.

    for row in follower_rows:
        try:
            link_el = row.find_element(By.XPATH, ".//a[contains(@href, '/')]")
        except NoSuchElementException:
            # No anchor in this row, skip
            continue

        full_href = link_el.get_attribute("href")
        # The handle is typically the last part of the URL, e.g. "https://www.instagram.com/cxxy_rc/"
        handle = full_href.rstrip("/").split("/")[-1]

        # Attempt to read text from <span> elements in that row.
        # Usually, the real name is the first <span>, and the handle is the second, but it can vary.
        try:
            real_name_span = link_el.find_element(
            By.XPATH,
                "./../../../../following-sibling::span"
            )
            real_name_span = real_name_span.find_element(
            By.XPATH,
                "./span"
            )
            real_name = real_name_span.text

        except NoSuchElementException:
            real_name = "NA"

        # Add to list
        followers_info.append((handle, real_name))

        # Print or store them
        # for user_handle, rname in followers_info:
        #     print(f"[Follower] Username: {user_handle}, Real Name: {rname}")


    print(f"[Info] - Found {len(followers_info)} followers for {username}. Saving to file...")

    # Write to a text file, one follower per line in "handle,real_name" format
    with open(f'{username}_followers.txt', 'w', encoding='utf-8') as file:
        for (u, r) in followers_info:
            file.write(f"{u},{r}\n")
    with open(f"{username}_followers.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Optional: write a header row
        writer.writerow(["Username", "Real Name"])

        # Write each tuple (u, r) as a new row
        for (u, r) in followers_info:
            writer.writerow([u, r])

def scrape():
    # Load or prompt for credentials
    credentials = load_credentials()
    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    # Hard-coded for example
    user_input = 20
    usernames = ["lucy_wjzh", "candice_wyj_"]

    # Set up Chrome
    service = Service(CM().install())
    options = Options()
    # Uncomment to run in headless mode
    # options.add_argument("--headless")

    # Mobile emulation can sometimes cause different layouts
    # If the script fails to find elements, try disabling it.
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")

    bot = webdriver.Chrome(service=service, options=options)
    bot.set_page_load_timeout(90)

    try:
        login(bot, username, password)
        print("[Info] - Login finished.")
        # Scrape each username in the list
        for user in usernames:
            user = user.strip()
            scrape_followers(bot, user, user_input)
    finally:
        bot.quit()

if __name__ == '__main__':
    scrape()
