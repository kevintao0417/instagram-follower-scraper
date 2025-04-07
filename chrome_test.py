from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def hold_example(url):
    chrome_binary = (
        "/Users/kevintao/Develop/ChromeTest/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    )

    # Path to your ChromeDriver executable (make sure this file exists and is executable)
    chromedriver_path = (
        "/Users/kevintao/Develop/ChromeTest/chromedriver-mac-arm64/chromedriver"
    )
    options = Options()
    options.binary_location = chrome_binary
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/134.0.6998.99 Mobile/15E148 Safari/604.1"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")

    service = Service(executable_path=chromedriver_path)
    bot = webdriver.Chrome(service=service, options=options)
    bot.set_page_load_timeout(90)
    bot.get(url)
    # Pause here so the page remains open
    print(f"Page opened: {bot.title}")
    print("Press ENTER to continue...")
    input()  # Wait for user input to proceed

    bot.quit()

if __name__ == "__main__":
    hold_example("https://www.instagram.com/accounts/login")
