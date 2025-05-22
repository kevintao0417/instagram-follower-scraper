import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


import json

def save_credentials(username, password):
    # WARNING: Storing credentials in a plain text file is not secure.
    # Consider using environment variables or a more secure method for production.
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")

def save_cookies(bot, username):
    """Saves browser cookies to a file."""
    # WARNING: Storing cookies can also be a security risk.
    try:
        cookie_file_path = os.path.join('cookies', f'{username}_cookies.json')
        with open(cookie_file_path, 'w') as file:
            json.dump(bot.get_cookies(), file)
        print(f"[Info] - Cookies saved for {username}.")
    except Exception as e:
        print(f"[Error] - Could not save cookies for {username}: {e}")

def load_cookies(bot, username):
    """Loads browser cookies from a file and adds them to the browser."""
    try:
        cookie_file_path = os.path.join('cookies', f'{username}_cookies.json')
        if not os.path.exists(cookie_file_path):
            print(f"[Info] - No cookie file found for {username}.")
            return False

        bot.get('https://www.instagram.com/') # Navigate to the domain before adding cookies
        with open(cookie_file_path, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                # Add domain to cookie if missing (sometimes necessary)
                if 'domain' not in cookie:
                    cookie['domain'] = '.instagram.com'
                # Ensure cookie is valid for adding
                if 'expiry' in cookie:
                    # Convert float expiry to int if necessary
                    if isinstance(cookie['expiry'], float):
                         cookie['expiry'] = int(cookie['expiry'])
                bot.add_cookie(cookie)
        print(f"[Info] - Cookies loaded for {username}.")
        bot.refresh() # Refresh the page to use the loaded cookies
        # Check if login was successful by looking for a post-login element
        WebDriverWait(bot, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/explore/']"))
        )
        print(f"[Info] - Login successful using cookies for {username}.")
        return True
    except FileNotFoundError:
        print(f"[Info] - Cookie file not found for {username}.")
        return False
    except TimeoutException:
        print(f"[Info] - Cookie login failed for {username}. Timeout waiting for post-login element.")
        return False
    except Exception as e:
        print(f"[Error] - Could not load or use cookies for {username}: {e}")
        return False



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
    try:
        bot.get('https://www.instagram.com/accounts/login/')
        WebDriverWait(bot, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )

        # Attempt to accept any cookie pop-up
        try:
            # Look for buttons that might accept cookies
            cookie_buttons = WebDriverWait(bot, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[contains(text(),'Accept') or "
                               "contains(text(),'Allow')]"))
            )
            for button in cookie_buttons:
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    print("[Info] - Accepted cookie banner.")
                    break  # Click only one button
        except TimeoutException:
            print("[Info] - No cookie banner found or couldn't click it.")

        print("[Info] - Logging in...")
        username_input = WebDriverWait(bot, 20).until(
            EC.element_to_be_clickable((By.NAME, 'username'))
        )
        password_input = WebDriverWait(bot, 20).until(
            EC.element_to_be_clickable((By.NAME, 'password'))
        )

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)

        login_button = WebDriverWait(bot, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()

        # Wait for an element that indicates successful login (e.g., the explore link)
        WebDriverWait(bot, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/explore/']"))
        )
        print("[Info] - Login successful.")

    except TimeoutException:
        print("[Error] - Timeout during login. Check credentials or network.")
        raise
    except WebDriverException as e:
        print(f"[Error] - WebDriver error during login: {e}")
        raise
    except Exception as e:
        print(f"[Error] - An unexpected error occurred during login: {e}")
        raise


def get_follower_count(bot, username):
    """Gets the follower count for the given username."""
    try:
        bot.get(f'https://www.instagram.com/{username}/')
        print(f"[Info] - Opening profile page for {username}...")
        WebDriverWait(bot, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//a[@href='/{username}/followers/']"))
        )

        followers_link_xpath = f"//a[@href='/{username}/followers/']"
        followers_link = bot.find_element(By.XPATH, followers_link_xpath)
        span_with_count = followers_link.find_element(By.XPATH, ".//span[@title]")
        follower_count_str = span_with_count.get_attribute("title")
        follower_count = int(follower_count_str.replace(",", ""))
        print(f"[Info] - Follower count for {username} is: {follower_count}")
        return follower_count

    except TimeoutException:
        print(f"[Error] - Timeout while getting follower count for {username}. "
              "Profile might not exist or loaded slowly.")
        return 0
    except NoSuchElementException:
        print(f"[Error] - Could not find follower count element for {username}.")
        return 0
    except Exception as e:
        print(f"[Error] - An unexpected error occurred while getting follower count: {e}")
        return 0


def open_followers_modal(bot, username):
    """Clicks the followers link to open the modal."""
    try:
        followers_link_xpath = f"//a[@href='/{username}/followers/']"
        
        # Attempt to dismiss any potential overlays by pressing Escape
        try:
            bot.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1) # Give a moment for overlay to disappear
            print("[Info] - Attempted to dismiss overlay with Escape key.")
        except Exception as e:
            print(f"[Debug] - Could not send Escape key: {e}") # Log as debug as it might not be necessary

        followers_link = WebDriverWait(bot, 20).until(
            EC.element_to_be_clickable((By.XPATH, followers_link_xpath))
        )
        bot.execute_script("arguments[0].click();", followers_link)
        print("[Info] - Clicked followers link using JavaScript.")
        # Wait for the modal to appear
        modal = WebDriverWait(bot, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        print("[Info] - Followers modal appeared.")
        return modal
    except TimeoutException:
        print("[Error] - Timeout while waiting for followers link or modal.")
        return None
    except NoSuchElementException:
        print("[Error] - Could not find followers link or modal element.")
        return None
    except Exception as e:
        print(f"[Error] - An unexpected error occurred while opening followers modal: {e}")
        return None


def find_scrollable_element(modal):
    """Finds the scrollable element within the followers modal."""
    try:
        # Wait for a stable element within the modal to be present, e.g., the search input
        search_input_xpath = ".//input[@aria-label='Search input']"
        WebDriverWait(modal, 20).until(
            EC.presence_of_element_located((By.XPATH, search_input_xpath))
        )
        print("[Info] - Stable element (search input) found within modal.")

        # Find the element with overflow style within the modal
        scrollable_element_xpath = ".//div[contains(@style, 'overflow: hidden auto;') or contains(@style, 'overflow: auto;')]"
        scrollable_element = WebDriverWait(modal, 20).until(
             EC.visibility_of_element_located((By.XPATH, scrollable_element_xpath))
        )
        print("[Info] - Found element with overflow style.")

        # Return the parent element as the scrollable element
        scrollable_parent_element = scrollable_element.find_element(By.XPATH, "..")
        print("[Info] - Returning parent element as scrollable element.")
        return scrollable_parent_element

    except TimeoutException:
        print("[Error] - Timeout while waiting for stable element or scrollable element.")
        return None
    except NoSuchElementException:
        print("[Error] - Could not find stable element, scrollable element, or its parent.")
        return None
    except Exception as e:
        print(f"[Error] - An unexpected error occurred while finding scrollable element: {e}")
        return None


def scroll_modal(bot, modal, scrollable_element):
    """Scrolls the modal all the way down to load all followers."""
    print("[Info] - Scrolling modal all the way down...")
    try:
        # Scroll to the bottom of the scrollable element
        bot.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
        time.sleep(5)  # Give time for all content to load after scrolling

        print("[Info] - Scrolled to the bottom of the modal.")

    except Exception as e:
        print(f"[Error] - An unexpected error occurred during scrolling: {e}")


def extract_follower_data(modal):
    """Extracts follower usernames and real names from the modal."""
    print("[Info] - Extracting follower data...")
    followers_info = []
    try:
        # Find all elements that represent individual follower rows.
        # Based on the HTML, these are divs with specific classes.
        follower_rows = modal.find_elements(
            By.XPATH,
            ".//div[contains(@class, 'x1dm5mii') and contains(@class, 'x16mil14') and contains(@class, 'xiojian')]" # Targeting key classes for follower rows
        )
        print(f"[Info] - Found {len(follower_rows)} potential follower rows.")

        for row in follower_rows:
            try:
                # Find the link element which contains the username in its href within the current row
                link_el = row.find_element(By.XPATH, ".//a[contains(@href, '/')]")
                full_href = link_el.get_attribute("href")
                handle = full_href.rstrip("/").split("/")[-1]

                # Attempt to find the real name span within the current row
                real_name = "NA"
                try:
                    # Look for span elements with a common text class within the row.
                    # Filter to find the one that is not the username.
                    name_spans = row.find_elements(
                        By.XPATH,
                        ".//span[contains(@class, 'x1lliihq')]" # Common class for text
                    )
                    for span in name_spans:
                        # Check if the span text is not the handle and is not empty
                        if span.text != handle and span.text.strip() != "":
                            real_name = span.text
                            break # Found the real name, move to the next row

                except NoSuchElementException:
                    pass  # Real name not found for this follower

                if handle and handle != "NA":  # Ensure a valid handle was found
                    followers_info.append((handle, real_name))

            except NoSuchElementException:
                print("[Debug] - Could not find link element in a row. Skipping row.")
                continue  # Skip rows that don't have a link
            except Exception as e:
                print(f"[Error] - An unexpected error occurred while processing a follower row: {e}")
                continue  # Continue to the next row even if one fails

    except Exception as e:
        print(f"[Error] - An unexpected error occurred while extracting follower data: {e}")

    print(f"[Info] - Extracted info for {len(followers_info)} followers.")
    return followers_info


def save_followers_to_file(followers_info, username):
    """Saves the extracted follower information to text and CSV files."""
    try:
        # Write to a text file, one follower per line in "handle,real_name" format
        with open(f'{username}_followers.txt', 'w', encoding='utf-8') as file:
            for (u, r) in followers_info:
                file.write(f"{u},{r}\n")
        print(f"[Info] - Saved follower data to {username}_followers.txt")

        # Write to a CSV file
        with open(f"{username}_followers.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Real Name"])  # Header row
            for (u, r) in followers_info:
                writer.writerow([u, r])
        print(f"[Info] - Saved follower data to {username}_followers.csv")

    except IOError as e:
        print(f"[Error] - Error writing follower data to file: {e}")
    except Exception as e:
        print(f"[Error] - An unexpected error occurred while saving follower data: {e}")


def scrape_followers(bot, username):
    """Scrapes followers for the given username."""
    follower_count = get_follower_count(bot, username)
    if follower_count == 0:
        print(f"[Info] - Skipping scraping for {username} due to inability to get follower count.")
        return

    modal = open_followers_modal(bot, username)
    if modal is None:
        print(f"[Error] - Could not open followers modal for {username}. Skipping scraping.")
        return

    scrollable_element = find_scrollable_element(modal)

    # If finding the scrollable element fails, try re-opening the modal and finding it again
    if scrollable_element is None:
        print(f"[Warning] - Could not find scrollable element on first attempt for {username}. Trying to re-open modal and find again.")
        # Close the modal (by pressing Escape key or clicking outside, Escape is usually more reliable)
        try:
            bot.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(2) # Give time for modal to close
        except Exception as e:
            print(f"[Error] - Could not close modal before re-opening: {e}")

        modal = open_followers_modal(bot, username)
        if modal is None:
            print(f"[Error] - Could not re-open followers modal for {username}. Skipping scraping.")
            return
        scrollable_element = find_scrollable_element(modal)
        if scrollable_element is None:
            print(f"[Error] - Could not find scrollable element after re-opening modal for {username}. Skipping scraping.")
            return


    scroll_modal(bot, modal, scrollable_element)
    followers_info = extract_follower_data(modal)
    save_followers_to_file(followers_info, username)


def scrape():
    # Load or prompt for credentials
    credentials = load_credentials()
    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    usernames = get_usernames()

    # Use ChromeDriverManager to automatically download and manage chromedriver
    try:
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        print(f"[Error] - Could not install or find chromedriver: {e}")
        print("Please ensure you have a compatible Chrome browser installed.")
        return

    # Set up Chrome options
    options = Options()
    # options.add_argument("--headless")  # Uncomment to run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    # Start maximized for better visibility in non-headless mode
    options.add_argument("--start-maximized")

    # You can add a default user agent or make this configurable
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    bot = None
    try:
        bot = webdriver.Chrome(service=service, options=options)
        bot.set_page_load_timeout(60)  # Set a reasonable page load timeout

        # Attempt to load and use cookies
        if not load_cookies(bot, username):
            print("[Info] - Cookie login failed or cookie file not found. Proceeding with username/password login.")
            # If cookie login fails, perform username/password login
            login(bot, username, password)
            # Save cookies after successful username/password login
            save_cookies(bot, username)


        # Scrape each username in the list
        for user in usernames:
            user = user.strip()
            if user:  # Ensure username is not empty
                scrape_followers(bot, user)

    except Exception as e:
        print(f"[Error] - An error occurred during the scraping process: {e}")
    finally:
        if bot:
            bot.quit()
            print("[Info] - Browser closed.")


def get_usernames():
    # Temporarily hardcoding choice to 1 for testing purposes
    # choice = input(
    #     "Select input method:\n"
    #     "1. Read from CSV file (usernamelist.csv)\n"
    #     "2. Input manually\n"
    #     "Enter 1 or 2: "
    # ).strip()

    choice = "1" # Hardcoded to use CSV

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
                "CSV file 'usernamelist.csv' not found. "
                "Please check the file location.")
            return []
        except Exception as e:
            print(f"[Error] - Error reading usernames from CSV: {e}")
            return []
    elif choice == "2":
        usernames = input(
            "Enter the Instagram usernames you want to scrape "
            "(separated by commas): ").split(",")
        usernames = [username.strip()
                     for username in usernames if username.strip()]
        print(f"Usernames entered manually: {usernames}")
        return usernames
    else:
        print("Invalid selection. Please enter either '1' or '2'.")
        return get_usernames()  # Ask again if input is invalid


if __name__ == '__main__':
    scrape()
