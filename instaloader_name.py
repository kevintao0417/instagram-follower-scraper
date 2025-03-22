import csv
import time
import instaloader

# Create an instance of Instaloader
L = instaloader.Instaloader()

# Log in to Instagram (replace with your credentials)
L.login("kevintaoooo", "KEVINt4s1k7!")

# Ask user for comma-separated Instagram usernames to scrape
usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

for target_username in usernames:
    target_username = target_username.strip()
    input_csv = f"{target_username}_followers.csv"
    output_csv = f"{target_username}_followers_with_names.csv"
    
    print(f"\nProcessing followers for: {target_username}")
    try:
        with open(input_csv, newline='', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            # Change the output field from 'full_name' to 'real_name'
            fieldnames = ['username', 'real_name']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                follower_username = row.get('username')
                if not follower_username:
                    continue
                
                try:
                    profile = instaloader.Profile.from_username(L.context, follower_username)
                    real_name = profile.full_name  # Using full_name as the real_name
                    writer.writerow({'username': follower_username, 'real_name': real_name})
                    print(f"Processed {follower_username}: {real_name}")
                except Exception as e:
                    print(f"Error retrieving data for {follower_username}: {e}")
                    
                # Delay to reduce the chance of hitting rate limits
                time.sleep(5)
    except FileNotFoundError:
        print(f"CSV file for {target_username} not found: {input_csv}")
