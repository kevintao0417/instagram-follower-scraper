import csv
import instaloader

# Create an instance of Instaloader
L = instaloader.Instaloader()

# Optional: Log in if you need to access private profiles or reduce rate limiting
# L.login("your_instagram_username", "your_password")

# Ask user for comma-separated Instagram usernames to scrape
usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

# Process each provided username
for target_username in usernames:
    target_username = target_username.strip()  # Clean up any extra whitespace
    input_csv = f"{target_username}_followers.csv"
    output_csv = f"{target_username}_followers_with_names.csv"
    
    print(f"\nProcessing followers for: {target_username}")
    try:
        with open(input_csv, newline='', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            # We'll output two columns: the follower's username and real (display) name
            fieldnames = ['username', 'real_name']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                follower_username = row.get('username')
                if not follower_username:
                    continue  # Skip if there's no username field
                try:
                    # Fetch the profile data using Instaloader
                    profile = instaloader.Profile.from_username(L.context, follower_username)
                    real_name = profile.full_name
                    writer.writerow({'username': follower_username, 'real_name': real_name})
                    print(f"Processed {follower_username}: {real_name}")
                except Exception as e:
                    print(f"Error retrieving data for {follower_username}: {e}")
    except FileNotFoundError:
        print(f"CSV file for {target_username} not found: {input_csv}")
