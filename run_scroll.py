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
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Accept')]"))
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

    login_button = WebDriverWait(bot, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_button.click()

    # Wait for login to complete (watch a specific element from homepage or post-login)
    time.sleep(5)  # adjust as needed


def scrape_followers(bot, username, num_followers_to_scrape, scrape_mode_se):
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
    span_with_count = followers_link.find_element(
        By.XPATH, ".//span[@title]")
    follower_count_str = span_with_count.get_attribute("title")
    follower_count = int(follower_count_str.replace(",", ""))
    print(f"[Info] - Follower count for {username} is: {follower_count}")

    followers_link.click()
    time.sleep(5)

    # Wait for the modal to appear
    if scrape_mode_se == "1":
        modal = WebDriverWait(bot, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        time.sleep(10)
        print(
            f"[Info] - Followers modal found; scraping followers for {username}...")

        try:
            scrollable_div = modal.find_element(
                By.XPATH,
                ".//div[contains(@style, 'height: auto; overflow: hidden auto;)]"
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
        scrollable_div = scrollable_div.find_element(By.XPATH, "./parent::div")

    elif scrape_mode_se == "2":
        bot.get(f'https://www.instagram.com/{username}/followers')
        print(
            f"[Info] - Followers modal found; scraping followers for {username}...")
        try:
            scrollable_div = WebDriverWait(bot, 20).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    ".//div[contains(@style, 'height: auto; overflow: hidden auto;')]"))
            )
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
    SCROLL_TIMES = follower_count // 3 + 5
    bot.set_script_timeout(60)
    scroll_pos = 0
    scroll_increment = 1000
    for i in range(SCROLL_TIMES):
        if (i % 5 == 0):
            print(f"[Info] - Total Scrolls: {SCROLL_TIMES}, Scroll {i}")
        scroll_pos += scroll_increment
        bot.execute_script(
            "arguments[0].scrollTop = arguments[1];", scrollable_div, scroll_pos)
        time.sleep(2)

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

    print(
        f"[Info] - Found {len(followers_info)} followers for {username}. Saving to file...")

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

    UA, scrape_mode_se = scrape_mode()

    usernames = get_usernames()
    chrome_binary = (
        "/Users/kevintao/Develop/ChromeTest/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    )

    # Path to your ChromeDriver executable (make sure this file exists and is executable)
    chromedriver_path = (
        "/Users/kevintao/Develop/ChromeTest/chromedriver-mac-arm64/chromedriver"
    )
    # Set up Chrome
    options = Options()
    # Use your custom Chrome binary
    options.binary_location = chrome_binary
    # Uncomment to run in headless mode
    # options.add_argument("--headless")

    # Mobile emulation can sometimes cause different layouts
    # If the script fails to find elements, try disabling it.
    if scrape_mode_se == "1":
        mobile_emulation = {"UserAgent": UA}
    elif scrape_mode_se == "2": 
        mobile_emulation = {"deviceName": "iPhone X"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")

    service = Service(executable_path=chromedriver_path)

    bot = webdriver.Chrome(service=service, options=options)
    bot.set_page_load_timeout(90)

    try:
        login(bot, username, password)
        print("[Info] - Login finished.")
        # Scrape each username in the list
        for user in usernames:
            user = user.strip()
            scrape_followers(bot, user, user_input, scrape_mode_se)
    finally:
        bot.quit()


def get_usernames():
    choice = input(
        "Select input method:\n"
        "1. Read from CSV file (usernamelist.csv)\n"
        "2. Input manually\n"
        "Enter 1 or 2: "
    ).strip()

    if choice == "1":
        try:
            with open("usernamelist.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                # Uncomment the following line if your CSV has a header row
                # next(reader, None)
                usernames = [row[0].strip() for row in reader if row]
            print(f"Usernames loaded from CSV: {usernames}")
            return usernames
        except FileNotFoundError:
            print(
                "CSV file 'usernamelist.csv' not found. Please check the file location.")
            return []
    elif choice == "2":
        usernames = input(
            "Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")
        usernames = [username.strip()
                     for username in usernames if username.strip()]
        print(f"Usernames entered manually: {usernames}")
        return usernames
    else:
        print("Invalid selection. Please enter either '1' or '2'.")
        return get_usernames()


def scrape_mode():
    scrape_UA = input("Type 1 for using PC UA, Type 2 for using Mobile UA:")
    if scrape_UA == "2":
        UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/134.0.6998.99 Mobile/15E148 Safari/604.1"
        print("UA Selected with PC mode")
        return UA, scrape_UA
    elif scrape_UA == "1":
        UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        print("UA Selected with mobile mode")
        return UA, scrape_UA
    else:
        print("Invalid selection. Please enter either '1' or '2'.")
        return scrape_mode()


if __name__ == '__main__':
    scrape()
