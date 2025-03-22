import csv
import requests
from bs4 import BeautifulSoup


def get_real_name_from_profile(username):
    """
    Given a username, scrape the profile page (hypothetical example),
    parse the HTML to find and return the real name.
    """
    # Construct the user profile URL (adjust to match the actual site).
    url = f"https://www.instagram.com/{username}"
    
    try:
        # Send a GET request to the user's profile page
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an error if request failed
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Hypothetical: real name is in a <span> with class "user-real-name"
        real_name_span = soup.find("span", class_="user-real-name")
        
        if real_name_span:
            return real_name_span.get_text(strip=True)
        else:
            return "Unknown"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching profile for {username}: {e}")
        return "Error"


def process_user_followers_csv(username):
    """
    Opens 'username_followers.csv', reads each row (assuming each row is a single
    username), scrapes real names, and writes out to 'username_followers_realname.csv'.
    """
    input_filename = f"{username}_followers.csv"
    output_filename = f"{username}_followers_realname.csv"
    
    # Read usernames from the input CSV
    try:
        with open(input_filename, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            # If your CSV has a header row and you only need the first column:
            # next(reader, None)  # skip header if needed
            follower_usernames = [row[0] for row in reader if row]
    except FileNotFoundError:
        print(f"File not found: {input_filename}")
        return

    # Write to the output CSV
    with open(output_filename, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["username", "real_name"])  # Header row

        for follower in follower_usernames:
            real_name = get_real_name_from_profile(follower)
            writer.writerow([follower, real_name])
            print(f"{username} follower {follower} => {real_name}")


def main():
    # 1. Define or read a list of usernames
    # For example, let's define them right here.
    # You could also get them from another CSV, user input, etc.
    usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

    # 2. Loop over each username
    for user in usernames:
        print(f"Processing {user}...")
        process_user_followers_csv(user)


if __name__ == "__main__":
    main()
import csv
import requests
from bs4 import BeautifulSoup

def get_instagram_real_name(username):
    """
    Attempt to retrieve the user's 'real name' from the Instagram profile page
    by looking for an element with the specified style attribute.
    
    IMPORTANT: This will likely fail without proper authentication or JavaScript
    rendering, given Instagram's anti-scraping measures.
    """
    url = f"https://www.instagram.com/{username}/"
    # Common practice to include a User-Agent header to appear more like a real browser
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/109.0.0.0 Safari/537.36"
        )
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Search for the exact style attribute 
        # e.g. style="----base-line-clamp-line-height: 18px; --lineHeight: 18px;"
        name_span = soup.find("span", attrs={
            "style": "----base-line-clamp-line-height: 18px; --lineHeight: 18px;"
        })
        if name_span:
            return name_span.get_text(strip=True)
        else:
            return "Name not found"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def process_user_followers_csv(username):
    """
    For a given username, opens `username_followers.csv`, reads each follower's username,
    scrapes the real name from Instagram, and writes out to `username_followers_realname.csv`.
    """
    input_filename = f"{username}_followers.csv"
    output_filename = f"{username}_followers_realname.csv"

    # Read the follower usernames from the input CSV
    try:
        with open(input_filename, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            # If your CSV has a header row, skip it by uncommenting:
            # next(reader, None) 
            follower_usernames = [row[0] for row in reader if row]
    except FileNotFoundError:
        print(f"File not found: {input_filename}")
        return

    # Write results to the output CSV
    with open(output_filename, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["username", "real_name"])  # Header row

        for follower in follower_usernames:
            real_name = get_instagram_real_name(follower)
            writer.writerow([follower, real_name])
            print(f"Processed follower '{follower}' => Real name: {real_name}")

def main():
    """
    1. Define or read a list of Instagram usernames.
    2. For each username, open their `username_followers.csv`.
    3. Scrape real names from Instagram for each follower.
    4. Write to `username_followers_realname.csv`.
    """
    # Example list of top-level Instagram usernames
    usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

    for user in usernames:
        print(f"Processing followers of '{user}'...")
        process_user_followers_csv(user)

if __name__ == "__main__":
    main()
