# combine_followers.py

try:
    import instaloader_name as instaloader_module
except ImportError as e:
    print("Error importing instaloader_name:", e)
    instaloader_module = None

try:
    import run_scroll as run_kevin_module
except ImportError as e:
    print("Error importing run_kevin:", e)
    run_kevin_module = None

def get_followers(module):
    """Attempt to extract a follower list from the given module.
    It first looks for a callable get_followers() function,
    then for a variable named 'followers'. Returns a list (or empty list).
    """
    if module is None:
        return []
    # Check if there is a function named get_followers
    if hasattr(module, "get_followers") and callable(module.get_followers):
        try:
            return module.get_followers()
        except Exception as e:
            print(f"Error calling get_followers() in module {module.__name__}: {e}")
    # Check for a variable named 'followers'
    if hasattr(module, "followers"):
        try:
            data = getattr(module, "followers")
            # Ensure data is a list or iterable
            if isinstance(data, list):
                return data
            else:
                return list(data)
        except Exception as e:
            print(f"Error retrieving 'followers' from module {module.__name__}: {e}")
    print(f"No follower data found in module {module.__name__}.")
    return []

# Retrieve followers from each module
followers_from_instaloader = get_followers(instaloader_module)
followers_from_run_kevin   = get_followers(run_kevin_module)

# Combine and remove duplicates using a set
combined_followers = set(followers_from_instaloader + followers_from_run_kevin)

print("Combined list of followers:")
for follower in sorted(combined_followers):
    print(follower)
