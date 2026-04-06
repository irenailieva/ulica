import time
import requests
from playwright.sync_api import sync_playwright

def main():
    print("Starting scraper service...")
    
    # Test requests
    try:
        response = requests.get('https://example.com')
        print(f"Requests test: example.com returned status {response.status_code}")
    except Exception as e:
        print(f"Requests test failed: {e}")

    # Test playwright
    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://example.com')
            title = page.title()
            print(f"Playwright test: page title is '{title}'")
            browser.close()
    except Exception as e:
        print(f"Playwright test failed: {e}")

    print("Scraper initialization complete. Entering idle state to keep container running.")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
